## Release Versioning

Public PaperDIY releases use clean semver. Never add a fork suffix or a
free-form revision to the version.

- Tag: `vMAJOR.MINOR.PATCH` (for example `v2.1.0`). `[crosspoint] version` in
  `platformio.ini` and `CROSSPOINT_VERSION` are the same string without the
  leading `v` (`2.1.0`). Do not write `2.1.0-paperdiy` or `2.1.0.1`.
- `MAJOR`: incompatible changes (partitions, settings migration, etc.).
- `MINOR`: new features or an upstream sync that brings features.
- `PATCH`: fixes, dependency updates, or documentation only.
- RC: `v2.2.0-rc.1`; publish it as a GitHub pre-release so it is not returned
  by `/releases/latest`. Set `[crosspoint] version` to `2.2.0-rc.1` while
  building it.
- Internal builds: `2.2.0-dev.<sha>`, never tagged or published.
- Never reuse a tag. To rebuild a published release, bump PATCH.
- The upstream commit and SDK pin go in `CHANGELOG.md` and the release notes,
  not in the version.
- `-paperdiy` is only the OTA board suffix in the asset name:
  `crosspoint-v2.1.0-paperdiy.bin`. The OTA parser matches the tag, not the
  firmware suffix.
- M5Burner and Launcher packages use the same public version. Keep the stable
  Launcher alias `PaperDIYReader-launcher.bin` unchanged.
- The release workflow validates the tag and version with
  `scripts/check_release_version.py`. Do not bypass that check.
- Release notes must warn that the reader does not install updates under
  M5Launcher (`Check for Updates` only notifies; install from
  `M5Launcher > OTA`) and link to `docs/paperdiy/13-m5launcher.md`. Publish
  each release on M5Burner as `CrossPoint for PaperDIY (community port)` so
  the notice finds it.
