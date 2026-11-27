# PaperDIY Reader

**Idiomas:** **Español** · [English](README.en.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

Firmware de lectura rico en funciones para la **M5Stack PaperDIY** (ESP32-S3 +
panel E Ink ED047TC1 de 4,7", 960×540, 16 grises), construido sobre
[CrossPoint Reader 2.0](https://github.com/crosspoint-reader/crosspoint-reader)
(MIT). La meta no es un POC: es un e-reader con biblioteca, ajustes, fuentes,
diccionario, sync, OPDS/Calibre y el resto de cosas que hacen usable el aparato
a diario.

Desde `2.0.0-12` también funciona, de forma experimental, en la
**Waveshare ESP32-S3-ePaper-3.97** (ver
[Waveshare ESP32-S3-ePaper-3.97](#waveshare-esp32-s3-epaper-397-experimental)).

> **Estado:** el firmware **compila, arranca y lee EPUB en un PaperDIY real**.
> Validación (04/11/2026): arranque, pantalla/UI, Home, wake, botones A/B,
> batería, SD y navegación OK tras sincronizar con CrossPoint `308cd522`.
> Smoke del sync `5d731041` (06/11/2026): arranque, Home, A/B y About con
> tamaño/usado/libre de SD y batería.
> Smoke del sync `818a1540` y del stack de dependencias (08/11/2026): arranque,
> Home, menús, lector, paginación, orientaciones, USB MSC y diccionario
> StarDict. Smoke del sync `f8db833f` (09/11/2026): arranque, Home, lector,
> recorte multipalabra con A/B, selector de enlaces, orientación, About y
> USB MSC. Sleep/wake no se repitió; el camino de energía no cambia.
> Smoke del sync `8276d518` (10/11/2026): arranque, Home, A/B, lector con page
> turns, OTA sin actualizaciones, fuente descargada/instalada, orientación,
> OPDS con descarga, USB MSC (DABI, escritura/expulsión), BLE activado/escaneo
> y servidor Calibre. Quedan pendientes ghosting/autonomía, sleep/wake,
> emparejamiento BLE real, envío Calibre completo y OTA completa.
> Smoke del sync `fa17b9ca` (12/11/2026): `make smoke` PASS 25 pasos (Home,
> explorador, lector, TOC, enlaces, nota al pie, recorte y diccionario); build
> de producción `2.0.0-5` flasheado y arranca en Home. Pendientes:
> ghosting/autonomía, sleep/wake, emparejamiento BLE real, envío Calibre
> completo y OTA completa.
> La lectura EPUB, Wi-Fi, web UI y transferencia de libros ya se validaron el
> 28/10/2026. Calibre wireless y OTA verificados el 04/11/2026. OPDS
> (Project Gutenberg) verificado el 05/11/2026. Auto-suspensión y sleep screen
> con portada verificadas el 05/11/2026. Lectura larga: 250+ cambios de página
> sin errores ni fugas el 06/11/2026. KOReader Sync validado contra un servidor
> KOSync local el 06/11/2026. Pendiente: emparejar un mando BLE, consumo en
> sleep y revisión visual física del ghosting. `make smoke` completo superado
> en el árbol de `2.1.0-1` (sync `a2b0d48b`, 26/11/2026) en las dos placas:
> PaperDIY run `20261126-203815` y Waveshare 3.97 run `20261126-193226`. Ver
> [`docs/paperdiy/06-porting.md`](docs/paperdiy/06-porting.md).
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

### Carcasa 3D

El **PaperDIY Complete Kit** de M5Stack incluye una carcasa impresa en PLA. La
versión actual de nuestra carcasa es la **v21**, en STL en
[`hardware/3d/v21/`](hardware/3d/v21/): tapa trasera con hendidura para un
anillo MagSafe, marco frontal, una barra basculante para A/B y una palanca para
el botón C (power). La versión anterior,
[`hardware/3d/PaperDIY_kit_completo.3mf`](hardware/3d/PaperDIY_kit_completo.3mf),
es una modificación del modelo oficial con los tres botones originales y se
abre como proyecto de Bambu Studio.

El modelo original, la licencia MIT de M5Stack y el aviso de los tornillos M2
están en [`hardware/README.md`](hardware/README.md).

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
| Power ~10 s | modo descarga (LED rojo; la pantalla puede congelarse) |
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

Requisitos: PlatformIO Core, `python3` y conexión a internet la primera vez
(el core aislado descarga plataforma, framework y toolchain; ~5 GB).

```bash
make build
# equivalente a:
core="$(make -s core-dir)" && PLATFORMIO_CORE_DIR="$core" python3 scripts/pio_lock.py pio run -e paperdiy
```

El binario queda en:

```
.pio/build/paperdiy/firmware.bin          # app (offset 0x10000)
.pio/build/paperdiy/firmware.factory.bin  # imagen completa (offset 0x0)
```

Si tu `~/.platformio` global ya está sano, `pio run -e paperdiy` también
funciona. El `Makefile` usa un core aislado para que el build sea reproducible
aunque haya paquetes viejos. Lo elige `scripts/pio_core_dir.py`: un core por
versión fijada de la plataforma, fuera del repo, por ejemplo
`~/.platformio-cores/pioarduino-55.03.311` (`make -s core-dir` muestra la
ruta). Lo comparten todos los clones y worktrees de esa versión, así que los
~5 GB se descargan una vez por versión; otra versión usa su propio core. Los
entornos con `custom_sdkconfig` (`default`, `slim`, `sticky`…) siguen usando
`.platformio-core/` dentro del checkout, porque pioarduino recompila el
framework dentro del core. Para usar otra carpeta: `make build CORE_DIR=/ruta`.
`make` (build, flash, size, clean), `scripts/build.sh` y `scripts/flash.sh`
bloquean el core (`scripts/pio_lock.py`): si dos usan el mismo core, el segundo
espera a que termine el primero. Un `pio run` lanzado sin `pio_lock.py` no toma
el bloqueo.

Si no compilas entornos con `custom_sdkconfig`, el `.platformio-core/` que
dejaron builds anteriores ya no se usa y se puede borrar. Tras subir la versión de la
plataforma, borra el core viejo de `~/.platformio-cores` cuando ninguna rama lo
use; borrar un core hace que todos los checkouts de esa versión lo vuelvan a
descargar. `.pio/` es una caché local (git-ignored) que `make build`
reconstruye.

## Flashear

1. Conecta el PaperDIY por USB-C.
2. Mantén el botón de power ~10 s hasta que el LED rojo parpadee (modo descarga).
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

### M5Launcher

Con [M5Launcher](https://github.com/bmorcelli/Launcher) 3.0.0 o superior
(port PaperDIY), instala **CrossPoint for PaperDIY (community port)** desde
`M5Launcher > OTA`, o la imagen completa `crosspoint-paperdiy-latest.bin` de
la release desde la SD (`SD > Install`), la WebUI o Favoritos. Es la misma
imagen que va a M5Burner; Launcher copia solo la app.

> **OTA bajo Launcher:** el lector no se actualiza a sí mismo bajo
> M5Launcher. `Verificar actualizaciones` avisa si hay versión nueva en el
> catálogo; instálala desde `M5Launcher > OTA` y **borra después la versión
> anterior**, porque Launcher instala cada versión junto a la vieja. No
> flashees `firmware.bin` en `0x10000` con Launcher instalado.

El lector detecta Launcher y
muestra `Ajustes > Sistema > Salir a M5Launcher`; la actualización por SD se
oculta porque Launcher es quien gestiona las particiones OTA. Para que el
lector despierte sin pasar por la pantalla de Launcher, configura en Launcher
`CFG > GPIO on boot starts Launcher` = A: Launcher solo aparecerá al encender
con A pulsado. Ver
[`docs/paperdiy/13-m5launcher.md`](docs/paperdiy/13-m5launcher.md).

## Waveshare ESP32-S3-ePaper-3.97 (experimental)

La [Waveshare ESP32-S3-ePaper-3.97](https://www.waveshare.com/esp32-s3-epaper-3.97.htm)
es la segunda placa del fork. Usa el mismo firmware con su propio env
(`ws397`); el soporte viene de PRs de upstream que aún no están fusionados.

| | Waveshare 3.97 |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8, 240 MHz |
| Flash / PSRAM | 16 MB / 8 MB Octal |
| Pantalla | 3,97" 800×480 en blanco y negro, controlador SSD1677 por SPI; grises por LUT |
| Entrada | botonera lateral (Arriba / OK / Abajo) y BOOT; la tecla PWR no llega al firmware |
| Energía | PMIC AXP2101 (serigrafiado TG28): batería y carga |
| SD | microSD por SDMMC de 4 bits |
| Otros | reloj PCF85063, IMU QMI8658, Wi-Fi 2,4 GHz + BLE 5; audio ES8311 sin uso |

| Tecla | Acción |
|---|---|
| Arriba / Abajo | mover la selección; pasar página |
| OK | seleccionar |
| BOOT corto | atrás |
| BOOT mantenido | dormir |
| BOOT con la placa dormida | despertar (mantenlo un momento) |

No hay fila de pistas de botones: la placa no tiene botones frontales.

**Instalar:** si quieres conservar el firmware que trae la placa, haz antes
una copia (en nuestra unidad, leer toda la flash de una vez con esptool
fallaba; ver el doc enlazado abajo). Después descarga
`crosspoint-ws397-latest.bin` de la release y grábalo con la placa conectada
por USB-C:

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX write-flash 0x0 crosspoint-ws397-latest.bin
```

Grabarla en `0x0` borra los ajustes del firmware anterior, pero no los libros
de la SD. Las siguientes versiones llegan por `Verificar actualizaciones`, que
busca `crosspoint-ws397-<versión>-ota.bin` en la release; también puedes copiar
ese fichero a la raíz de la SD y usar `Actualizar firmware por tarj. SD`, o
`make flash ENV=ws397` si compilas. `Transferir archivos → Unidad USB` monta
la SD en el ordenador. No hay M5Burner ni M5Launcher para esta placa.

Detalles, grabado, copia de seguridad y limitaciones en
[`docs/paperdiy/15-waveshare-397.md`](docs/paperdiy/15-waveshare-397.md).

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
├── hardware/3d/          # carcasa 3D (v21 y remix del kit completo)
├── platformio.ini        # env `paperdiy`
└── Makefile
```

## Documentación

El índice, la guía de usuario y las notas de hardware y port también están
disponibles en [English](docs/paperdiy/README.en.md),
[简体中文](docs/paperdiy/README.zh-CN.md) y
[日本語](docs/paperdiy/README.ja.md).

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
- [Testing por USB](docs/paperdiy/12-serial-testing.md)
- [M5Launcher](docs/paperdiy/13-m5launcher.md)
- [Regresión determinista en hardware](docs/paperdiy/14-device-regression.md)
- [Waveshare ESP32-S3-ePaper-3.97 (experimental)](docs/paperdiy/15-waveshare-397.md)

## Limitaciones conocidas

- Pendientes de medir: LUTs/ghosting tras muchas páginas y corriente de sueño.
  La autonomía solo se midió con la 604050 extendida (45,4 h y 5.448 páginas
  en una descarga real); la celda original de 140 mAh no se midió en esa
  prueba. Ambas curvas siguen pendientes de validar en lectura normal.
- Sin táctil, frontlight, RTC, IMU ni audio. La UI debe funcionar con 2 botones.
- Batería de 140 mAh: al dormir, el firmware pide apagado al PM1. Si el PM1
  corta la alimentación (lo habitual, también con USB), solo el botón power
  vuelve a encender. Verificado el 05/11/2026: A+B con USB apagó vía PM1 y A
  no despertó. Si el USB mantiene la placa viva, el fallback es deep sleep
  con wake A/B.
- El botón físico de power lo gestiona el M5PM1; el firmware lo recibe como
  evento I²C, no como GPIO.
- La OTA del env `paperdiy` consulta las releases de este repo
  (`CROSSPOINT_OTA_RELEASES_URL`) y descarga `crosspoint-paperdiy-<versión>-ota.bin`
  (`CROSSPOINT_OTA_ASSET_FORMAT`); ambos se fijan en `platformio.ini`.
- CrossPoint 2.0 es la rama de desarrollo (2.0.0), no la 1.6.x estable.

## Créditos y licencia

El código fuente es MIT. El motor y la mayor parte del código son de
[CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader)
(Copyright 2025 CrossPoint Reader organization); el SDK de hardware es
[FreeInk](https://github.com/Free-Ink/freeink-sdk) (MIT); el panel se maneja con
M5GFX/LovyanGFX. Las librerías de terceros conservan sus licencias.

El **firmware compilado** (los `.bin` de las releases y de M5Burner) es
**GPLv3** porque incluye wolfSSL. Cada release adjunta un `LICENSE` con los
textos completos, los avisos de terceros y las revisiones del código fuente;
ver [`licenses/README.md`](licenses/README.md).

La carcasa 3D es un remix del modelo MIT de
[M5Stack](https://github.com/m5stack/M5_Hardware) y también es MIT. Ver
[LICENSE](LICENSE) y [NOTICE](NOTICE).
