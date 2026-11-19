#!/usr/bin/env python3
"""Read-only upstream drift check for PaperDIY Reader.

Every source and baseline lives in ``scripts/upstreams.json`` so that the
check is deterministic: the same repositories, refs and watched paths on every
run. The script never edits the work tree; remote clones are cached outside the
repository.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).with_name("upstreams.json")
DEFAULT_CACHE = Path(
    os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
) / "paperdiy-reader" / "upstream-check"

MAX_SUBJECTS = 8
MAX_FILES = 15
GIT_ENV = {**os.environ, "LC_ALL": "C"}


@dataclass
class Result:
    id: str
    kind: str
    baseline: str = ""
    current: str = ""
    latest_tag: str = ""
    commits: int = 0
    commit_subjects: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    deleted: int = 0
    modified: int = 0
    renamed: int = 0
    build_changed: bool = False
    new_components: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class DiffStat:
    added: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    modified: int = 0
    renamed: int = 0


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=False,
        env=GIT_ENV,
    )


def git_ok(cwd: Path, *args: str) -> str:
    proc = git(cwd, *args)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout.strip()


def resolve(cwd: Path, ref: str) -> str | None:
    proc = git(cwd, "rev-parse", "--verify", f"{ref}^{{commit}}")
    return proc.stdout.strip() if proc.returncode == 0 else None


def short(cwd: Path, ref: str) -> str:
    proc = git(cwd, "rev-parse", "--short", ref)
    return proc.stdout.strip() if proc.returncode == 0 else ref[:8]


def label(cwd: Path, ref: str) -> str:
    sha = resolve(cwd, ref)
    return f"{ref}@{sha[:8]}" if sha else ref


def diff_stat(cwd: Path, base: str, current: str, paths: list[str]) -> DiffStat:
    args = ["diff", "--name-status", f"{base}..{current}"]
    if paths:
        args += ["--", *paths]
    proc = git(cwd, *args)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git diff failed")

    stat = DiffStat()
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        if status.startswith("R") or status.startswith("C"):
            stat.renamed += 1
            if len(parts) >= 3:
                stat.deleted.append(parts[1])
                stat.added.append(parts[2])
                stat.changed.extend(parts[1:3])
        elif status.startswith("A"):
            stat.added.append(parts[1])
            stat.changed.append(parts[1])
        elif status.startswith("D"):
            stat.deleted.append(parts[1])
            stat.changed.append(parts[1])
        else:
            stat.modified += 1
            stat.changed.append(parts[1])
    return stat


def log_info(
    cwd: Path, base: str, current: str, paths: list[str]
) -> tuple[int, list[str]]:
    count_args = ["rev-list", "--count", f"{base}..{current}"]
    if paths:
        count_args += ["--", *paths]
    count = int(git_ok(cwd, *count_args) or "0")

    log_args = ["log", f"-n{MAX_SUBJECTS}", "--format=%h %s", f"{base}..{current}"]
    if paths:
        log_args += ["--", *paths]
    proc = git(cwd, *log_args)
    subjects = [line for line in proc.stdout.splitlines() if line.strip()]
    return count, subjects


def log_matching(
    cwd: Path,
    base: str,
    current: str,
    paths: list[str],
    pattern: str,
    limit: int = MAX_SUBJECTS,
) -> list[str]:
    args = ["log", "--format=%h %s", f"{base}..{current}"]
    if paths:
        args += ["--", *paths]
    proc = git(cwd, *args)
    if proc.returncode != 0:
        return []
    regex = re.compile(pattern, re.IGNORECASE)
    return [
        line for line in proc.stdout.splitlines() if regex.search(line)
    ][:limit]


def child_dirs(cwd: Path, ref: str, prefix: str) -> set[str]:
    proc = git(cwd, "ls-tree", "-d", "--name-only", ref, "--", prefix)
    if proc.returncode != 0:
        return set()
    return {line.rstrip("/").split("/")[-1] for line in proc.stdout.splitlines() if line.strip()}


def new_component_dirs(
    cwd: Path, base: str, current: str, prefixes: list[str]
) -> list[str]:
    found: list[str] = []
    for prefix in prefixes:
        new = child_dirs(cwd, current, prefix) - child_dirs(cwd, base, prefix)
        found.extend(f"{prefix}{name}" for name in sorted(new))
    return found


def latest_tag(cwd: Path) -> str:
    proc = git(cwd, "tag", "--sort=-version:refname")
    if proc.returncode != 0:
        return ""
    for tag in proc.stdout.splitlines():
        if re.match(r"^v?\d+\.\d+", tag):
            return tag
    return ""


def tree_commit(cwd: Path, ref: str, path: str) -> str | None:
    proc = git(cwd, "ls-tree", ref, "--", path)
    for line in proc.stdout.splitlines():
        meta, _, _ = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "commit":
            return parts[2]
    return None


def ini_value(text: str, section: str, key: str) -> str:
    active = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            active = stripped
        elif active == section and stripped.startswith(f"{key} = "):
            return stripped.split("=", 1)[1].strip()
    return ""


def crosspoint_version(cwd: Path, ref: str, path: str) -> str:
    proc = git(cwd, "show", f"{ref}:{path}")
    if proc.returncode != 0:
        return ""
    return ini_value(proc.stdout, "[crosspoint]", "version")


def ensure_repo(cache: Path, repo_id: str, url: str, no_fetch: bool) -> Path:
    dest = cache / repo_id
    if not (dest / ".git").exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        clone = [
            "git",
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            "--quiet",
            url,
            str(dest),
        ]
        proc = subprocess.run(
            clone, text=True, capture_output=True, check=False, env=GIT_ENV
        )
        if proc.returncode != 0:
            subprocess.run(
                ["git", "clone", "--no-checkout", "--quiet", url, str(dest)],
                check=True,
                env=GIT_ENV,
            )
    if not no_fetch:
        proc = git(dest, "fetch", "--tags", "--prune", "--quiet", "origin")
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "git fetch failed")
    return dest


def check_crosspoint(cfg: dict, no_fetch: bool) -> Result:
    result = Result(id="crosspoint", kind="firmware")
    if git(ROOT, "remote", "get-url", "upstream").returncode != 0:
        raise RuntimeError(
            "no 'upstream' remote; run: git remote add upstream "
            "https://github.com/crosspoint-reader/crosspoint-reader.git"
        )
    if not no_fetch:
        proc = git(ROOT, "fetch", "--prune", "upstream")
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "git fetch upstream failed")

    base_ref = cfg["mirror_ref"]
    current_ref = cfg["upstream_ref"]
    if not resolve(ROOT, base_ref) or not resolve(ROOT, current_ref):
        raise RuntimeError(f"missing ref {base_ref} or {current_ref}")

    result.baseline = label(ROOT, base_ref)
    result.current = label(ROOT, current_ref)
    result.commits, result.commit_subjects = log_info(ROOT, base_ref, current_ref, [])

    stat = diff_stat(ROOT, base_ref, current_ref, [])
    result.added = stat.added
    result.deleted = len(stat.deleted)
    result.modified = stat.modified
    result.renamed = stat.renamed

    build_files = set(cfg.get("build_files", []))
    result.build_changed = any(
        path in build_files
        or path.endswith("library.json")
        or path.startswith("sdkconfig.")
        for path in stat.changed
    )
    result.new_components = new_component_dirs(
        ROOT, base_ref, current_ref, ["lib/", "src/components/"]
    )
    result.new_components.extend(
        path for path in stat.added if path.endswith("/library.json")
    )

    version = crosspoint_version(ROOT, current_ref, cfg["version_file"])
    base_version = crosspoint_version(ROOT, base_ref, cfg["version_file"])
    if version:
        result.notes.append(f"CrossPoint version: {version}")
    if base_version and version and base_version != version:
        result.notes.append(
            f"CrossPoint version changed: {base_version} -> {version}; "
            "release numbering resets"
        )

    if result.commits == 0 and not stat.added and not stat.deleted and not stat.modified:
        result.notes.append("up to date")
    return result


def check_freeink(
    cfg: dict, crosspoint_cfg: dict, cache: Path, no_fetch: bool
) -> Result:
    result = Result(id="freeink-sdk", kind="sdk")
    base_ref = crosspoint_cfg["mirror_ref"]
    current_ref = crosspoint_cfg["upstream_ref"]
    path = cfg["submodule_path"]

    our_pin = tree_commit(ROOT, base_ref, path)
    new_pin = tree_commit(ROOT, current_ref, path)
    if not our_pin or not new_pin:
        raise RuntimeError(f"missing {path} submodule commit in {base_ref} or {current_ref}")

    result.baseline = f"pin {our_pin[:8]}"
    result.current = f"pin {new_pin[:8]}"
    repo = ensure_repo(cache, "freeink-sdk", cfg["repo_url"], no_fetch)
    if not resolve(repo, our_pin) or not resolve(repo, new_pin):
        raise RuntimeError("SDK pin is not present in the FreeInk clone")

    result.commits, result.commit_subjects = log_info(repo, our_pin, new_pin, [])
    stat = diff_stat(repo, our_pin, new_pin, [])
    result.added = stat.added
    result.deleted = len(stat.deleted)
    result.modified = stat.modified
    result.renamed = stat.renamed
    result.build_changed = any(
        path.endswith("library.json") or path.endswith("platformio.sample.ini")
        for path in stat.changed
    )
    result.new_components = new_component_dirs(
        repo, our_pin, new_pin, ["libs/"]
    )
    result.new_components.extend(
        path for path in stat.added if path.endswith("/library.json")
    )

    sdk_main = resolve(repo, "origin/main")
    if sdk_main:
        behind = int(git_ok(repo, "rev-list", "--count", f"{new_pin}..origin/main"))
        if behind:
            result.notes.append(
                f"upstream pin is {behind} commits behind FreeInk main ({sdk_main[:8]})"
            )
        else:
            result.notes.append("upstream pin is at FreeInk main")
        if git(repo, "merge-base", "--is-ancestor", new_pin, "origin/main").returncode != 0:
            result.notes.append("upstream pin is not an ancestor of FreeInk main")
    if our_pin == new_pin:
        result.notes.append("no pin change")
    return result


def check_m5(spec: dict, cache: Path, no_fetch: bool) -> Result:
    result = Result(id=spec["id"], kind=spec["kind"])
    repo = ensure_repo(cache, spec["id"], spec["repo_url"], no_fetch)
    branch_ref = f"origin/{spec['branch']}"
    if not resolve(repo, branch_ref):
        raise RuntimeError(f"missing branch {branch_ref}")

    watch = spec.get("watch", [])
    kind = spec["kind"]

    if kind == "dependency":
        pin_text = (ROOT / spec["pin_file"]).read_text(encoding="utf-8")
        match = re.search(spec["pin_pattern"], pin_text)
        if not match:
            raise RuntimeError(
                f"could not find {spec['id']} pin in {spec['pin_file']}"
            )
        base_ref = match.group(1)
        if not resolve(repo, base_ref):
            raise RuntimeError(f"pinned tag {base_ref} not found in {spec['id']}")
        result.baseline = label(repo, base_ref)
        latest = latest_tag(repo)
        result.latest_tag = latest
        if latest and latest != base_ref:
            result.notes.append(f"latest tag: {latest}")
            ahead = int(git_ok(repo, "rev-list", "--count", f"{base_ref}..{latest}"))
            result.notes.append(f"{ahead} commits from pinned tag to latest tag")
        compare_ref = latest or base_ref
        if resolve(repo, branch_ref) != resolve(repo, compare_ref):
            ahead = int(git_ok(repo, "rev-list", "--count", f"{base_ref}..{branch_ref}"))
            result.notes.append(
                f"branch {spec['branch']} is {ahead} commits ahead of {compare_ref}"
            )
    else:
        base_ref = spec["baseline"]
        if not resolve(repo, base_ref):
            raise RuntimeError(f"missing baseline {base_ref} in {spec['id']}")
        result.baseline = spec.get("baseline_label", base_ref)
        sha = short(repo, base_ref)
        if sha not in result.baseline:
            result.baseline = f"{result.baseline} ({sha})"
        latest = latest_tag(repo)
        result.latest_tag = latest
        if latest and resolve(repo, latest) != resolve(repo, base_ref):
            result.notes.append(f"latest tag: {latest}")

    result.current = label(repo, branch_ref)
    result.commits, result.commit_subjects = log_info(
        repo, base_ref, branch_ref, watch
    )
    if spec.get("highlight_pattern"):
        result.highlights = log_matching(
            repo, base_ref, branch_ref, watch, spec["highlight_pattern"]
        )
    stat = diff_stat(repo, base_ref, branch_ref, watch)
    result.added = stat.added
    result.deleted = len(stat.deleted)
    result.modified = stat.modified
    result.renamed = stat.renamed
    result.build_changed = any(
        path.endswith("library.json") or path.endswith("library.properties")
        for path in stat.changed
    )

    if "src" in watch:
        areas = new_component_dirs(repo, base_ref, branch_ref, ["src/"])
        if areas:
            # These live inside a dependency/reference source; they are not
            # components we extract into the firmware on their own.
            result.notes.append("new upstream code areas: " + ", ".join(areas))
    result.new_components.extend(
        path for path in stat.added if path.endswith("/library.json")
    )

    if result.commits == 0 and resolve(repo, base_ref) != resolve(repo, branch_ref):
        result.notes.append("branch moved, but no changes under watched paths")
    if kind == "reference":
        result.notes.append("reference source; not linked into the firmware")
    elif kind == "hardware":
        result.notes.append("3D/hardware source; informational only")
    return result


def safe(result_id: str, kind: str, fn, *args) -> Result:
    try:
        return fn(*args)
    except Exception as exc:  # Report one source failure without aborting the rest.
        return Result(id=result_id, kind=kind, error=str(exc))


def has_drift(result: Result) -> bool:
    if result.error or result.commits or result.added:
        return True
    # A dependency tag is actionable even if the watched paths did not move.
    # Reference-only releases are reported separately.
    return bool(
        result.kind == "dependency"
        and result.latest_tag
        and result.latest_tag not in result.baseline
    )


def render_markdown(results: list[Result]) -> str:
    lines = [
        f"# Upstream check — {date.today().isoformat()}",
        "",
        "Read-only. Baselines live in `scripts/upstreams.json`.",
        "",
        "| Source | Kind | Baseline | Current | Commits | Added |",
        "|---|---|---|---|---:|---:|",
    ]
    for result in results:
        current = "error" if result.error else result.current
        commits = "-" if result.error else str(result.commits)
        added = "-" if result.error else str(len(result.added))
        lines.append(
            f"| `{result.id}` | {result.kind} | {result.baseline or '?'} | "
            f"{current} | {commits} | {added} |"
        )
    lines.append("")

    for result in results:
        lines += [f"## {result.id}", ""]
        if result.error:
            lines += [f"**ERROR:** {result.error}", ""]
            continue
        lines += [
            f"- Baseline: `{result.baseline}`",
            f"- Current: `{result.current}`",
            f"- Commits in watched paths: {result.commits}",
        ]
        if result.latest_tag:
            lines.append(f"- Latest tag: `{result.latest_tag}`")
        if result.commit_subjects:
            lines.append("- Recent commits:")
            lines += [f"  - `{subject}`" for subject in result.commit_subjects]
        if result.highlights:
            lines.append("- Relevant commits:")
            lines += [f"  - `{subject}`" for subject in result.highlights]
        lines.append(
            f"- Files: +{len(result.added)} added, {result.modified} modified, "
            f"{result.deleted} deleted, {result.renamed} renamed"
        )
        if result.added:
            shown = result.added[:MAX_FILES]
            lines.append("- Added files:")
            lines += [f"  - `{path}`" for path in shown]
            if len(result.added) > len(shown):
                lines.append(f"  - … {len(result.added) - len(shown)} more")
        if result.new_components:
            lines.append("- New component candidates:")
            lines += [f"  - `{path}`" for path in result.new_components]
        else:
            lines.append("- New component candidates: none")
        lines.append(f"- Build/deps changed: {'yes' if result.build_changed else 'no'}")
        if result.notes:
            lines.append("- Notes:")
            lines += [f"  - {note}" for note in result.notes]
        lines.append("")

    components = sorted({path for result in results for path in result.new_components})
    errors = [result.id for result in results if result.error]
    drift = [result.id for result in results if has_drift(result)]
    release_only = [
        result.id
        for result in results
        if not has_drift(result)
        and not result.error
        and result.latest_tag
        and result.latest_tag not in result.baseline
    ]

    lines += ["## Verdict", ""]
    if components:
        lines.append("New component candidates:")
        lines += [f"- `{path}`" for path in components]
    else:
        lines.append("No new component candidates detected.")
    if drift:
        lines += ["", "Sources with drift: " + ", ".join(f"`{name}`" for name in drift)]
    if release_only:
        lines += [
            "",
            "Release-only notices (no watched changes): "
            + ", ".join(f"`{name}`" for name in release_only),
        ]
    if errors:
        lines += ["", "Sources that could not be checked: " + ", ".join(f"`{name}`" for name in errors)]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check CrossPoint, FreeInk and M5 sources for upstream drift."
    )
    parser.add_argument(
        "--json", action="store_true", help="emit the report as JSON"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when any source has drift or a check failed",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="use cached clones and existing refs without fetching",
    )
    parser.add_argument(
        "--cache-dir",
        help=f"clone cache directory (default: {DEFAULT_CACHE})",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="print the cache directory to stderr"
    )
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cache = Path(args.cache_dir).expanduser() if args.cache_dir else DEFAULT_CACHE
    cache.mkdir(parents=True, exist_ok=True)
    if args.verbose:
        print(f"cache: {cache}", file=sys.stderr)

    results = [
        safe("crosspoint", "firmware", check_crosspoint, config["crosspoint"], args.no_fetch),
        safe(
            "freeink-sdk",
            "sdk",
            check_freeink,
            config["freeink_sdk"],
            config["crosspoint"],
            cache,
            args.no_fetch,
        ),
    ]
    for spec in config["m5_sources"]:
        results.append(safe(spec["id"], spec["kind"], check_m5, spec, cache, args.no_fetch))

    if args.json:
        payload = {
            "date": date.today().isoformat(),
            "new_components": sorted(
                {path for result in results for path in result.new_components}
            ),
            "sources": [asdict(result) for result in results],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(results))

    drift = any(has_drift(result) for result in results)
    return 1 if args.strict and drift else 0


if __name__ == "__main__":
    sys.exit(main())
