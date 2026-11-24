#pragma once

// Expat 2.10+ requires an entropy source for its hash-table salt. The
// firmware gets it from the ESP32 hardware RNG (see esp_random_shim.c);
// host unit tests use the weak fallback, which is fine for test fixtures.
#if defined(ESP_PLATFORM)
#define HAVE_GETRANDOM 1
#else
#define XML_POOR_ENTROPY 1
#endif
