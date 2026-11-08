#pragma once

// PaperDIY release versions: <CrossPoint X.Y.Z>-paperdiy.<N>[-rc.<M>], with an
// optional leading "v" on tags (see .agents/rules/release-versioning.md).
// Ordering: CrossPoint version, then the port revision N, then a release
// candidate before its final release. A missing segment or revision is 0, and
// any "-rc"/"-dev" suffix counts as a pre-release of that version.
namespace firmware_version {

struct Version {
  int base[3] = {0, 0, 0};
  int revision = 0;
  // Pre-release order: rc.M sorts as M; a final release sorts above any rc.
  int preRelease = FINAL;

  static constexpr int FINAL = 0x7fffffff;
};

Version parse(const char* text);

// True when `a` is a later release than `b`.
bool isNewer(const Version& a, const Version& b);

inline bool isNewer(const char* a, const char* b) { return isNewer(parse(a), parse(b)); }

}  // namespace firmware_version
