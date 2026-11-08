## Release Versioning

PaperDIY releases are numbered after the CrossPoint version they are built on,
plus a port revision, so users can tell which upstream release they run:

```
<CrossPoint X.Y.Z>-paperdiy.<N>        e.g. 2.0.0-paperdiy.1
```

- `X.Y.Z` is `[crosspoint] version` on upstream `main` at the synced commit.
  Never invent or bump it on our own.
- `N` is the port revision on that base. It starts at 1 and goes up by one on
  every public release (fixes, features, docs, dependency updates). A sync to
  a new CrossPoint version resets it: `2.1.0-paperdiy.1`.
- Tag: `v` + version (`v2.0.0-paperdiy.1`). `[crosspoint] version` in
  `platformio.ini` and `CROSSPOINT_VERSION` are the same string without the
  `v`.
- RC: `v2.0.0-paperdiy.2-rc.1`; the workflow publishes it as a GitHub
  pre-release so `/releases/latest` skips it. Set `[crosspoint] version` to
  `2.0.0-paperdiy.2-rc.1` while building it. Do not upload RCs to M5Burner.
- Local `paperdiy` builds report the plain `[crosspoint] version`; never
  publish them. The parser treats any `-rc`/`-dev` suffix as a pre-release.
- Never reuse a tag. To rebuild a published release, bump `N`.
- Ordering (`src/network/FirmwareVersion.h`, used by the GitHub OTA and the
  LauncherHub notice): CrossPoint version, then `N`, then an RC/dev build
  before its release. Keep that file, its tests (`test/firmware_version`) and
  `scripts/check_release_version.py` in sync with this rule.
- The upstream commit and SDK pin go in `CHANGELOG.md` and the release notes.
- The OTA asset is `crosspoint-<tag>-paperdiy.bin`
  (`crosspoint-v2.0.0-paperdiy.1-paperdiy.bin`); the trailing `-paperdiy` is
  the board tag the OTA looks for, not part of the version.
- M5Burner and Launcher packages use the same version string as the tag
  without the `v`. Keep the stable Launcher alias
  `PaperDIYReader-launcher.bin` unchanged.
- The release workflow validates the tag and version with
  `scripts/check_release_version.py`. Do not bypass that check.
- Release notes must warn that the reader does not install updates under
  M5Launcher (`Check for Updates` only notifies; install from
  `M5Launcher > OTA`) and link to `docs/paperdiy/13-m5launcher.md`. Publish
  each release on M5Burner as `CrossPoint for PaperDIY (community port)` so
  the notice finds it.
- Every M5Burner version must follow this scheme: the notice picks the
  highest version in the catalog, so one stray `2.1.0` would be offered to
  every `2.0.0-paperdiy.N` unit until CrossPoint reaches 2.1.0.
- History: `v0.1.0` and `v2.1.0` predate this scheme. `v2.1.0` was removed
  from GitHub before `v2.0.0-paperdiy.1` was published. Units still on 2.1.0,
  standalone or under M5Launcher, compare it as newer than `2.0.0-paperdiy.N`
  and must be updated once by hand.
