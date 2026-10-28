# 03 — Matriz de funcionalidades

Leyenda: ✅ existe y se usa; 🟡 parcial o con matices; ❌ no existe; 🧪 está
compilado en este port pero **pendiente de validación en hardware**; N/A no
aplica al hardware.

| Funcionalidad | POC PaperDIY | CrossPoint 2.0 | Papyrix | KOReader | PaperDIY Reader |
|---|---|---|---|---|---|
| EPUB 2 | ✅ | ✅ | ✅ | ✅ | 🧪 |
| EPUB 3 (nav) | ✅ | ✅ | ✅ | ✅ | 🧪 |
| CSS (subconjunto) | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Imágenes en EPUB | 🟡 | ✅ | ✅ | ✅ | 🧪 |
| Hiphenación | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Kerning / layout fino | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Tablas / ruby CJK / RTL | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Footnotes | ❌ | ✅ | ✅ | ✅ | 🧪 |
| TOC / navegación capítulos | 🟡 | ✅ | ✅ | ✅ | 🧪 |
| Posición guardada | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Bookmarks | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Highlights / clippings | ❌ | ✅ | 🟡 | ✅ | 🧪 |
| Exportar citas | ❌ | 🟡 | ❌ | ✅ | 🟡 (roadmap) |
| Diccionario StarDict | ❌ | ✅ | ❌ | ✅ | 🧪 |
| Diccionario español | ❌ | ❌ | ❌ | ✅ | 🟡 (roadmap) |
| Búsqueda en libro | ❌ | ✅ | 🟡 | ✅ | 🧪 |
| Búsqueda en biblioteca | ❌ | ✅ | 🟡 | ✅ | 🧪 |
| Biblioteca indexada | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Portadas | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Colecciones / series / tags | ❌ | 🟡 | 🟡 | ✅ | 🟡 (roadmap) |
| Stats de lectura | ❌ | ❌ | ❌ | ✅ | 🟡 (roadmap) |
| Bionic / focus reading | ❌ | ✅ focus | 🟡 | 🟡 | 🧪 |
| Auto page turn | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Temas / modo noche | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Fuentes TTF/OTF en SD | ❌ | ✅ | ✅ | ✅ | 🧪 |
| 16 grises / AA | 🟡 | ✅ | ✅ | ✅ | 🧪 |
| FB2 | ❌ | ❌ | ✅ | ✅ | ❌ (roadmap) |
| Markdown | ❌ | ❌ | ✅ | 🟡 | ❌ (roadmap) |
| HTML | ❌ | ❌ | ✅ | 🟡 | ❌ (roadmap) |
| XTC/XTCH | ❌ | ✅ | ✅ | ❌ | 🧪 |
| TXT | ❌ | ✅ | ✅ | ✅ | 🧪 |
| BMP | ❌ | ✅ | ✅ | 🟡 | 🧪 |
| CBZ/CBR (cómics) | ❌ | ❌ | ❌ | 🟡 | ❌ (roadmap) |
| PDF nativo | ❌ | ❌ | ❌ | ✅ | ❌ (no prioritario) |
| PDF por conversión externa | ❌ | ❌ | ❌ | ❌ | 🟡 (roadmap) |
| OPDS | ❌ | ✅ | 🟡 | ✅ | 🧪 |
| Calibre wireless | ❌ | ✅ | 🟡 | ✅ | 🧪 |
| KOReader Sync | ❌ | ✅ | ❌ | ✅ | 🧪 |
| WebDAV | ❌ | ✅ | ❌ | 🟡 | 🧪 |
| Web UI | ❌ | ✅ | 🟡 | ❌ | 🧪 |
| OTA | ❌ | ✅ | ❌ | ✅ | 🧪 |
| BLE page turner | ❌ | 🟡 | ❌ | ❌ | 🧪 (activado) |
| USB MSC | ❌ | ✅ (algunos) | ❌ | ❌ | 🧪 (activado) |
| Deep sleep | ❌ | ✅ | ✅ | ✅ | 🧪 |
| Wake por botón | ❌ | ✅ | ✅ | ✅ | 🧪 (A/B) |
| Wi-Fi | ❌ | ✅ | ✅ | ✅ | 🧪 |
| 35 idiomas UI | ❌ | ✅ | 🟡 | ✅ | 🧪 (español) |
| Táctil | N/A | ✅ | ✅ | ✅ | N/A |
| Frontlight | N/A | ✅ | ✅ | ✅ | N/A |
| RTC | N/A | ✅ | ✅ | ✅ | ❌ (NTP) |
| IMU / tilt | N/A | ✅ | ❌ | 🟡 | N/A |
| Audio / TTS | N/A | ❌ | ❌ | ✅ | N/A |

## Lectura de la tabla

- El POC solo cubre lectura básica; no es una base para "rico en features".
- CrossPoint 2.0 cubre casi todo lo que no depende de hardware ausente.
- Papyrix es la referencia para formatos (FB2/MD/HTML) y RTL/CJK.
- KOReader es la referencia para diccionario, stats, highlights y PDF; no es
  portable tal cual.
- El port PaperDIY hereda CrossPoint y añade BLE page turner + USB MSC; todo
  está compilado, pero la validación en hardware está pendiente.

## Prioridades para el PaperDIY

1. **Validar** lo que ya compila (pantalla, botones, batería, SD, Wi-Fi,
   sleep).
2. **Pulir UX de 2 botones** (la mayor fricción).
3. **Biblioteca + colecciones + stats + exportar citas** (lo que hace que se
   use a diario).
4. **Diccionario español + búsqueda**.
5. **OPDS/Calibre/web UI** (ecosistema).
6. **Formatos**: FB2/MD/HTML y CBZ; PDF solo por conversión.
7. **Mods**: batería, RTC, encoder/funda.
