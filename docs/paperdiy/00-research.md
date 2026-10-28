# 00 — Investigación y estado actual

> Fecha de la investigación: 28 de octubre de 2026. Versiones y enlaces
> consultados ese día.

## Resumen ejecutivo

El PaperDIY es un e-reader DIY con hardware muy cercano al M5Paper S3: mismo
SoC (ESP32-S3 N16R8), mismo panel de 4,7" 960×540 y, lo más importante, **el
mismo bus paralelo de 8 bits**. La diferencia es que el PaperDIY no lleva
IT8951, no tiene táctil/RTC/IMU/audio y usa un PMIC M5PM1 con una batería muy
pequeña (140 mAh). Tiene dos botones de usuario y un botón de power gestionado
por el PM1.

El repo de ejemplos de PaperDIY demuestra el hardware, pero su lector EPUB es
un POC: no guarda posición, no tiene biblioteca ni ajustes, no usa Wi-Fi, no
duerme y refresca la pantalla completa en cada página. Partir de ahí para
llegar a un lector "rico" sería reescribir casi todo.

CrossPoint Reader 2.0 ya tiene ese "casi todo": motor EPUB 2/3 con CSS,
imágenes, hiphenación, fuentes TTF, biblioteca, bookmarks, highlights,
diccionario StarDict, OPDS, Calibre, KOReader Sync, WebDAV, web UI, OTA, temas y
35 idiomas. Además, su SDK (`freeink-sdk`) ya trae perfiles para M5Paper S3 y
LilyGo T5 S3, ambos con el mismo panel ED047TC1 en paralelo. El port al
PaperDIY es, sobre todo, un **perfil de placa + el rail EPD del M5PM1 + los dos
botones**.

**Decisión:** fork de CrossPoint 2.0 con soporte PaperDIY, no un lector nuevo
desde cero. El repositorio conserva la licencia MIT y la atribución.

> **Prior art:** existe una issue abierta en CrossPoint
> ([#4005](https://github.com/crosspoint-reader/crosspoint-reader/issues/4005))
> y varios PRs en borrador de `prateek` con un port muy parecido, además de
> lectores PaperDIY independientes. Ninguno está mergeado ni validado en
> hardware. Ver [`09-prior-art.md`](09-prior-art.md).

## Hardware, en corto

| Elemento | Detalle |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8, dual-core LX7 @240 MHz |
| Memoria | 16 MB flash, 8 MB PSRAM Octal |
| Pantalla | ED047TC1, 4,7", 960×540, 16 grises, interfaz paralela de 8 bits |
| Controlador de pantalla | **ninguno**: el ESP32-S3 genera el timing (a diferencia del M5Paper, que usa IT8951) |
| Entrada | BtnA=GPIO4, BtnB=GPIO3, power por M5PM1 |
| Energía | M5PM1 (carga, rails, power button), batería 140 mAh |
| SD | SPI: SCLK39, MISO40, MOSI38, CS47 |
| Radio | Wi-Fi 2,4 GHz + BLE 5.0 |
| Sensores | ninguno (sin RTC, IMU, táctil, frontlight, audio) |

Pines del panel (idénticos al PaperS3):

```
D0..D7 = 6, 14, 7, 12, 9, 11, 8, 10
XCL/CL = 16   XLE/LE = 15   XSTL/SPH = 13
XOE/OE = 45   CKV = 18      SPV = 17      PWR = 46
PM1 GPIO2 = rail EPD adicional (I2C SDA41/SCL42)
```

## El repo de ejemplos: qué hay y qué falta

`melastmohican/m5paperdiy-arduino-examples` es una colección de sketches, no una
app. Lo relevante:

| Sketch | Estado | Comentario |
|---|---|---|
| `Button`, `Display`, `TextLogScroll`, `microSD`, `M5PM1` | funciona | Demos de periféricos |
| `FactoryTest` | funciona | Test de fábrica, refrescos, grises, Life |
| `PaperDIYUserDemo` | funciona | Demo ESP-IDF: batería, Wi-Fi, SD |
| `EpubReader` | funciona | Port de atomic14/diy-esp32-epub-reader |
| `FastEPD/animated_smiles` | **no funciona** | FastEPD no tiene definición para este panel |

`EpubReader` es un port a Arduino + M5Unified/M5GFX del lector de atomic14.
Tiene ~9.700 líneas incluyendo `Epub`, `miniz`, `tinyxml2` y el renderer, pero
la app en sí son ~170 líneas:

- lista de EPUB en la raíz de la SD, sin metadatos ni portadas;
- TOC (NCX y `nav` de EPUB3);
- fuente fija FreeSerif 12pt (solo latín);
- render en un `M5Canvas` de 8 bits y `epd_quality`/`epd_text` para página
  completa, `epd_fast` para áreas;
- controles: A clic = siguiente, A mantener = anterior, B clic = seleccionar;
- sin persistencia de posición, sin ajustes, sin Wi-Fi, sin diccionario, sin
  bookmarks, sin highlights, sin búsqueda, sin sueño profundo;
- `loop()` con `delay(20)` permanente y lectura de batería en cada interacción;
- SD a 20 MHz; sin caché de capítulos en SD.

Es una prueba de concepto útil para validar el panel, no una base para un
lector completo.

## Ecosistema de firmwares para e-readers ESP32

### CrossPoint Reader (Xteink X3/X4, M5Paper, PaperS3, PaperMono, LilyGo...)

Lo más maduro y lo más cercano a lo que queremos. En la rama 2.0.0 (develop,
28/10/2026) incluye:

- EPUB 2/3 con CSS, imágenes, hiphenación, kerning, tablas, ruby CJK, RTL,
  footnotes, navegación por capítulos;
- biblioteca indexada, portadas, recientes, búsqueda, navegador de carpetas;
- bookmarks, highlights/clippings, diccionario StarDict, ir a porcentaje,
  auto page turn, orientación, focus reading;
- KOReader Sync, Calibre wireless, OPDS con búsqueda y paginación, WebDAV,
  web UI, OTA;
- fuentes TTF/OTF en SD, temas, modo noche, sleep screens;
- XTC/XTCH, TXT, BMP;
- 35 idiomas de interfaz;
- BLE page turner (en desarrollo/según build), USB MSC en algunos modelos.

Arquitectura 2.0: `src/` (actividades/UI), `lib/` (Epub, GfxRenderer, EpdFont,
hal), `freeink-sdk` (BoardConfig, FreeInkDisplay, InputManager, PowerManager,
BatteryMonitor). El `BoardProfile` describe pines, pantalla y capacidades; los
drivers leen `BoardConfig::ACTIVE`. Eso es exactamente lo que hacía falta para
añadir PaperDIY sin tocar el lector.

### Papyrix (fork de CrossPoint)

Añade FB2, Markdown, HTML, detección de panel, temas y soporte de árabe/RTL.
Es la referencia para formatos adicionales. No tiene OTA (según su
documentación), lo que en un dispositivo con USB accesible no es crítico.

### CrossInk (fork de CrossPoint)

Enfoque UX: estadísticas de lectura, Bionic Reading, ajustes extra. Buenas
ideas para la fase de "lector rico".

### KOReader (Kobo, Kindle, Android...)

El estándar de funcionalidades: diccionarios, highlights/anotaciones, PDF/DjVu,
estadísticas, Calibre, OPDS, plugins, gestos, TTS en dispositivos con audio.
No es portable directamente al PaperDIY (Lua/Linux, pantalla táctil), pero marca
la lista de deseos: diccionario, estadísticas, exportar citas, búsqueda global,
sincronización.

### M5Paper / M5Paper S3

Hay ports de CrossPoint para M5Paper v1.1 y PaperS3. El de PaperS3 es el más
cercano en pantalla, pero usa la arquitectura 1.x y `EPD_Painter`, y está
pensado para táctil. Nuestro port usa la 2.0 y el driver `LgfxEpd` del SDK, que
ya soporta ED047TC1 en paralelo.

## Qué significa "rico en features" en este hardware

Fortalezas:

- pantalla grande y de 234 PPI, 16 grises: texto muy legible, portadas y
  imágenes decentes;
- 8 MB PSRAM: fuentes TTF, cachés, diccionarios;
- Wi-Fi/BLE: OPDS, Calibre, web UI, sync, OTA, page turner;
- SD: biblioteca grande, fuentes, diccionarios, cachés;
- USB: MSC, flasheo, logs.

Limitaciones que condicionan el diseño:

- **sin táctil**: la UI debe ser 100% navegable con 2 botones; los atajos y el
  remapeo son clave;
- **sin frontlight**: no hay lectura nocturna sin luz externa;
- **sin RTC**: la hora depende de NTP o del RTC interno tras dormir; habrá que
  mostrar "sin sincronizar" y permitir ajuste manual;
- **sin IMU/audio**: no hay tilt page turn ni TTS;
- **140 mAh**: la autonomía exige dormir entre interacciones y medir el consumo
  de los rails del PM1;
- **sin IT8951**: el timing y las waveform las genera el ESP32; hay que validar
  LUTs, rotación y ghosting en la placa real.

## Estrategia recomendada

1. **Portar CrossPoint 2.0** y validar el hardware (pantalla, botones, batería,
   SD, Wi-Fi, sueño).
2. **Adaptar la UX a 2 botones** y añadir BLE page turner como entrada
   secundaria.
3. **Añadir lo que diferencia al PaperDIY**: biblioteca/colecciones, stats,
   exportar highlights, diccionario español, OPDS de catálogos públicos,
   Calibre, web UI, fuentes, temas.
4. **Formatos**: FB2/Markdown/HTML (ideas de Papyrix), CBZ para cómics, y PDF
   mediante conversión en la web UI o en un companion, no PDF nativo.
5. **Mods de hardware opcionales**: batería mayor, RTC I²C, encoder rotativo o
   sensor Hall para la funda. No son necesarios para el MVP, pero cambian la
   experiencia.

## Riesgos

- **Panel**: LUTs/rotación/ghosting del ED047TC1 en PaperDIY no validados.
  Mitigación: probar `rotation=0/2`, `cleanBankNeedsFreshBackground`, LUTs del
  PaperS3/LilyGo, y medir tiempos de refresco.
- **Energía**: el PM1 puede dejar rails activos; el consumo en deep sleep hay
  que medirlo y cortar EPD/SD. Mitigación: `BoardPaperDiy::powerDownEpdPower()`
  y holds de GPIO.
- **Batería**: 140 mAh es muy justa; si no se duerme, la autonomía será de horas.
- **UI de 2 botones**: CrossPoint está pensado para 5 botones/táctil; hay que
  revisar todos los diálogos y el teclado en pantalla.
- **Flash**: la app ocupa 5,35 MB de 6,25 MB (81,6%). Añadir features exige
  optimizar, usar el build `slim` o ampliar la partición de app (hay 16 MB).
- **CrossPoint 2.0 es develop**: puede cambiar; conviene fijar el commit y
  mantener un patch de port.

## Fuentes principales

- M5Stack PaperDIY: <https://docs.m5stack.com/en/core/PaperDIY_Complete_Kit>
- M5Stack PaperDIY Arduino: <https://docs.m5stack.com/en/arduino/paperdiy/program>
- Repo de ejemplos: <https://github.com/melastmohican/m5paperdiy-arduino-examples>
- CrossPoint: <https://github.com/crosspoint-reader/crosspoint-reader>
- CrossPoint features: <https://crosspointreader.com/>
- Papyrix: <https://github.com/bigbag/papyrix-reader>
- CrossInk: <https://github.com/uxjulia/CrossInk>
- KOReader: <https://github.com/koreader/koreader>
- atomic14 EPUB reader: <https://github.com/atomic14/diy-esp32-epub-reader>
- M5Paper S3 port: <https://github.com/juicecultus/crosspoint-reader-papers3>
- M5Paper v1.1 port: <https://github.com/madaerodog/crosspoint-reader-m5paper>
- M5GFX: <https://github.com/m5stack/M5GFX>
- M5Unified: <https://github.com/m5stack/M5Unified>
- ED047TC1 datasheet: <https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/517/C139_ED047TC1_datasheet.pdf>
- Esquema PaperDIY: <https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1288/K159-B_PaperDIY_sche.pdf>
