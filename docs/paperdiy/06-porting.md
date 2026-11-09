# 06 — Notas del port y validación

**Idiomas:** **Español** · [English](06-porting.en.md) · [简体中文](06-porting.zh-CN.md) · [日本語](06-porting.ja.md)

## Cambios respecto a CrossPoint 2.0

Commit base: `f8db833f16dc7adca81359eee74c6366a49bc0ce` (develop, 2.0.0,
2026-11-09). `main` es el espejo de upstream; `paperdiy` es el fork. El SDK
`freeink-sdk` está vendorizado para que el build sea autocontenido. El port se
mantiene en `patches/sdk.patch` + `patches/firmware.patch`.

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
- `FREEINK_FB_PSRAM` incluye PaperDIY (framebuffer en PSRAM).

### `freeink-sdk/libs/hardware/BoardConfig/include/M5Pm1.h`

- SDA/SCL = 41/42 para PaperDIY.
- `GPIO2` (rail EPD), `GPIO3` (CHG_STAT) y `REG_GPIO_IN`.

### `freeink-sdk/libs/display/FreeInkDisplay/src/driver/LgfxEpdDriver.cpp`

- Rama `FREEINK_DEVICE_PAPERDIY` que usa `paperdiyLgfxConfig()`.

### `freeink-sdk/libs/hardware/BatteryMonitor/src/BatteryMonitor.cpp`

- `hasM5Pm1Backend()` incluye `isPaperDiy()`; lee VBAT/VIN/VOUT, PWR_SRC y
  CHG_STAT (PM1 GPIO3) para el estado de carga.

### `freeink-sdk/libs/hardware/PowerManager/src/PowerManager.cpp`

- `armPowerButtonWakeup()`: PaperDIY arma `ext1` en GPIO3/4.
- `waitForPowerButtonRelease()`: espera a que A y B se suelten.
- `powerDownRailsForSleep()`: baja PM1 GPIO2 tras el sleep del panel.

### `freeink-sdk/libs/hardware/InputManager/src/InputManager.cpp`

- `BoardPaperDiy::ensureBooted()` al iniciar.
- `pollPowerButtonClicked()` se convierte en `BTN_POWER`; el botón físico del
  PM1 ya es usable por la UI.

### `src/network/FirmwareBoardTag.cpp`

- Tag `paperdiy` para OTA/telemetría de build.

### `lib/hal/HalGPIO.cpp`

- `coldBootImpliesPowerButton()` incluye PaperDIY.

### `lib/hal/HalPowerManager.cpp`

- En batería pide shutdown al PM1 (`SYS_CMD 0xA1`); si USB mantiene la placa,
  hace deep sleep con wake por A/B.

### `src/main.cpp`

- PaperDIY entra en el path `AfterUSBPower` (no dormir en bucle con USB).
- El clic del PM1 con acción `Sleep`/`Ignore` entra en `enterDeepSleep()`.

### `src/network/OtaUpdater.cpp`

- `CROSSPOINT_OTA_RELEASES_URL` configurable; tags con prefijo `v` aceptados.
- El env `paperdiy` fija las releases de este repo y el nombre del asset
  (`CROSSPOINT_OTA_ASSET_FORMAT`, `crosspoint-paperdiy-<versión>-ota.bin`).

### `platformio.ini`

- Env `paperdiy`:
  - `esp32-s3-devkitc1-n16r8`, `qio_opi`.
  - `FREEINK_DEVICE_PAPERDIY=1`, `BOARD_HAS_PSRAM`.
  - `FREEINK_CAP_USB_MSC=1`, `FREEINK_CAP_BLE_HID_HOST=1`.
  - `BoardPaperDiy` + `M5GFX`.

### Nuevo `freeink-sdk/libs/hardware/BoardPaperDiy/`

- `BoardPaperDiyPins.h`
- `BoardPaperDiy.h/.cpp`:
  - `ensureBooted()`: PM1, CHG/DCDC, GPIO2/3, botón power;
  - `setEpdPower()` / `prepareEpdPower()` / `powerDownEpdPower()`;
  - `pollPowerButtonClicked()`;
  - `powerOff()`.
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
RAM:   33.9% (110.924 / 327.680 bytes)
Flash: 82.7% (5.422.079 / 6.553.600 bytes)
firmware.bin          5,2 MB
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

2. Entrar en download mode: mantener power ~10 s hasta que el LED rojo
   parpadee; la pantalla puede quedarse congelada.

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

## Primera validación en hardware (28/10/2026)

- Flash de `firmware.factory.bin` en `0x0` por USB; hash verificado.
- Arranque correcto: logs con ~129 KB de heap libre y ~6,3 MB de PSRAM libre.
- La UI se ve **correcta en vertical**; home con “No open book”, Browse Files,
  Library, File Transfer y Settings. Batería al 100 %.
- A/B responden. Los clics cortos se registran **al soltar** (comportamiento
  de `DigitalTwoButton`, necesario para distinguir el clic de la pulsación
  larga). Pendiente decidir si se cambia a “page on press”.
- SD de 8 GB FAT32 monta tras reiniciar; `Books/Amar-o-depender.epub` y
  `Books/Reconciliacion.epub` aparecen en Browse Files. El EPUB abre, pagina y
  se lee correctamente.
- Wi-Fi y web UI funcionan; se han subido libros por la interfaz web y se han
  abierto desde el lector.
- Validado después: OPDS, Calibre wireless, OTA, power/shutdown y wake por
  power. Pendiente entonces: KOReader Sync con credenciales, ghosting general,
  consumo en sleep, deep sleep con wake A/B y autonomía.

Actualización (04/11/2026): tras sincronizar con upstream `308cd522`, se
validaron de nuevo arranque, Home, wake, navegación A/B, batería y SD.

Actualización (05/11/2026): OPDS con Project Gutenberg (navegación, descarga
y lectura), cambio de tamaño de fuente y 96 cambios de página sin fugas de
memoria. A+B con USB en el equipo de prueba apagó vía PM1 y A no despertó;
power encendió conservando la página. La revisión visual tras 24 páginas no
mostró ghosting apreciable; el contador pasó de 1/35 a 1/50 al completarse la
construcción de la sección (conteo parcial mientras indexa). Auto-suspensión a
1 min con `Fondo = Portada` y `Modo = Ajustar`: mostró la portada y power
despertó conservando la página.

Actualización (06/11/2026): lectura larga automatizada por USB con 250+ cambios
de página (spines 10→24, varios capítulos) sin reinicios ni fugas. Heap libre
120,6–120,8 KB y PSRAM ~6,36 MB; mínimo transitorio de heap 81,7 KB. Tiempos
de página completa: `fast` 569–620 ms de display (total 651–726 ms) y `text`
limpio 1538–1542 ms (total 1637–1651 ms); prewarm 38–58 ms y render B/W
49–59 ms. `quality` no lo usa el port; con un mapeo temporal `Half→quality`
midió 1538 ms, igual que `text`, y se restauró el código. La inyección
`CMD:KEY` no renueva la actividad: a los 10 min se auto-suspendió y el USB
desapareció; power despertó conservando la página. Para pruebas largas hay que
poner `Auto suspensión = Nunca` o renovar la actividad. La revisión visual
física del ghosting tras esa lectura sigue pendiente.

![Primer arranque](images/first-boot.png)

![Primera lectura](images/first-read.png)

### Ghosting al abrir el menú del lector

Primer hallazgo de uso real: al pasar de una página al menú del lector quedaba
una sombra tenue del texto anterior. La causa era que `UiListActivity::render()`
pintaba el menú completo con `FAST_REFRESH`.

Solución: `EpubReaderMenuActivity` marca `cleanFirstRender`; la primera pintada
del menú usa `HALF_REFRESH` (banco limpio) y las siguientes vuelven a
`FAST_REFRESH`. Verificado en hardware: el menú queda limpio y la navegación
dentro de él sigue siendo rápida. El primer pintado puede parpadear algo más,
es esperado.

Si al **cerrar** el menú aparece sombra del menú sobre la página, aplicar el
mismo tratamiento al re-render del lector.

### Ghosting al pasar páginas

El panel ED047TC1 en modo paralelo crudo acumula ghosting más rápido que los
controladores SPI para los que se calibró CrossPoint. Con antialiasing de
texto cada página envía **dos** waveforms (base B/W + plano de grises), así
que el intervalo por defecto de 15 páginas equivalía a ~30 pasadas rápidas
antes del limpiado.

Primer intento (31/10/2026): activar `cleanBankNeedsFreshBackground` con una
LUT no-drive en `lutFastest`. En hardware no redujo el ghosting y añadía
refrescos completos visibles, así que se revirtió.

Estado actual (prueba): `lutFast`/`lutFastest` usan la waveform AA de ED047TC1
del LilyGo T5 S3 (mismo panel). Mantiene la base B/W y el plano de grises en
el mismo offset de LUT, evita el flash negro de `lut_fast` y empuja de forma
específica los niveles grises que produce el antialiasing. El intervalo por
defecto pasa a **5 páginas** y una migración única mueve a 5 el 1 heredado de
la prueba anterior; después se respeta lo que elija el lector en
`Settings > Display > Refresh Frequency`.

Pendiente de validar en lectura prolongada. Si esta LUT no mejora el
ghosting, las siguientes opciones son una waveform `text` propia o un
refresco `epd_quality` periódico.

### Batería, carga y PM1

El M5PM1 no tiene coulomb counter: solo expone `VBAT` en mV. La carga la hace
un LGS4056H con `R11=2K`, es decir, 500 mA. En la celda original de 140 mAh eso
es ~3,6C; con una 604050 de ~2000 mAh queda en ~0,25C, mucho más razonable.

Medición en hardware con la celda original y USB conectado:

```
VBAT=4110 mV  VIN=5082 mV  PWR_SRC=5  CHG_STAT=alto  PWR_CFG=0x03
```

El cargador ya había terminado y la celda quedaba en ~4,10 V, no en 4,20 V.
La curva genérica de `BatteryMonitor` asumía 4,20 V y mostraba 90 %. Se añadió
`PAPERDIY_LIION_NOTCH_MV` con el mismo tramo inferior y **4,10 V = 100 %**.
Si se cambia a una celda que cargue hasta 4,20 V, hay que recalibrar el ancla
superior o volver a la curva genérica.

También se integran del ecosistema M5Stack:

- `M5PM1::setBatteryLvp()`: umbral de protección a 3,4 V (`REG_BATT_LVP`).
- `CHG_STAT` (PM1 GPIO3, activo bajo) para el icono de carga real.
- Muestreo de `VBAT`/`VIN` en `About` y log de arranque.
- Referencias: `m5stack/M5PM1`, `m5stack/M5PaperDIY-UserDemo` y
  `m5stack/uiflow-micropython` (driver `m5pm1.py`).

### Refresco parcial

El panel se puede actualizar por regiones sin repintar la pantalla completa:

- `GfxRenderer::displayWindow(x, y, w, h)` recibe coordenadas lógicas, las
  rota a memoria de panel, alinea x a 8 píxeles y llama a
  `HalDisplay::displayWindow`.
- `LgfxEpdDriver::displayWindow()` rellena el canvas de 8 bits desde el
  framebuffer y hace `pushImage(x, y, w, h)` sobre `Panel_EPD`; LovyanGFX
  refresca solo el `_range_mod` escrito.
- `OptionPopup` usa el camino parcial para el diálogo y la tira de botones
  (que se dibuja siempre en Portrait). Está activo en Settings, File Browser,
  Library y el menú del lector; las actividades que limpian la pantalla
  (`ConfirmationActivity`, `ClearCacheActivity`) siguen usando refresco
  completo.
- Pendiente: barra de estado/batería y un límite de parciales antes de un
  `epd_quality` completo, como hace el UserDemo de M5Stack.

### Detección de tarjeta SD

PaperDIY expone `CARD_DET` en GPIO48, activo bajo. `SdPins.detect` lo lleva al
`SDCardManager`:

- `isCardPresent()` lee el pin con pull-up.
- `begin()` no intenta montar si no hay tarjeta.
- Al arrancar sin tarjeta, `main` muestra “Insert SD card” y espera; al
  insertarla se reinicia para montar.
- En caliente, el bucle principal consulta el pin cada 500 ms; al insertar
  llama a `Storage.remount()`. Al quitarla no se desmonta a la fuerza para no
  invalidar archivos abiertos; el siguiente insert re-proba la tarjeta.
- Verificado (04/11/2026): al quitarla leyendo se muestra “Insert SD card”; al
  reinsertar, el equipo reinicia, monta la tarjeta y vuelve a Home.

## Checklist de validación en hardware

Marca cada punto y anota el resultado; es la información que falta para
considerar el port "estable".

| # | Prueba | Esperado | Resultado |
|---|---|---|---|
| 1 | Arranque | splash/UI en pantalla | OK (28/10) |
| 2 | Rotación | UI en horizontal, no invertida | Vertical OK (28/10); horizontal validado (04/11) |
| 3 | Texto | página EPUB legible, sin ghosting grave | OK (28/10); sin ghosting apreciable tras 24 páginas (05/11); 250+ páginas sin errores, falta revisión visual física (06/11) |
| 4 | Refresco quality/text/fast/fastest | tiempos y calidad aceptables | `fast` 569–620 ms, `text` 1538–1542 ms; `quality` ≈1538 ms con mapeo temporal; `fastest` no se usa (06/11) |
| 5 | A/B cortos | mover selección / página | OK (28/10) |
| 6 | A/B largos | back / confirm | Back/confirm por inyección (05/11); falta hold físico |
| 7 | A+B | evento power / dormir | Apaga vía PM1 con USB (05/11) |
| 8 | Batería | % y mV coherentes; carga detectada | OK (31/10) |
| 9 | SD | monta, lista libros, caché | OK (04/11) |
| 10 | EPUB grande | abre y pagina sin OOM | 7,3 MB OK (04/11) |
| 11 | Fuente TTF en SD | se puede seleccionar | N/T |
| 12 | Diccionario | indexa y busca | N/T |
| 13 | Wi-Fi | scan/join; web UI | OK (28/10) |
| 14 | OPDS/Calibre | descarga un libro | OPDS Gutenberg y Calibre OK (04–05/11) |
| 15 | Deep sleep | duerme y despierta con A/B | A+B con USB apagó vía PM1; A no despertó (05/11) |
| 16 | Consumo sleep | < 0,5 mA idealmente | Pendiente |
| 17 | Wake | no hace page turn accidental | Power despierta y conserva página; auto-sleep 1 min con portada OK; A no despierta tras A+B (05/11) |
| 18 | OTA | actualiza sin brick | OK (04/11) |
| 19 | Recuperación | download mode + factory bin | OK (04/11) |
| 20 | Autonomía | horas de lectura reales | Pendiente |
| 21 | Power PM1 corto | entrega `BTN_POWER` y duerme/apaga | OK (04/11) |
| 22 | Shutdown en batería | el PM1 corta y un clic enciende | OK (04/11) |
| 23 | Fallback USB | con USB, deep sleep y wake A/B | No aplica: PM1 apagó con USB (05/11) |
| 24 | OTA fork | no instala firmware oficial; URL propia si se publica | No instala firmware oficial (04/11) |

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Rotación incorrecta | probar `rotation=0` y `2` en `paperdiyLgfxConfig` |
| Ghosting | probar `cleanBankNeedsFreshBackground`, LUTs de LilyGo/PaperS3, refresco completo periódico |
| Panel no enciende | verificar `ensureBooted()`, PM1 GPIO2, GPIO46, CHG/DCDC_EN |
| Consumo alto en sleep | cortar PM1 GPIO2, SD power, holds; medir |
| Batería mal leída | verificar registros PM1 0x20–0x27 y `PWR_SRC` 0x04 |
| Wake accidental | `waitForPowerButtonRelease` + guardar el primer release |
| UI injugable con 2 botones | remapeo, atajos, BLE page turner, revisar diálogos |
| Flash lleno | build `slim`, optimizar fuentes/idiomas, ampliar app0 o reducir spiffs |
| CrossPoint 2.0 cambia | fijar commit, mantener patch, tests de build |
| El power deja de resetear | `PAPERDIY_PM1_APP_POWER_BUTTON=0` restaura el reset de fábrica |

## Upstream

El soporte se puede proponer a CrossPoint:

1. Los cambios de `freeink-sdk` van al submódulo/SDK.
2. Los cambios de `platformio.ini`, `FirmwareBoardTag.cpp` y la doc van al repo
   principal.
3. El perfil PaperDIY es pequeño y encaja con la arquitectura existente; es un
   buen candidato a PR.

El port está separado en `patches/sdk.patch` (base SDK `ac146e4`) y
`patches/firmware.patch` (base CrossPoint `f8db833f`). La generación y el
proceso de sync están en
[`10-fork-maintenance.md`](10-fork-maintenance.md).

## Estado

- [x] Perfil de placa.
- [x] Driver de panel.
- [x] PM1 (rail, batería, CHG_STAT, shutdown).
- [x] Botón power del PM1 como `BTN_POWER`.
- [x] Wake por botones; shutdown en batería y fallback USB.
- [x] Build reproducible y fork `main`/`paperdiy`.
- [x] OTA configurable y tag `paperdiy`.
- [x] Validación básica en hardware (04/11/2026).
- [x] OPDS, Calibre wireless y OTA (04–05/11/2026).
- [x] KOReader Sync con credenciales (servidor KOSync local, 06/11/2026).
- [ ] Ajuste de rotación/LUT/ghosting.
- [ ] Medición de consumo/autonomía.
- [ ] UX de 2 botones pulida.
- [ ] Release.
