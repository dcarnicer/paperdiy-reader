# 04 — Arquitectura

## Vista general

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CrossPoint 2.0 (src/)                        │
│  Activities / UI  ·  EpubReaderActivity  ·  Library  ·  Settings     │
│  Web UI / OPDS / Calibre / KOReader Sync / OTA                       │
└───────────────▲─────────────────────────────────────────────────────┘
                │ páginas, eventos, ajustes
┌───────────────┴─────────────────────────────────────────────────────┐
│                         lib/ (motor y HAL)                           │
│  Epub/Section/ParsedText → Page → GfxRenderer → framebuffer 1bpp     │
│  EpdFont (bitmap + TTF/FreeType)  ·  HalStorage/SdFat  ·  HalGPIO    │
└───────────────▲─────────────────────────────────────────────────────┘
                │ BoardConfig::ACTIVE
┌───────────────┴─────────────────────────────────────────────────────┐
│                      freeink-sdk (hardware)                          │
│  BoardConfig (M5PAPER_DIY)  ·  FreeInkDisplay  ·  InputManager       │
│  PowerManager  ·  BatteryMonitor  ·  Rtc/Imu/Frontlight (stubs)      │
└───────────────▲─────────────────────────────────────────────────────┘
                │ LgfxEpdConfig / PM1
┌───────────────┴─────────────────────────────────────────────────────┐
│  M5GFX Panel_EPD / Bus_EPD  →  ED047TC1 (960×540, 16 grises)         │
│  M5PM1 (I²C 41/42): rail EPD, VBAT, carga, shutdown                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Flujo de una página

1. `EpubReaderActivity` pide una sección al `Epub`/`Section`.
2. `Section` parsea HTML/CSS y genera `Page` con bloques de texto/imagen.
3. `GfxRenderer` pinta en un framebuffer de 1 bpp y, para AA, en planos de
   grises (LSB/MSB).
4. `HalDisplay` llama al driver `LgfxEpd`.
5. `LgfxEpdDriver` expande el framebuffer a un canvas de 8 bits en PSRAM y
   hace `pushSprite` a `Panel_EPD` con el modo de refresco adecuado.
6. `Panel_EPD` genera el timing paralelo y el PM1 mantiene el rail EPD.

Para texto normal se usa `epd_text` (limpio); para cambios pequeños,
`epd_fast`. El driver normaliza el banco limpio si hace falta
(`cleanBankNeedsFreshBackground`), una propiedad que hay que validar en el
PaperDIY.

## Perfil de placa

`BoardConfig.h` define `M5PAPER_DIY`:

```cpp
constexpr BoardProfile M5PAPER_DIY = {
    Board::M5PaperDiy,
    "paperdiy",
    InputStyle::DigitalTwoButton,
    DisplayController::LgfxEpd,
    960, 540,
    {/* display pins: none, parallel config */},
    0,
    {39, 40, 38, 47, PIN_UNASSIGNED, false, 0},   // SD SPI
    {PIN_UNASSIGNED, ..., 4, 3, PIN_UNASSIGNED, false}, // up=A, down=B
    PIN_UNASSIGNED, PIN_UNASSIGNED, 2.0f, PIN_UNASSIGNED,
    NO_TOUCH, NO_FRONTLIGHT, NO_AUDIO, NO_LEDS, NO_FLIP,
    NO_SDMMC, NO_GAUGE, NO_MIC, NO_SENSORS,
    1.0f, {}, 0, {}, false, NO_I2C_FRONTLIGHT, {},
    0, 0, 0, 100, 100, 0, true, 0, 0
};
```

Los campos que importan:

- `DisplayController::LgfxEpd` → `FreeInkDisplay` usa `LgfxEpdDriver`.
- `InputStyle::DigitalTwoButton` → `InputManager` sintetiza up/down/back/confirm/power.
- `batteryAdc = -1`, `NO_GAUGE` → `BatteryMonitor` cae en el backend M5PM1.
- `NO_SENSORS` → sin RTC/IMU; `Rtc`/`Imu` quedan como stubs.
- `power = {}` → no hay latch GPIO; el PM1 gestiona la energía.

## BoardPaperDiy

`freeink-sdk/libs/hardware/BoardPaperDiy/`:

- `BoardPaperDiyPins.h`: pines del panel, botones, PM1.
- `BoardPaperDiy.cpp`:
  - `ensureBooted()`: `m5pm1::beginBus()`, activa `CHG_EN | DCDC_EN` (sin
    BOOST/LDO/LED), configura GPIO2 (rail EPD), GPIO3 (CHG_STAT) y el botón
    power del PM1;
  - `setEpdPower()` / `prepareEpdPower()` / `powerDownEpdPower()`;
  - `pollPowerButtonClicked()`: lee el evento PM1 y lo entrega como `BTN_POWER`;
  - `powerOff()`: `m5pm1::requestShutdown()`.
- `PaperDiyLgfxConfig.cpp`: `LgfxEpdConfig` con los pines del PaperS3 y el hook
  `prepare`.
- `InputManager` llama a `ensureBooted()` y sondea el botón power.

## Energía y sueño

- **Batería:** `HalPowerManager::startDeepSleep()` pide shutdown al PM1
  (`SYS_CMD 0xA1`). Si el USB mantiene la placa, hace deep sleep y despierta
  con A/B.
- **Botón power:** `configureAppPowerButton()` desactiva el single-click reset
  del PM1 y el clic se entrega como `BTN_POWER`; la acción corta por defecto es
  dormir/apagar. `PAPERDIY_PM1_APP_POWER_BUTTON=0` restaura el reset de fábrica.
- **Wake:** `PowerManager::armPowerButtonWakeup()` arma `ext1` en GPIO3/4
  (activo bajo), porque no hay un power GPIO. `waitForPowerButtonRelease()`
  espera a que se suelten A y B para que el toque de wake no se convierta en un
  page turn.
- **Rails:** `powerDownRailsForSleep()` corta PM1 GPIO2 después de que el panel
  reciba el comando de sleep.
- **BatteryMonitor:** `hasM5Pm1Backend()` incluye PaperDIY; lee VBAT/VIN/VOUT,
  `PWR_SRC` y CHG_STAT (GPIO3) del PM1.
- **Framebuffer:** `FREEINK_FB_PSRAM` lo coloca en PSRAM.

## Almacenamiento

CrossPoint cachea en la SD:

```
/.crosspoint/
├── epub_<hash>/
│   ├── progress.bin
│   ├── cover.bmp
│   ├── book.bin
│   ├── css_rules.cache
│   ├── img_*
│   └── sections/*.bin
├── settings.json
├── state.json
└── recent.json
```

Borrar `/.crosspoint` fuerza a regenerar cachés. Los libros, fuentes y
diccionarios viven fuera de esa carpeta (ver guía de usuario).

## Build

- `platformio.ini`, env `paperdiy`.
- Plataforma pioarduino 55.03.311, Arduino-ESP32 3.3.11.
- `FREEINK_DEVICE_PAPERDIY=1`, `FREEINK_CAP_USB_MSC=1`,
  `FREEINK_CAP_BLE_HID_HOST=1`, `FREEINK_FB_PSRAM`.
- `BoardPaperDiy` + `M5GFX` en `lib_deps`.
- `partitions.csv` da ~6,25 MB a la app; el build actual usa 5,35 MB (81,6%).
- El `Makefile` usa `PLATFORMIO_CORE_DIR=.platformio-core` para reproducibilidad.
- `CROSSPOINT_OTA_RELEASES_URL` permite apuntar la OTA al fork.

## Por qué vendorizado

`main` es un espejo de `upstream/develop`; `paperdiy` es el fork con
CrossPoint 2.0 + `freeink-sdk` vendorizado. Ventajas: se clona y se compila sin
depender de commits de submódulos; el port es autocontenido. Desventaja:
actualizar desde upstream requiere re-vendorizar el SDK y reaplicar
`patches/sdk.patch` + `patches/firmware.patch`. Ver
[`10-fork-maintenance.md`](10-fork-maintenance.md).
