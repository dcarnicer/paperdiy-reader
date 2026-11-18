#pragma once

#include <cstdint>

// bmorcelli/Launcher ("M5Launcher") keeps its resident firmware in an
// ESP_PARTITION_SUBTYPE_APP_TEST slot and boots installed apps from a dynamic
// OTA partition. That marker lets an app detect the launcher and avoid
// touching the boot selection or another installed app's OTA slot.
namespace launcher_env {

// Launcher's boot settings, read from its "launcher" NVS namespace. Launcher's
// bootloader reads the same keys to choose between its own UI and the app:
//   - keyGpio > 0: only that GPIO held at keyLevel starts Launcher, on any
//     reset (power-on, deep-sleep wake, software restart).
//   - otherwise:   power-on always starts Launcher; a deep-sleep wake does too
//     unless ddlb is set; a software restart never does.
struct BootConfig {
  bool ddlb = false;      // CFG > DeepSleep starts Launcher, inverted
  int32_t keyGpio = -1;   // CFG > GPIO on boot starts Launcher; -1 = off
  bool keyLevel = false;  // level that counts as "held"
  // The bootloader skips GPIO 0 (a boot strap) as well as -1.
  bool hasKey() const { return keyGpio > 0; }
};

// True when the partition table contains Launcher's resident APP_TEST slot.
bool isUnderLauncher();

// Launcher's boot settings, read once per boot. Defaults (no key, DDLB off)
// when the namespace or a key is missing, matching the bootloader.
const BootConfig& bootConfig();

// One log line with the detected Launcher boot settings; no-op otherwise.
void logStatus();

// Restart into Launcher's resident firmware when no key is configured: a
// deep-sleep wake while DDLB is off, otherwise a power-on reset through the
// M5PM1 (PaperDIY, Paper Mono). Returns false without restarting when a key is
// configured (the caller must restart with the key held), when not under
// Launcher, or when no restart path is available.
bool exitToLauncher();

// Software restart for the key mode. The bootloader starts Launcher only if
// the configured key is held while it samples the pin.
[[noreturn]] void restartWithKeyHeld();

}  // namespace launcher_env
