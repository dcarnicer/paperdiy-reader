# 05 — Roadmap

El orden no es arbitrario: primero se valida el hardware, luego se pule la UX
mínima y después se añaden features. Sin la fase 0, cualquier feature es una
hipótesis.

## Fase 0 — Validación en hardware (prioridad máxima)

Objetivo: demostrar que el port funciona en un PaperDIY real y recoger datos.

- [x] Flashear `firmware.factory.bin` (28/10/2026; sin backup, a petición).
- [x] Confirmar que el panel enciende y muestra el splash/UI.
- [x] Rotación/orientación: UI correcta en vertical, sin cambios.
- [x] Medir tiempos de refresco: `epd_fast`, `epd_text` y `epd_quality`
      (06/11). Página completa: `fast` 569–620 ms de display (total 651–726 ms),
      `text` limpio 1538–1542 ms (total 1637–1651 ms). `quality` no lo usa el
      port; con un mapeo temporal midió 1538 ms, igual que `text`. Prewarm
      38–58 ms y render B/W 49–59 ms. `epd_fastest` no se usa en la lectura.
- [x] Evaluar ghosting general en tanda corta: sin ghosting apreciable tras
      24 páginas con refresco cada 5 (05/11).
- [x] Lectura muy larga funcional: 250+ cambios de página y varios capítulos sin
      reinicios, errores ni fugas de heap/PSRAM (06/11).
- [x] Revisión visual física del ghosting tras la lectura larga: leve con
      refresco cada 5 páginas (06/11); las capturas por serial son el
      framebuffer, no el estado del panel. Valorar bajar a 1 página o añadir
      un paso intermedio.
- [x] Ghosting al abrir el menú del lector: corregido con `HALF_REFRESH` en la
      primera pintada; verificado en hardware.
- [x] Ghosting al pasar páginas: default 15 -> 5 y prueba de LUT AA de
      ED047TC1 (LilyGo T5 S3) en `fast`/`fastest`; validar en lectura
      prolongada. `cleanBankNeedsFreshBackground` se probó y se revirtió.
- [x] Probar A/B: navegación, página, back, confirm y A+B. Cortos y atajos
      back/confirm verificados; A+B con USB apaga vía PM1 (05/11). Falta
      validar la pulsación larga física sostenida.
- [x] Batería: curva PaperDIY (4,10 V = 100 %), LVP a 3,4 V, `About` con
      VBAT/estado de carga y rayo según `CHG_STAT`. Pendiente validar la nueva
      604050 y medir autonomía.
- [x] SD: monta tras reiniciar, aparecen `Books/*.epub`, abre y lee.
- [x] Libro grande / caché / cambios de fuente: EPUB de 7,3 MB y cambio de
      tamaño 14/16 pt con reflow verificados.
- [x] Wi-Fi + web UI + transferencia de archivos.
- [x] OPDS (Project Gutenberg), Calibre wireless y OTA.
- [x] KOReader Sync con credenciales: validado contra un servidor KOSync local
      (auth, pull, push y aplicación de progreso remoto, 06/11). Falta probar
      un servidor oficial/remoto si se usa en producción.
- [ ] Medir consumo: activo, idle, deep sleep; autonomía estimada.
- [ ] Medir tiempo de wake y comprobar que el botón que despierta no pasa
      página accidentalmente. Power despierta y conserva la página; A+B con
      USB apagó vía PM1 y A no despertó (05/11).
- [ ] Probar recuperación: entrar en download mode y reflashear.

**Criterio de salida:** se puede leer un EPUB completo, dormir/despertar, y la
autonomía es al menos "unas horas de lectura" con una carga.

## Fase 1 — Port pulido y UX de 2 botones

- [x] Refresco parcial de diálogos con `GfxRenderer::displayWindow` +
      `Panel_EPD::display(x, y, w, h)`: `OptionPopup` refresca solo el diálogo
      y la tira de botones; activo en Settings, File Browser, Library y el menú
      del lector. Verificado en hardware.
- [ ] Refresco parcial de barra de estado/batería (siguiente iteración).
- [x] Detección de tarjeta SD por GPIO48 (`CARD_DET`, activo bajo): espera de
      inserción al arrancar y re-mount al insertar en caliente. Verificado en
      hardware + host test.
- [x] Aviso y recuperación si se quita la SD durante la lectura: “Insert SD
      card” y, al reinsertar, reinicio + montaje + Home. Verificado en hardware
      (04/11/2026).
- [ ] Ajustar el perfil según la fase 0 (rotación, LUTs, PM1, timeout).
- [ ] Revisar todos los diálogos/actividades para que sean operables con
      A/B/largos; eliminar dependencias de táctil.
- [ ] Remapeo de botones y atajos contextuales.
- [ ] Pantalla de ajustes rápida (fuente, tamaño, tema, refresco).
- [ ] Español como idioma por defecto (o detectar/es-ES).
- [ ] Arreglar el wake para que el primer press no haga page turn. Power
      despertó sin cambiar de página (05/11); falta el deep sleep con wake A/B.
- [x] Auto-sleep + sleep screen con portada: auto suspensión a 1 min, `Fondo
      = Portada` + `Modo = Ajustar`, power despierta y conserva la página
      (05/11).
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
      Wikisource, Internet Archive). Project Gutenberg ya validado
      (navegación, descarga y lectura); Standard Ebooks devuelve 401 y
      requiere credenciales.
- [x] Calibre wireless + web UI para transferencia; gestión de metadatos y
      portadas pendiente.
- [ ] BLE page turner probado con mandos/media buttons. El escaneo BLE
      funciona; el Keychron Q1 Pro es Bluetooth Classic (no vale para el
      ESP32-S3) y el teclado HID BLE emulado desde macOS se ve pero falla al
      emparejar. Falta un mando BLE real.
- [x] USB MSC probado (exponer SD).
- [ ] OTA bajo M5Launcher vía catálogo: `Verificar actualizaciones` consulta
      LauncherHub (app `CrossPoint for PaperDIY (community port)`, publicada en
      M5Burner) y manda a `M5Launcher > OTA`; el lector no escribe en la flash.
      Falta: aprobación en M5Burner, probar el aviso con la app ya publicada y
      comprobar en hardware si actualizar desde Launcher reemplaza la app o
      crea un duplicado (`paper1`). Ver `13-m5launcher.md`.
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
| OTA bajo Launcher | Alto | Alto | 2 |
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
