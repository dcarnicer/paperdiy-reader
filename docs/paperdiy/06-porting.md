# 06 — Notas del port y validación

## Cambios respecto a CrossPoint 2.0

Commit base: `31dc683f9ad54d85a35a1eeb698470bb6da69224` (develop, 2.0.0,
2026-10-28). El snapshot está vendorizado en este repo.

### `freeink-sdk/libs/hardware/BoardConfig/include/BoardConfig.h`

- Nuevo flag `FREEINK_DEVICE_PAPERDIY` (0/1).
- Nuevo `Board::M5PaperDiy`.
- Nuevo perfil `M5PAPER_DIY`:
  - 960×540, `LgfxEpd`, `DigitalTwoButton`.
  - SD SPI 39/40/38/47.
  - `up=GPIO4` (A), `down=GPIO3` (B).
  - sin táctil/RTC/IMU/audio/frontlight; batería por PM1.
- `FREEINK_DRIVER_LGFX_EPD` incluye PaperDIY.
- `DEFAULT_DEVICE`, `selectDevice()` y `isPaperDiy()`.
- `MAX_FRAMEBUFFER_BYTES` incluye el panel de PaperDIY.

### `freeink-sdk/libs/hardware/BoardConfig/include/M5Pm1.h`

- SDA/SCL = 41/42 para PaperDIY.
- `GPIO2` como constante (rail EPD).

### `freeink-sdk/libs/display/FreeInkDisplay/src/driver/LgfxEpdDriver.cpp`

- Rama `FREEINK_DEVICE_PAPERDIY` que usa `paperdiyLgfxConfig()`.

### `freeink-sdk/libs/hardware/BatteryMonitor/src/BatteryMonitor.cpp`

- `hasM5Pm1Backend()` incluye `isPaperDiy()`; lee VBAT/VIN/VOUT y PWR_SRC.

### `freeink-sdk/libs/hardware/PowerManager/src/PowerManager.cpp`

- `armPowerButtonWakeup()`: PaperDIY arma `ext1` en GPIO3/4.
- `waitForPowerButtonRelease()`: espera a que A y B se suelten.
- `powerDownRailsForSleep()`: baja PM1 GPIO2 tras el sleep del panel.

### `src/network/FirmwareBoardTag.cpp`

- Tag `paperdiy` para OTA/telemetría de build.

### `platformio.ini`

- Env `paperdiy`:
  - `esp32-s3-devkitc1-n16r8`, `qio_opi`.
  - `FREEINK_DEVICE_PAPERDIY=1`, `BOARD_HAS_PSRAM`.
  - `FREEINK_CAP_USB_MSC=1`, `FREEINK_CAP_BLE_HID_HOST=1`.
  - `BoardPaperDiy` + `M5GFX`.

### Nuevo `freeink-sdk/libs/hardware/BoardPaperDiy/`

- `BoardPaperDiyPins.h`
- `BoardPaperDiy.h/.cpp` (`prepareEpdPower`, `powerDownEpdPower`, `powerOff`)
- `PaperDiyLgfxConfig.cpp`
- `library.json`

## Build

```bash
make build
# o:
PLATFORMIO_CORE_DIR="$PWD/.platformio-core" pio run -e paperdiy
```

Resultado en la máquina de desarrollo (macOS, PlatformIO 6.1.19, pioarduino
55.03.311, Arduino-ESP32 3.3.11):

```
RAM:   33.9% (111.068 / 327.680 bytes)
Flash: 81.6% (5.347.523 / 6.553.600 bytes)
firmware.bin          5,1 MB
firmware.factory.bin  5,2 MB
```

### Problema de entorno encontrado

El `~/.platformio` global tenía un `framework-arduinoespressif32` viejo
(3.20017) mezclado con el framework 3.3.11 que pide pioarduino. Eso producía
errores como `Client.h: No such file`, `pins_arduino.h` o un `FRAMEWORK_DIR`
apuntando a un directorio `@src-...` inexistente. La solución reproducible es
usar un **core de PlatformIO aislado**:

```bash
PLATFORMIO_CORE_DIR="$PWD/.platformio-core" pio run -e paperdiy
```

El `Makefile` ya lo hace. `.platformio-core` está en `.gitignore`; se puede
borrar y se reconstruye solo (descarga ~5 GB la primera vez).

## Flash

### Primera instalación

1. Backup del firmware original:

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  read_flash 0 0x1000000 paperdiy-original.bin
```

2. Entrar en download mode: mantener power ~2 s hasta que el LED rojo
   parpadee.

3. Imagen completa:

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x0 .pio/build/paperdiy/firmware.factory.bin
```

### Actualización de la app

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x10000 .pio/build/paperdiy/firmware.bin
```

o `make flash PORT=/dev/cu.usbmodemXXXX`.

## Checklist de validación en hardware

Marca cada punto y anota el resultado; es la información que falta para
considerar el port "estable".

| # | Prueba | Esperado | Resultado |
|---|---|---|---|
| 1 | Arranque | splash/UI en pantalla | |
| 2 | Rotación | UI en horizontal, no invertida | |
| 3 | Texto | página EPUB legible, sin ghosting grave | |
| 4 | Refresco quality/text/fast/fastest | tiempos y calidad aceptables | |
| 5 | A/B cortos | mover selección / página | |
| 6 | A/B largos | back / confirm | |
| 7 | A+B | evento power / dormir | |
| 8 | Batería | % y mV coherentes; carga detectada | |
| 9 | SD | monta, lista libros, caché | |
| 10 | EPUB grande | abre y pagina sin OOM | |
| 11 | Fuente TTF en SD | se puede seleccionar | |
| 12 | Diccionario | indexa y busca | |
| 13 | Wi-Fi | scan/join; web UI | |
| 14 | OPDS/Calibre | descarga un libro | |
| 15 | Deep sleep | duerme y despierta con A/B | |
| 16 | Consumo sleep | < 0,5 mA idealmente | |
| 17 | Wake | no hace page turn accidental | |
| 18 | OTA | actualiza sin brick | |
| 19 | Recuperación | download mode + factory bin | |
| 20 | Autonomía | horas de lectura reales | |

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Rotación incorrecta | probar `rotation=0` y `2` en `paperdiyLgfxConfig` |
| Ghosting | probar `cleanBankNeedsFreshBackground`, LUTs de LilyGo/PaperS3, refresco completo periódico |
| Panel no enciende | verificar PM1 GPIO2, GPIO46, `applyBootPowerPolicy`, DCDC_EN |
| Consumo alto en sleep | cortar PM1 GPIO2, SD power, holds; medir |
| Batería mal leída | verificar registros PM1 0x20–0x27 y `PWR_SRC` 0x04 |
| Wake accidental | `waitForPowerButtonRelease` + guardar el primer release |
| UI injugable con 2 botones | remapeo, atajos, BLE page turner, revisar diálogos |
| Flash lleno | build `slim`, optimizar fuentes/idiomas, ampliar app0 o reducir spiffs |
| CrossPoint 2.0 cambia | fijar commit, mantener patch, tests de build |

## Upstream

El soporte se puede proponer a CrossPoint:

1. Los cambios de `freeink-sdk` van al submódulo/SDK.
2. Los cambios de `platformio.ini`, `FirmwareBoardTag.cpp` y la doc van al repo
   principal.
3. El perfil PaperDIY es pequeño y encaja con la arquitectura existente; es un
   buen candidato a PR.

Para generar el patch del port:

```bash
git diff a54770e -- \
  freeink-sdk/libs/hardware/BoardConfig \
  freeink-sdk/libs/hardware/BatteryMonitor \
  freeink-sdk/libs/hardware/PowerManager \
  freeink-sdk/libs/hardware/BoardPaperDiy \
  freeink-sdk/libs/display/FreeInkDisplay/src/driver/LgfxEpdDriver.cpp \
  platformio.ini src/network/FirmwareBoardTag.cpp > patches/paperdiy-support.patch
```

(`a54770e` es el commit de importación de upstream en este repo; los archivos
nuevos deben estar añadidos con `git add -N` para que aparezcan en el diff.)

## Estado

- [x] Perfil de placa.
- [x] Driver de panel.
- [x] PM1 (rail, batería, shutdown).
- [x] Wake por botones.
- [x] Build reproducible.
- [ ] Validación en hardware.
- [ ] Ajuste de rotación/LUT/ghosting.
- [ ] Medición de consumo/autonomía.
- [ ] UX de 2 botones pulida.
- [ ] Release.
