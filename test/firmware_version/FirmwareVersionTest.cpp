#include <gtest/gtest.h>

#include "FirmwareVersion.h"

using firmware_version::isNewer;
using firmware_version::parse;

TEST(FirmwareVersionTest, ParsesPortVersion) {
  const auto v = parse("v2.0.0-paperdiy.3-rc.2");
  EXPECT_EQ(v.base[0], 2);
  EXPECT_EQ(v.base[1], 0);
  EXPECT_EQ(v.base[2], 0);
  EXPECT_EQ(v.revision, 3);
  EXPECT_EQ(v.preRelease, 2);
}

TEST(FirmwareVersionTest, MissingPartsAreZeroAndFinal) {
  const auto v = parse("2.2");
  EXPECT_EQ(v.base[0], 2);
  EXPECT_EQ(v.base[1], 2);
  EXPECT_EQ(v.base[2], 0);
  EXPECT_EQ(v.revision, 0);
  EXPECT_EQ(v.preRelease, firmware_version::Version::FINAL);
  const auto empty = parse("");
  EXPECT_EQ(empty.base[0], 0);
  EXPECT_FALSE(isNewer("", "0.0.0"));
}

TEST(FirmwareVersionTest, RevisionOrdersWithinSameCrossPointVersion) {
  EXPECT_TRUE(isNewer("2.0.0-paperdiy.2", "2.0.0-paperdiy.1"));
  EXPECT_TRUE(isNewer("2.0.0-paperdiy.10", "2.0.0-paperdiy.9"));
  EXPECT_FALSE(isNewer("2.0.0-paperdiy.1", "2.0.0-paperdiy.1"));
  EXPECT_FALSE(isNewer("2.0.0-paperdiy.1", "2.0.0-paperdiy.2"));
}

TEST(FirmwareVersionTest, CrossPointVersionWinsOverRevision) {
  EXPECT_TRUE(isNewer("2.1.0-paperdiy.1", "2.0.0-paperdiy.9"));
  EXPECT_FALSE(isNewer("2.0.0-paperdiy.9", "2.1.0-paperdiy.1"));
}

TEST(FirmwareVersionTest, LeadingVIsIgnored) {
  EXPECT_FALSE(isNewer("v2.0.0-paperdiy.1", "2.0.0-paperdiy.1"));
  EXPECT_TRUE(isNewer("v2.0.0-paperdiy.2", "2.0.0-paperdiy.1"));
}

TEST(FirmwareVersionTest, ReleaseCandidateSortsBeforeItsRelease) {
  EXPECT_TRUE(isNewer("2.0.0-paperdiy.2", "2.0.0-paperdiy.2-rc.1"));
  EXPECT_TRUE(isNewer("2.0.0-paperdiy.2-rc.2", "2.0.0-paperdiy.2-rc.1"));
  EXPECT_TRUE(isNewer("2.0.0-paperdiy.2-rc.1", "2.0.0-paperdiy.1"));
  EXPECT_FALSE(isNewer("2.0.0-paperdiy.2-rc.1", "2.0.0-paperdiy.2"));
}

TEST(FirmwareVersionTest, DevBuildIsPreRelease) {
  EXPECT_TRUE(isNewer("2.0.0-paperdiy.2", "2.0.0-paperdiy.2-dev.abc123"));
}

TEST(FirmwareVersionTest, PlainSemverStillCompares) {
  EXPECT_TRUE(isNewer("1.0.1", "1.0.0"));
  EXPECT_TRUE(isNewer("2.2.0", "2.2.0-rc"));
  EXPECT_FALSE(isNewer("1.0.0", "1.0.1"));
}
