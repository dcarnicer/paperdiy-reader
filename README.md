# PaperDIY Reader

Firmware de lectura rico en funciones para la **M5Stack PaperDIY** (ESP32-S3 +
panel E Ink ED047TC1 de 4,7", 960×540, 16 grises), construido sobre
[CrossPoint Reader 2.0](https://github.com/crosspoint-reader/crosspoint-reader)
(MIT). La meta no es un POC: es un e-reader con biblioteca, ajustes, fuentes,
diccionario, sync, OPDS/Calibre y el resto de cosas que hacen usable el aparato
a diario.

> **Estado:** el firmware **compila, arranca y lee EPUB en un PaperDIY real**.
> Primera validación (28/10/2026): pantalla/UI, botones A/B, batería, SD,
> biblioteca y lectura EPUB OK; la UI se ve correcta en vertical. Pendiente:
> Wi-Fi/OPDS/Calibre, ghosting, consumo en sleep, botón power/shutdown, wake y
> OTA. Ver [`docs/paperdiy/06-porting.md`](docs/paperdiy/06-porting.md).
>
> **Fork downstream:** `main` es un espejo de `upstream/develop`; `paperdiy`
> es nuestra rama de trabajo. El SDK `freeink-sdk` está vendorizado para que el
> repo se clone y compile sin submódulos. Ver
> [`docs/paperdiy/10-fork-maintenance.md`](docs/paperdiy/10-fork-maintenance.md).

## Por qué este repo

El repo de ejemplos `melastmohican/m5paperdiy-arduino-examples` demuestra que el
panel y los botones funcionan, pero su `EpubReader` es un port del lector de
atomic14: sin persistencia, sin biblioteca, sin ajustes, sin Wi-Fi, sin sueño
profundo y con refresco completo en cada página. CrossPoint ya resuelve el motor
EPUB, el layout, las fuentes, la caché en SD, la biblioteca, el diccionario,
OPDS, Calibre, KOReader Sync, la web UI y OTA. Lo que faltaba era la capa de
placa del PaperDIY.

Este repo añade esa capa:

- perfil `M5PAPER_DIY` dentro de `freeink-sdk` (pantalla, botones, batería,
  energía, wake);
- `BoardPaperDiy` con el bus paralelo ED047TC1 y el rail EPD del **M5PM1**;
- `paperdiyLgfxConfig` reutilizando el bus del PaperS3 (mismos pines);
- batería/estado de carga por M5PM1;
- botón power del PM1 como `BTN_POWER`, apagado en batería y fallback de deep
  sleep por USB despertando con A/B;
- framebuffer en PSRAM (`FREEINK_FB_PSRAM`);
- OTA configurable (`CROSSPOINT_OTA_RELEASES_URL`) para no descargar firmware
  oficial;
- env de PlatformIO `paperdiy`.

## Hardware

| | PaperDIY |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8, 240 MHz |
| Flash / PSRAM | 16 MB / 8 MB Octal |
| Pantalla | ED047TC1 4,7" 960×540, 16 grises, bus paralelo de 8 bits |
| Entrada | 2 botones de usuario (GPIO4 = A, GPIO3 = B), botón de power gestionado por el PM1 |
| Energía | M5PM1; batería de 140 mAh; USB-C |
| SD | microSD por SPI (SCLK39 / MISO40 / MOSI38 / CS47) |
| Conectividad | Wi-Fi 2,4 GHz + BLE 5 |
| Sin | táctil, frontlight, RTC, IMU, audio |

El bus del panel es **pin a pin el mismo que el del M5Paper S3**: D0–D7 =
6,14,7,12,9,11,8,10; CL=16, LE=15, SPH=13, SPV=17, CKV=18, OE=45, PWR=46. La
diferencia es que el PaperDIY necesita además el rail EPD del M5PM1 (GPIO2 por
I²C en SDA41/SCL42).

## Controles (2 botones)

CrossPoint usa `InputStyle::DigitalTwoButton`, pensado exactamente para dos
botones:

| Gesto | Acción |
|---|---|
| **A** (GPIO4) corto | arriba / página anterior / mover selección arriba |
| **B** (GPIO3) corto | abajo / página siguiente / mover selección abajo |
| **A** largo | atrás / salir |
| **B** largo | confirmar / seleccionar |
| **A + B** | botón power (menú de energía / dormir) |
| Power corto | acción configurada; por defecto dormir/apagar (el PM1 entrega el clic al firmware) |
| Power doble clic | apagado hardware (si el PM1 lo mantiene habilitado) |
| Power ~2 s | modo descarga (LED rojo) |
| Power desde apagado | encender |

El comportamiento del power cambia respecto a fábrica: con
`PAPERDIY_PM1_APP_POWER_BUTTON=1` (por defecto) el single-click reset del PM1
se desactiva para que el clic llegue a CrossPoint. Si prefieres el reset de
fábrica, compila con `-DPAPERDIY_PM1_APP_POWER_BUTTON=0`; entonces usa A+B para
dormir.

La navegación es la principal limitación del hardware. El plan incluye
remapeo de botones, atajos contextuales y **BLE page turner** (ya compilado)
para poder pasar página con un mando o el móvil.

## Qué incluye (heredado de CrossPoint 2.0)

- **Motor EPUB 2/3**: CSS, imágenes, hiphenación, kerning, tablas, footnotes,
  navegación por capítulos, ruby CJK, RTL, modo focus, orientación.
- **Biblioteca**: índice de títulos/autores, portadas, recientes, búsqueda,
  navegador de carpetas, caché en SD.
- **Lectura**: posición guardada, bookmarks, highlights/clippings, ir a %,
  auto page turn, temas, modo noche, tipografías y tamaños.
- **Diccionario StarDict** y búsqueda de palabras.
- **Sync**: KOReader Sync, Calibre wireless, OPDS (con búsqueda y paginación),
  WebDAV, web UI para subir libros, OTA.
- **Formatos**: `.epub`, `.xtc/.xtch`, `.txt`, `.bmp`.
- **Fuentes**: incluidas + TTF/OTF en la SD.
- **Internacional**: 35 idiomas de interfaz (español incluido).
- **PaperDIY**: BLE HID host (page turner) y USB Mass Storage activados en el
  env `paperdiy`.

## Compilar

Requisitos: PlatformIO Core y conexión a internet la primera vez (el core
aislado descarga plataforma, framework y toolchain; ~5 GB).

```bash
make build
# equivalente a:
PLATFORMIO_CORE_DIR="$PWD/.platformio-core" pio run -e paperdiy
```

El binario queda en:

```
.pio/build/paperdiy/firmware.bin          # app (offset 0x10000)
.pio/build/paperdiy/firmware.factory.bin  # imagen completa (offset 0x0)
```

Si tu `~/.platformio` global ya está sano, `pio run -e paperdiy` también
funciona. El `Makefile` usa un core aislado para que el build sea reproducible
aunque haya paquetes viejos. `.platformio-core/` y `.pio/` son cachés locales
(git-ignored); se pueden borrar y `make build` las reconstruye.

## Flashear

1. Conecta el PaperDIY por USB-C.
2. Mantén el botón de power ~2 s hasta que el LED rojo parpadee (modo descarga).
3. Primera instalación (imagen completa, incluye bootloader y tabla de
   particiones):

```bash
make flash-factory PORT=/dev/cu.usbmodemXXXX
```

Para actualizar solo la app (conserva bootloader/particiones):

```bash
make flash PORT=/dev/cu.usbmodemXXXX
```

o, para control total:

```bash
# actualización de la app (conserva bootloader/particiones)
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x10000 .pio/build/paperdiy/firmware.bin

# primera instalación / recuperación (imagen completa)
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x0 .pio/build/paperdiy/firmware.factory.bin
```

Antes de flashear por primera vez, haz un backup del firmware original:

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  read_flash 0 0x1000000 paperdiy-original.bin
```

## Estructura

```
.
├── src/                  # app CrossPoint (actividades, lector, UI, red)
├── lib/                  # Epub, GfxRenderer, EpdFont, HAL, etc.
├── freeink-sdk/          # SDK de hardware + perfiles de placa
│   └── libs/hardware/
│       ├── BoardConfig/  # M5PAPER_DIY + M5Pm1
│       └── BoardPaperDiy/# bus ED047TC1, rail PM1, power-off
├── docs/paperdiy/        # investigación, hardware, roadmap, port
├── docs/upstream/        # README/user guide originales de CrossPoint
├── platformio.ini        # env `paperdiy`
└── Makefile
```

## Documentación

- [Investigación y estado actual](docs/paperdiy/00-research.md)
- [Hardware y pines](docs/paperdiy/01-hardware.md)
- [Análisis del POC y del ecosistema](docs/paperdiy/02-current-state.md)
- [Matriz de funcionalidades](docs/paperdiy/03-feature-matrix.md)
- [Arquitectura](docs/paperdiy/04-architecture.md)
- [Roadmap](docs/paperdiy/05-roadmap.md)
- [Notas del port y validación](docs/paperdiy/06-porting.md)
- [Guía de usuario PaperDIY](docs/paperdiy/07-user-guide.md)
- [Fuentes](docs/paperdiy/08-sources.md)
- [Prior art: issue #4005 y PRs de PaperDIY](docs/paperdiy/09-prior-art.md)
- [Mantener el fork y actualizar upstream](docs/paperdiy/10-fork-maintenance.md)
- [Borrador de comentario para la issue #4005](docs/paperdiy/11-upstream-note.md)

## Limitaciones conocidas

- Sin validación en hardware todavía: rotación, LUTs, ghosting, corriente de
  sueño y autonomía son los primeros puntos a medir.
- Sin táctil, frontlight, RTC, IMU ni audio. La UI debe funcionar con 2 botones.
- Batería de 140 mAh: en batería el equipo pide apagado al PM1 al dormir; con
  USB hace deep sleep y despierta con A/B. La autonomía sigue pendiente de
  medir.
- El botón físico de power lo gestiona el M5PM1; el firmware lo recibe como
  evento I²C, no como GPIO.
- La OTA apunta por defecto al repo oficial, pero no hay asset `-paperdiy`, así
  que no instala firmware ajeno. Para OTA propia hay que configurar
  `CROSSPOINT_OTA_RELEASES_URL`.
- CrossPoint 2.0 es la rama de desarrollo (2.0.0), no la 1.6.x estable.

## Créditos y licencia

MIT. El motor y la mayor parte del código son de
[CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader)
(Copyright 2025 CrossPoint Reader organization); el SDK de hardware es
[FreeInk](https://github.com/crosspoint-reader/crosspoint-reader) (MIT); el
panel se maneja con M5GFX/LovyanGFX. Ver [LICENSE](LICENSE) y [NOTICE](NOTICE).
