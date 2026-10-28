# 02 — Estado actual y análisis del ecosistema

## 1. El POC del repo de ejemplos

`EpubReader/EpubReader.ino` es un port de
[atomic14/diy-esp32-epub-reader](https://github.com/atomic14/diy-esp32-epub-reader)
a Arduino + M5Unified/M5GFX. La estructura:

```
EpubReader/
├── EpubReader.ino              # app, ~170 líneas
└── src/
    ├── Epub/                   # parser EPUB, zip, HTML, layout
    ├── miniz/                  # inflate
    ├── tinyxml2/               # XML
    └── M5GfxRenderer.h         # renderer M5GFX
```

### Lo que hace bien

- Valida el panel y los botones.
- Lee EPUB 2/3, TOC (NCX y `nav`), texto e imágenes.
- Renderiza en un `M5Canvas` de 8 bits y usa `epd_quality`/`epd_text` para
  página completa y `epd_fast` para áreas.
- Es compacto y fácil de entender.

### Lo que le falta para ser un lector

| Área | Estado |
|---|---|
| Persistencia de posición | ❌ no guarda |
| Biblioteca/metadatos/portadas | ❌ solo lista de archivos |
| Ajustes de fuente/tamaño/márgenes | ❌ fuente fija FreeSerif 12pt |
| CSS/layout real | 🟡 parser limitado, sin CSS |
| Búsqueda, bookmarks, highlights | ❌ |
| Diccionario | ❌ |
| Wi-Fi / OPDS / Calibre / sync | ❌ |
| Web UI / OTA | ❌ |
| Sueño profundo / gestión de energía | ❌ `loop()` permanente |
| Refresco parcial inteligente | 🟡 solo `flush_area` |
| Caché de capítulos en SD | ❌ |
| Fuentes TTF/OTF | ❌ solo fuentes M5GFX |
| Tests / CI | ❌ |
| Licencia clara | 🟡 mezcla de terceros |

Además, el repo es una **colección de sketches**, no una aplicación; el
`FastEPD` no funciona con este panel y el `EpubReader` no tiene una arquitectura
pensada para crecer.

## 2. CrossPoint Reader 2.0

Es el firmware custom de referencia para Xteink. En la rama `develop`
(2.0.0, commit `31dc683`, 28/10/2026):

### Motor de lectura

- EPUB 2/3, `nav` y NCX, CSS, imágenes, tablas, ruby CJK, RTL.
- Hiphenación, kerning, `text-indent`, márgenes, `pre`, footnotes.
- Fuentes bitmap comprimidas + TTF/OTF en SD (FreeType).
- Caché de secciones y metadatos en `/.crosspoint/`.
- Bookmarks, highlights/clippings, diccionario StarDict, focus reading,
  auto page turn, ir a porcentaje, orientación.

### Biblioteca y UI

- Índice de títulos/autores, portadas, recientes, orden alfabético, búsqueda,
  navegador de carpetas, caché de portadas.
- Temas (Classic, Lyra, Lyra Extended, RoundedRaff), modo noche, status bar,
  sleep screens, screenshots.
- 35 idiomas, incluido español.

### Red y sync

- Web UI para subir libros, gestionar archivos y ajustes.
- WebDAV, AP/STA con QR, Calibre wireless, OPDS con búsqueda y paginación,
  KOReader Sync, OTA desde GitHub.
- Optimizador de EPUB.

### Formatos

- `.epub`, `.xtc/.xtch`, `.txt`, `.bmp`.
- No PDF nativo; no FB2/Markdown/HTML (eso lo añade Papyrix).

### Hardware

- Perfiles para Xteink X3/X4/X4 Pro/X4 Classic, M5Paper v1.1, M5Paper S3,
  PaperMono, PaperColor, LilyGo T5 S3, Sticky, EEGO A4, OnePage, Picco, etc.
- `BoardConfig` describe pines, pantalla, botones, batería, touch, frontlight,
  RTC, IMU, audio, SD, etc.
- `FreeInkDisplay` selecciona driver (SSD1677, UC8253, UC8279, IT8951, LgfxEpd,
  PaperMono...).
- `InputManager`, `PowerManager`, `BatteryMonitor` leen el perfil activo.

## 3. Papyrix, CrossInk y KOReader: qué copiar

### Papyrix

- FB2 con metadatos/TOC; Markdown; HTML; XTC.
- Detección automática de panel.
- Soporte árabe/RTL y CJK.
- Temas y fuentes.
- **Idea**: añadir FB2/Markdown/HTML y un parser de Markdown ligero; no
  necesitamos PDF nativo.

### CrossInk

- Estadísticas de lectura (sesiones, páginas/minuto).
- Bionic Reading.
- Ajustes de UX.
- **Idea**: base de datos de sesiones en SD + pantalla de stats; exportar a
  Markdown/CSV.

### KOReader

- Diccionarios, highlights/anotaciones, búsqueda global, estadísticas,
  Calibre, OPDS, plugins, PDF/DjVu, TTS.
- **Idea**: el estándar de "lector rico"; copiar la organización de
  highlights y la exportación de citas, no el código (Lua/Linux).

## 4. Qué aporta el PaperDIY y qué no

### A favor

- Pantalla grande (960×540) y 234 PPI: texto excelente.
- 16 grises: portadas, imágenes y AA de calidad.
- 8 MB PSRAM: fuentes TTF, cachés, diccionarios.
- Wi-Fi/BLE: OPDS, Calibre, web UI, sync, page turner.
- SD: biblioteca grande, fuentes, diccionarios.
- USB: MSC, flasheo, recuperación.
- 16 MB flash: margen para features (aunque la app ya usa 81,6%).

### En contra

- Sin táctil: la UI debe ser operable con 2 botones.
- Sin frontlight: no hay lectura a oscuras.
- Sin RTC: hora por NTP o RTC interno; no hay alarma fiable.
- Sin IMU: no hay tilt page turn.
- Sin audio: no hay TTS/audiolibros.
- 140 mAh: autonomía muy limitada si no se duerme.
- Sin IT8951: el ESP32 genera el timing; hay que validar LUTs/ghosting.
- CrossPoint 2.0 es develop, no una release estable.

## 5. Conclusión

El POC sirve para aprender y para validar el panel, pero no para llegar a un
lector completo. CrossPoint 2.0 aporta el 90% del software; el PaperDIY aporta
el hardware. El trabajo real es la capa de placa y la UX de dos botones. Eso es
lo que hace este repo.
