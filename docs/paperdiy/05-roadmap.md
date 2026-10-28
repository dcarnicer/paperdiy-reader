# 05 — Roadmap

El orden no es arbitrario: primero se valida el hardware, luego se pule la UX
mínima y después se añaden features. Sin la fase 0, cualquier feature es una
hipótesis.

## Fase 0 — Validación en hardware (prioridad máxima)

Objetivo: demostrar que el port funciona en un PaperDIY real y recoger datos.

- [x] Flashear `firmware.factory.bin` (28/10/2026; sin backup, a petición).
- [x] Confirmar que el panel enciende y muestra el splash/UI.
- [x] Rotación/orientación: UI correcta en vertical, sin cambios.
- [ ] Medir tiempos de refresco: `epd_quality`, `epd_text`, `epd_fast`,
      `epd_fastest`; página completa vs área.
- [ ] Evaluar ghosting general y si hace falta `cleanBankNeedsFreshBackground`
      o LUTs propias (comparar con PaperS3/LilyGo).
- [x] Ghosting al abrir el menú del lector: corregido con `HALF_REFRESH` en la
      primera pintada; verificado en hardware.
- [ ] Probar A/B: navegación, página, back, confirm, A+B. Cortos ya funcionan;
      largos y A+B pendientes.
- [x] Batería: lectura al 100 %. Pendiente carga, VBAT y USB presente.
- [x] SD: monta tras reiniciar, aparecen `Books/*.epub`, abre y lee.
- [ ] Libro grande / caché / cambios de fuente.
- [ ] Probar Wi-Fi: web UI, OPDS, Calibre, OTA.
- [ ] Medir consumo: activo, idle, deep sleep; autonomía estimada.
- [ ] Medir tiempo de wake y comprobar que el botón que despierta no pasa
      página accidentalmente.
- [ ] Probar recuperación: entrar en download mode y reflashear.

**Criterio de salida:** se puede leer un EPUB completo, dormir/despertar, y la
autonomía es al menos "unas horas de lectura" con una carga.

## Fase 1 — Port pulido y UX de 2 botones

- [ ] Ajustar el perfil según la fase 0 (rotación, LUTs, PM1, timeout).
- [ ] Revisar todos los diálogos/actividades para que sean operables con
      A/B/largos; eliminar dependencias de táctil.
- [ ] Remapeo de botones y atajos contextuales.
- [ ] Pantalla de ajustes rápida (fuente, tamaño, tema, refresco).
- [ ] Español como idioma por defecto (o detectar/es-ES).
- [ ] Arreglar el wake para que el primer press no haga page turn.
- [ ] Auto-sleep agresivo + sleep screen con portada.
- [ ] Documentación de usuario y troubleshooting.
- [ ] CI que compile `paperdiy` y publique artefactos.

**Criterio de salida:** un usuario puede instalar, leer, ajustar y dormir sin
tocar un cable ni leer documentación técnica.

## Fase 2 — Lector rico

- [ ] Biblioteca con colecciones/series/tags/estado (leyendo/leído/pendiente).
- [ ] Estadísticas: sesiones, tiempo, páginas/minuto, racha; almacenamiento en
      SD y pantalla de stats.
- [ ] Exportar highlights/citas a Markdown/CSV; integración con Obsidian.
- [ ] Diccionario español (StarDict) + gestor de diccionarios; historial.
- [ ] Búsqueda global de biblioteca y dentro del libro con índice en SD.
- [ ] OPDS con catálogos curados (Project Gutenberg, Standard Ebooks,
      Wikisource, Internet Archive).
- [ ] Calibre wireless + web UI para gestionar metadatos/portadas.
- [ ] BLE page turner probado con mandos/media buttons.
- [ ] USB MSC probado (exponer SD).
- [ ] Screenshots y sleep screens personalizables.

**Criterio de salida:** el PaperDIY compite con un Kindle básico en lectura,
aunque sin táctil/frontlight.

## Fase 3 — Formatos y flujos

- [ ] FB2 (metadatos, TOC, texto; sin imágenes inline al principio).
- [ ] Markdown y HTML (parser ligero, streaming).
- [ ] CBZ/CBR para cómics (imágenes + zoom por botones).
- [ ] PDF: flujo de conversión en web UI/companion a EPUB o imágenes
      pre-renderizadas; no PDF nativo.
- [ ] RSS/Atom, Pocket, Wallabag, Instapaper (descarga a EPUB/HTML).
- [ ] Traducción online opcional (LibreTranslate/DeepL) y offline básica.
- [ ] Sync propio/WebDAV además de KOReader.
- [ ] "Send to PaperDIY" (email/servicio) si hay demanda.

## Fase 4 — Hardware y comunidad

- [ ] Mod de batería mayor documentado (celda, espacio, carga).
- [ ] RTC I²C opcional (DS3231/PCF8563) con alarmas.
- [ ] Encoder rotativo / 5-way / funda con sensor Hall.
- [ ] Frontlight: clip externo documentado; no integrado.
- [ ] Releases con `firmware.factory.bin` y web flasher.
- [ ] Upstream del soporte PaperDIY a CrossPoint (PR).
- [ ] Guía de contribución, tests host y banco de pruebas.

## Matriz impacto/esfuerzo

| Feature | Impacto | Esfuerzo | Fase |
|---|---|---|---|
| Validar pantalla/energía | Alto | Medio | 0 |
| UX 2 botones | Alto | Medio | 1 |
| Auto-sleep + wake limpio | Alto | Bajo | 1 |
| Biblioteca/colecciones | Alto | Medio | 2 |
| Stats + exportar citas | Medio | Medio | 2 |
| Diccionario español | Alto | Bajo/Medio | 2 |
| OPDS/Calibre/web UI | Alto | Bajo (heredado) | 2 |
| BLE page turner | Alto | Bajo (heredado) | 2 |
| FB2/MD/HTML | Medio | Alto | 3 |
| CBZ | Medio | Medio | 3 |
| PDF conversión | Medio | Alto | 3 |
| Batería mayor | Alto | Bajo (hardware) | 4 |
| RTC/encoder/Hall | Medio | Medio | 4 |

## No objetivos (por ahora)

- PDF nativo con reflow: demasiado para el ESP32-S3 y el tamaño de pantalla.
- TTS/audiolibros: no hay audio; requeriría hardware.
- Color: el panel es monocromo.
- DRM/Adobe ACSM: fuera de alcance.
- Táctil: no hay panel táctil; no se puede simular.
- Frontlight integrado: no hay LED/rail; solo clip externo.
