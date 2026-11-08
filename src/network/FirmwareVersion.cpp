#include "FirmwareVersion.h"

#include <cstdlib>
#include <cstring>

namespace firmware_version {
namespace {

// Reads a non-negative decimal at `p`; returns 0 when there is none.
int readNumber(const char* p) {
  if (p == nullptr || *p < '0' || *p > '9') return 0;
  return static_cast<int>(std::strtol(p, nullptr, 10));
}

}  // namespace

Version parse(const char* text) {
  Version v;
  if (text == nullptr) return v;
  const char* p = text;
  if (*p == 'v' || *p == 'V') ++p;

  for (int i = 0; i < 3; ++i) {
    if (*p < '0' || *p > '9') break;
    char* end = nullptr;
    v.base[i] = static_cast<int>(std::strtol(p, &end, 10));
    p = end;
    if (*p != '.') break;
    ++p;
  }

  const char* revision = std::strstr(text, "-paperdiy.");
  if (revision != nullptr) v.revision = readNumber(revision + std::strlen("-paperdiy."));

  const char* rc = std::strstr(text, "-rc");
  if (rc != nullptr) {
    v.preRelease = rc[3] == '.' ? readNumber(rc + 4) : 0;
  } else if (std::strstr(text, "-dev") != nullptr) {
    v.preRelease = 0;
  }
  return v;
}

bool isNewer(const Version& a, const Version& b) {
  for (int i = 0; i < 3; ++i) {
    if (a.base[i] != b.base[i]) return a.base[i] > b.base[i];
  }
  if (a.revision != b.revision) return a.revision > b.revision;
  return a.preRelease > b.preRelease;
}

}  // namespace firmware_version
