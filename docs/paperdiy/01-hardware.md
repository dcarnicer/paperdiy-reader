# 01 — Hardware y pines

## Specs

| | |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8 (dual-core LX7, 240 MHz) |
| Flash | 16 MB |
| PSRAM | 8 MB Octal (OPI) |
| Pantalla | ED047TC1, 4,7", 960×540, 16 niveles de gris, 234 PPI |
| Interfaz de pantalla | paralela de 8 bits, **sin controlador IT8951** |
| Botones | A=GPIO4, B=GPIO3 (activos a nivel bajo); power por M5PM1 |
| Batería | 140 mAh, cargada por M5PM1 |
| SD | microSD por SPI |
| USB | USB-C nativo del ESP32-S3 (Serial/JTAG) |
| Radio | Wi-Fi 2,4 GHz, BLE 5.0 |
| Sin | táctil, frontlight, RTC, IMU, audio, Grove |

## Mapa de pines

### Panel (idéntico al M5Paper S3)

| Señal | GPIO | Notas |
|---|---:|---|
| D0 | 6 | bus de datos |
| D1 | 14 | |
| D2 | 7 | |
| D3 | 12 | |
| D4 | 9 | |
| D5 | 11 | |
| D6 | 8 | |
| D7 | 10 | |
| XCL / CL | 16 | pixel clock |
| XLE / LE | 15 | latch |
| XSTL / SPH | 13 | start pulse horizontal |
| XOE / OE | 45 | output enable |
| CKV | 18 | gate clock |
| SPV | 17 | start pulse vertical |
| PWR | 46 | enable del boost del panel |
| PM1 GPIO2 | — | rail EPD adicional, vía I²C |

El `LgfxEpdConfig` del port usa exactamente estos pines. `Panel_EPD` de
LovyanGFX secuencia OE → PWR → SPV; el rail del PM1 se sube antes, en el hook
`prepare()`.

### SD

| Señal | GPIO |
|---|---:|
| SCLK | 39 |
| MISO | 40 |
| MOSI | 38 |
| CS | 47 |

SPI, SdFat, FAT32/exFAT. La SD comparte el bus SPI con el panel? No: el panel
es paralelo; la SD es SPI dedicada. Aun así, el SDK usa `SdFat` sobre SPI.

### Botones

| Botón | GPIO | Tipo |
|---|---:|---|
| A | 4 | activo bajo, pull-up externo |
| B | 3 | activo bajo, pull-up externo |
| Power | — | M5PM1; single click on/reset, doble click off, long press download |

`InputStyle::DigitalTwoButton` traduce:

- A corto → `BTN_UP`
- B corto → `BTN_DOWN`
- A largo → `BTN_BACK`
- B largo → `BTN_CONFIRM`
- A+B → `BTN_POWER`

### M5PM1

| Señal | GPIO |
|---|---:|
| I²C SDA | 41 |
| I²C SCL | 42 |
| Dirección | 0x6E |
| GPIO2 | rail EPD |
| GPIO3 | CHG_STAT (entrada, activo bajo) |

El PM1 también gestiona la carga, el botón de power y el apagado. El firmware
lo usa para:

- subir el rail EPD antes de inicializar el panel;
- leer VBAT/VIN/VOUT y el estado de carga;
- apagar el equipo (`SYS_CMD 0xA1`);
- cortar el rail EPD antes de deep sleep.

## Refrescos del panel

M5GFX expone cuatro modos:

| Modo | Uso típico | Compromiso |
|---|---|---|
| `epd_quality` | portada, imágenes, primer pintado | más lento, más grises/calidad |
| `epd_text` | página completa de texto | limpio, puede parpadear |
| `epd_fast` | cambios pequeños, UI | rápido, más ghosting |
| `epd_fastest` | animaciones/feedback | muy rápido, ghosting alto |

CrossPoint usa un framebuffer de 1 bpp + planos de grises para antialiasing;
`LgfxEpdDriver` mapea `Full/Half` a `epd_text` y `Fast/Fastest` a `epd_fast`.
El port mantiene las LUTs estándar de `Panel_EPD` para `quality` y `text`.
Para `fast`/`fastest` usa la waveform AA de ED047TC1 validada en el LilyGo
T5 S3: una sola LUT para la base B/W y el plano de grises, con empuje
específico para los niveles que produce el antialiasing. Está pendiente de
validar en PaperDIY porque el PMIC/VCOM es distinto. Ver
[`06-porting.md`](06-porting.md#ghosting-al-pasar-páginas).

## Energía

- Batería 140 mAh: poca. El consumo medio importa más que el pico.
- Deep sleep: el ESP32-S3 baja a decenas de µA, pero los rails del PM1, la SD y
  el panel pueden sumar mA. El port corta el rail EPD del PM1 en
  `PowerManager::powerDownRailsForSleep()`; hay que medir.
- Wake: `ext1` en GPIO3/4 (RTC GPIOs del S3), activo bajo. Cualquiera de los
  dos botones despierta.
- Carga: `CHG_EN` del PM1 habilita el LGS4056H. El esquema K159 lleva
  `R11=2K`, que fija 500 mA; con la celda original de 140 mAh son ~3,6C y con
  una 604050 de ~2000 mAh, ~0,25C.
- `CHG_STAT` es PM1 GPIO3, activo bajo: se lee para saber si realmente está
  cargando, no solo si hay USB.
- Protección de baja tensión: `REG_BATT_LVP` a 3,4 V.
- El botón físico de power no es un GPIO del ESP32; no se puede leer por
  firmware. Para dormir desde la UI se usa A+B.

### Presupuesto orientativo (a medir)

| Estado | Corriente esperada | Autonomía con 140 mAh |
|---|---:|---:|
| Activo leyendo (Wi-Fi off) | 40–80 mA | 2–3,5 h |
| Activo con Wi-Fi | 100–150 mA | <1,5 h |
| Deep sleep (bien configurado) | 20–100 µA | semanas/meses |
| Deep sleep con rails mal cortados | 1–5 mA | días |

La conclusión práctica: el lector debe dormir tras un timeout corto y entre
sesiones; el botón de página despierta, pinta y vuelve a dormir. CrossPoint ya
tiene auto-sleep; hay que ajustar el timeout y medir.

## Mods de hardware (opcionales)

- **Batería mayor**: el kit trae 140 mAh; una celda de 500–1000 mAh en el
  hueco de la carcasa multiplica la autonomía. Requiere comprobar espacio,
  conector y carga (el PM1 regula).
- **RTC I²C**: un DS3231/PCF8563 en el bus interno (41/42) daría hora real y
  alarmas; hay que añadir soporte en `BoardConfig`/`Rtc`.
- **Encoder rotativo o 5-way**: un GPIO extra + I²C/ADC permitiría una UI tipo
  rueda; requiere modificar la carcasa.
- **Sensor Hall en la funda**: dormir/despertar al cerrar/abrir; un GPIO libre
  con imán.
- **Frontlight**: no es trivial; la solución realista es un clip de luz
  externo. No hay rail ni LED integrado.

## Modo descarga y recuperación

- Mantener power ~2 s hasta que el LED rojo parpadee → modo descarga.
- `esptool --chip esp32s3 --port ... write_flash 0x0 firmware.factory.bin`
  recupera el equipo aunque la app esté corrupta.
- Guarda un backup del firmware original antes de la primera instalación.
