// Expat 2.10+ asks the platform for entropy to salt its hash table. ESP-IDF
// does not expose POSIX getrandom(), so provide the one function the parser
// calls and back it with the ESP32 hardware RNG.
#include "random_getrandom.h"

#include <esp_random.h>

bool writeRandomBytes_getrandom_nonblock(void *target, size_t count) {
  esp_fill_random(target, count);
  return true;
}
