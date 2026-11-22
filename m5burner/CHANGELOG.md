# Changelog de M5Burner

Última publicación registrada en este repositorio: **2.0.0-10** (subida
confirmada por el usuario el 22/11/2026). La entrada **2.0.0-11** documenta sus
cambios y el texto preparado para el diálogo Publish; actualiza esta línea
cuando el catálogo la muestre.
La subida es manual: confirma el catálogo y actualiza esta línea solo después
de publicar.

## Short description for M5Burner (EN)

## CrossPoint for PaperDIY 2.0.0-11

Synced with CrossPoint `177d0694` and FreeInk SDK `995d9bd5`. Update from
2.0.0-10.

### New

- **Sync On Sleep** (optional, off by default): when you put the reader to
  sleep from an EPUB, it joins a saved Wi-Fi network in range (battery at
  least 20%) and syncs that book: position, bookmarks, reading sessions and,
  if enabled, clippings.
- Manual **Sync Progress** also syncs bookmarks and uploads reading sessions
  on servers that support it (CrossPoint Sync).
- Indic script support without HarfBuzz (Devanagari, Bengali, Tamil, Sinhala
  and more).
- Reading progress on the Lyra theme.
- Web UI: browse installed plugins.

### Improvements and fixes

- Clock and battery placement normalized across the built-in themes.
- The file browser popup shows the selected file name.
- Renaming a file in the web UI keeps its extension.
- The sleep image is cleared when the device replaces it.
- Clipping handles are no longer hidden at the top edge of the screen.
- Safer SD file reads: oversized files are rejected instead of truncated.
- Spanish, Catalan and Valencian translations for Sync On Sleep.

### PaperDIY

- Port reapplied on the new upstream. The sleep Wi-Fi battery check uses the
  PaperDIY battery reading, and the reader menu still clears the page
  underneath.
- Full hardware smoke test passed (25 steps).

### Known limitations

- Sync On Sleep has not been tried against a real server yet.
- Still pending: real BLE remote pairing, full Calibre transfer, full OTA
  install, sleep/wake, idle current, autonomy and the visual ghosting review.

### License

GPLv3: the combined firmware includes wolfSSL. The source code is MIT. Source
code, license texts and third-party notices (`LICENSE`):
https://github.com/dcarnicer/paperdiy-reader/releases/tag/v2.0.0-11

## Full changelog (EN)

### 2.0.0-11 — 2026-11-22

Synced with CrossPoint `177d0694` and FreeInk SDK `995d9bd5`.

- Upstream: Sync On Sleep (optional, off by default), reading-session and
  bookmark sync with CrossPoint Sync servers, Indic script support without
  HarfBuzz, clock and battery placement normalized across built-in themes,
  reading progress on Lyra, WebUI plugin navigation, selected file name in the
  file-browser popup, web rename keeps the extension, sleep image cleared when
  replaced, and clipping and BMP fixes.
- SDK: new Seeed reTerminal E1001 board, size-checked SD file reads, and dark
  mode and UC8279C A4 refresh improvements. No PaperDIY behaviour change
  expected.
- PaperDIY port reapplied. The new sleep-WiFi battery check uses the PaperDIY
  battery presentation, and the reader menu still scrubs the page underneath
  with a cleanup refresh.
- Spanish, Catalan and Valencian translations for Sync On Sleep.
- Patches regenerated against the new pins and verified with `git apply
  --check`. Build 5,528,960 B (84.3% flash, 34.1% RAM). Full `make smoke`
  passed on this tree (25 steps, run `20261122-193337`).

### 2.0.0-10 — 2026-11-19

Synced with CrossPoint `209cb53a` and FreeInk SDK `634a3f8c`.

- Upstream: full-tone image rendering on EEGO/Picco, KOReader Sync preserved
  while Bluetooth shuts down, auto-sleep no longer counts blocked activity, and
  dead-code cleanup.
- SDK: faster refresh after Gray3, grayscale overlay, SSD2677/UC8279C A4 LUT
  and driver updates, and Picco power-pin hold/release ordering.
- PaperDIY port reapplied; `HalStorage`, `AboutActivity` and `OtaUpdater`
  conflicts resolved while keeping the fork additions.
- Patches regenerated against the new pins and verified with `git apply
  --check`. Build 5.446.032 B (83,0% flash, 33,9% RAM). Full `make smoke`
  passed on this tree (25 steps, run `20261119-120845`).

### 2.0.0-9 — 2026-11-18

Synced with CrossPoint `b6b7a6c1` and FreeInk SDK `77ae8c75`.

- Upstream: dictionary page side buttons, font caches released after chapter
  builds, Recent opened-only option, OPDS redirect error message, EEGO A4
  auto-sleep/UID, Picco app-only upload and branch+hash versions.
- PaperDIY port reapplied; `cleanNextRefresh`, the About row count and the
  A+B chord suppression resolved against the new upstream code.
- PM1: shared I²C lock, one-time bus setup and a `BATTERY_POLL_MS` status cache
  prevent interleaved button/battery access from the loop and render tasks.
- `Display Refresh` removed from Settings; guides point to `Refresh Screen`
  under Controls > Power button > Short click and to `Refresh Frequency`.
- Spanish/Catalan/Valencian translations for the new Recent strings; CA/VA
  recovery hint now names `-ota.bin`.
- Build 5,446,272 B (83.0% flash, 33.9% RAM); 935 host tests, `paperdiy-test`
  build and 25-step hardware smoke passed (`20261118-132153`).

### 2.0.0-8 — 2026-11-16

Synced with CrossPoint `490813ff` and FreeInk SDK `3f3e4c1`.

- Upstream: power-button gesture disambiguation across soft restarts, misc
  reader/Home/WebDAV/font-download/web-server fixes, and CI flash/RAM stats.
- PaperDIY port reapplied over the new SDK; the PM1 pulse is normalized as a
  click (duration 0) and the wake click is not replayed to the app.
- Battery profile changes apply live from the UI and web, without a reboot,
  and persist in `settings.json` with validation and a kit fallback.
- Spanish `Display Refresh` translation.
- Build 5,445,184 B (83.0% flash, 33.9% RAM); 18 Python tests, 933 host tests,
  PaperDIY PMIC test and 25-step hardware smoke passed.
- Hardware: wake-click after A+B, SD hot-plug, profile persistence and the web
  change validated. Pending: visual battery-curve jump below ~90% and autonomy.

### 2.0.0-7 — 2026-11-15

Battery display fix on top of `2.0.0-6`. No upstream changes: still CrossPoint
`36b9430e` / FreeInk SDK `a8acebf`.

- The PM1 has no coulomb counter and charging voltage is not a usable state of
  charge. While USB is connected, the percentage stays at the last discharge
  value; it shows 100% when charging completes.
- After unplugging, the last value is held for about two minutes while the cell
  relaxes, then the discharge curve resumes.
- The last discharge percentage is stored in NVS, so it survives power-off and
  a boot while charging.
- The `BATHOLD` hook exists only in `paperdiy-test`, to exercise the hold path.
- Build 5,438,679 B (83.0% flash, 33.9% RAM); battery tests 5/5.
- Not covered: full `make smoke` and the deferred ghosting/sleep-wake review.

### 2.0.0-6 — 2026-11-15

Synced with CrossPoint `36b9430e` and FreeInk SDK `a8acebf`.

- EPD refresh improvements for all panels, TTF optimizations, XTC bit depth,
  previous-page chevron, and the earlier controls web grouping / `OptionPopup`
  scroll fixes.
- PaperDIY port reapplied over the new SDK; PSRAM policy and `GfxRenderer`
  refresh-window conflicts resolved.
- Battery: discharge log at `/battery-log.csv` (5-minute samples, 1 MB
  rotation), `CMD:BATLOG` serial dump, autonomous page-turn test mode, and a
  measured 1500 mAh 604050 curve (45.4 h / 5,448 pages; 4.10 V at rest = 100%).
- New **Settings > System > Battery profile**: Original kit (140 mAh) or
  Extended (1500 mAh). It only changes the percentage curve, not charging.
- PM1 battery reads serialized through the HAL and `About`.
- Build 5,438,295 B (83.0% flash, 33.9% RAM); battery tests 5/5.
- Basic hardware smoke passed (Home, reader, page turn, settings and the
  Extended battery profile), not the full `make smoke`. Ghosting visual review
  and sleep/wake remain pending.

### 2.0.0-5 — 2026-11-12

Maintenance release; no functional firmware changes.

- Fixed the license test for the vendored SDK and preserved it in the sync.
- Host tests 922/922; Python tests 15/15.
- Same firmware as `2.0.0-4` except for the version string.

### 2.0.0-4 — 2026-11-12

Synced with CrossPoint `fa17b9ca` (16 commits).

- **Controls** reorganized into submenus: Power button, Front buttons, Side
  buttons and Taps & gestures.
- **OPDS** moved to `File Transfer → OPDS Browser`; manage servers in
  `Settings → Connectivity → OPDS Servers`. It also appears on Home when the
  plugin system is off and a server is already saved.
- New **Show File Extensions** setting.
- **Reader**: bottom margin preserved with the progress bar, page counter on
  the last page, no hyphenation in headings, TTF advance rounding and PageLink
  reset to zero.
- **Stability**: screenshot rotation, plugin tokens after failed writes,
  WebDAV credentials, Basic auth in clipping sync, Hebrew/Arabic dictionary
  lookup and Home cover cache.
- Spanish translations and user-guide updates for the new paths.
- Build 5,432,192 B (82.8% flash, 33.9% RAM); 922/922 host tests; 25-step
  hardware smoke.

### 2.0.0-3 — 2026-11-10

Synced with CrossPoint `8276d518` (3 commits) and FreeInk SDK `6a208c0c`.

- Home renders the cover grid in a single refresh with a warm cache.
- TLS requests 2 KB records again, with a 16 KB fallback.
- SecureNet discards oversized `Content-Security-Policy` headers from GitHub
  instead of failing.
- SDK update for font downloads.
- Added `make smoke`: deterministic regression with EPUB/StarDict fixtures,
  OCR assertions, backup/restore and `--restore-hold`.
- Validated: boot, Home, A/B, reader with 9 page turns, OTA with no updates,
  font catalog and download/install, orientation, OPDS download/delete, USB
  MSC, BLE enable/scan and Calibre wireless server.
- Build 5,428,032 B (82.7% flash, 33.9% RAM); 914/914 host tests.

## Known limitations

- Real BLE remote pairing has not been validated.
- A full Calibre transfer and a full OTA update have not been repeated.
- Sleep/wake, idle current and the visual ghosting review are still pending
  (default fast refresh every 5 pages). The 604050 extended cell was measured
  in a drain test (45.4 h / 5,448 pages), but both battery curves still need
  validation in normal reading. The original 140 mAh kit cell keeps its
  original curve.
- Sync On Sleep has not been tried against a real CrossPoint Sync server.
- The latest full `make smoke` passed on the `177d0694` tree (25 steps, run
  `20261122-193337`); `2.0.0-11` only bumps the version and adds translations.
  The visual battery-curve jump still needs a battery below ~90%.

## Changelog completo (ES)

### 2.0.0-11 — 2026-11-22

Sincronización con CrossPoint `177d0694` y FreeInk SDK `995d9bd5`.

- Upstream: Sync On Sleep (opcional, desactivado por defecto), sincronización
  de sesiones de lectura y marcadores con servidores CrossPoint Sync, soporte
  de escrituras índicas sin HarfBuzz, reloj y batería normalizados en los temas,
  progreso de lectura en Lyra, navegación de plugins en la WebUI, nombre del
  fichero en el popup del explorador, renombrar en la web conserva la
  extensión, la imagen de sleep se limpia al sustituirla y fixes de recortes y
  BMP.
- SDK: nueva placa Seeed reTerminal E1001, lectura de la SD con límite de
  tamaño y mejoras de refresco en modo oscuro y UC8279C A4. Sin cambios
  previstos en PaperDIY.
- Port PaperDIY reaplicado. La comprobación de batería del Wi-Fi al dormir usa
  la presentación de batería de PaperDIY y el menú del lector sigue limpiando
  la página de debajo con un refresco de limpieza.
- Traducciones ES/CA/VA de Sync On Sleep.
- Parches regenerados contra los pines nuevos y verificados con `git apply
  --check`. Build 5.528.960 B (84,3 % flash, 34,1 % RAM). `make smoke`
  completo sobre este árbol (25 pasos, run `20261122-193337`).

### 2.0.0-10 — 2026-11-19

Sincronización con CrossPoint `209cb53a` y FreeInk SDK `634a3f8c`.

- Upstream: render full-tone de imágenes en EEGO/Picco, KOReader Sync
  conservado al apagar Bluetooth, auto-sleep sin contar tiempo bloqueado y
  limpieza de código muerto.
- SDK: refresco más rápido tras Gray3, overlay de grises, LUTs/drivers
  SSD2677 y UC8279C A4 y orden hold/release de pines en Picco.
- Port PaperDIY reaplicado; conflictos de `HalStorage`, `AboutActivity` y
  `OtaUpdater` resueltos conservando las adiciones del fork.
- Parches regenerados contra los pines nuevos y verificados con `git apply
  --check`. Build 5.446.032 B (83,0 % flash, 33,9 % RAM). `make smoke`
  completo sobre este árbol (25 pasos, run `20261119-120845`).

### 2.0.0-8 — 2026-11-16

Sincronización con CrossPoint `490813ff` y FreeInk SDK `3f3e4c1`.

- Upstream: desambiguación de gestos del botón power en reinicios suaves,
  arreglos varios de lector, Home, WebDAV, descarga de fuentes y servidor web,
  y stats de flash/RAM en CI.
- Port de PaperDIY reaplicado sobre el SDK nuevo; el pulso del PM1 se normaliza
  como click (duración 0) y el click que despierta no se reenvía a la app.
- El perfil de batería se aplica en caliente desde la UI y la web, sin
  reinicio, y persiste en `settings.json` con validación y fallback al kit.
- Traducción española de `Display Refresh`.
- Build 5.445.184 B (83,0 % flash, 33,9 % RAM); 18 tests Python, 933 host, test
  PMIC PaperDIY y smoke de hardware de 25 pasos.
- Hardware: wake-click tras A+B, SD en caliente, persistencia del perfil y
  cambio web validados. Pendiente: salto visual de la curva con batería <90 %
  y autonomía.

### 2.0.0-7 — 2026-11-15

Corrección de la presentación de batería sobre `2.0.0-6`. Sin cambios upstream:
sigue CrossPoint `36b9430e` / FreeInk SDK `a8acebf`.

- El PM1 no tiene coulomb counter y la tensión de carga no sirve para estimar
  el estado de carga. Mientras hay USB, el porcentaje se queda en el último
  valor de descarga; al completar la carga muestra 100 %.
- Tras desenchufar, mantiene el último valor unos 2 min mientras la celda se
  relaja y después vuelve a la curva de descarga.
- El último porcentaje de descarga se guarda en NVS, así que sobrevive al
  apagado y a un arranque mientras carga.
- El hook `BATHOLD` solo existe en `paperdiy-test`, para probar la retención.
- Build 5.438.679 B (83,0 % flash, 33,9 % RAM); tests de batería 5/5.
- No cubierto: `make smoke` completo ni la revisión diferida de ghosting y
  sleep/wake.

### 2.0.0-6 — 2026-11-15

Sincronización con CrossPoint `36b9430e` y FreeInk SDK `a8acebf`.

- Mejoras de refresco EPD para todos los paneles, optimizaciones TTF,
  profundidad de bits XTC, chevron de página anterior y los fixes anteriores de
  Controles agrupados en la web y scroll de `OptionPopup`.
- Port de PaperDIY reaplicado sobre el SDK nuevo; conflictos resueltos en la
  política PSRAM y en las ventanas de refresco de `GfxRenderer`.
- Batería: log de descarga en `/battery-log.csv` (muestra cada 5 min, rotación
  a 1 MB), descarga por serie con `CMD:BATLOG`, modo de page-turning autónomo y
  curva medida de la 604050 de 1500 mAh (45,4 h / 5.448 páginas; 4,10 V en
  reposo = 100 %).
- Nuevo ajuste **Ajustes > Sistema > Perfil de batería**: `Kit original
  (140 mAh)` o `Extendida (1500 mAh)`. Solo cambia la curva del porcentaje, no
  la carga.
- Lecturas de batería del PM1 serializadas en la HAL y `About`.
- Build 5.438.295 B (83,0 % flash, 33,9 % RAM); tests de batería 5/5.
- Smoke básico de hardware OK (Home, lector, giro de página, ajustes y perfil
  Extendida), no el `make smoke` completo. Quedan pendientes la revisión visual
  de ghosting y sleep/wake.

### 2.0.0-5 — 2026-11-12

Mantenimiento; sin cambios funcionales de firmware.

- Corregido el test de licencias para el SDK vendorizado y preservado en el
  sync.
- Tests host 922/922 y tests Python 15/15.
- Mismo firmware que `2.0.0-4` salvo la cadena de versión.

### 2.0.0-4 — 2026-11-12

Sincronización con CrossPoint `fa17b9ca` (16 commits).

- **Controles** reorganizados en submenús: Botón de encendido, Botones
  frontales, Botones laterales y Toques y gestos.
- **OPDS** pasa a `Transferir archivos → Navegador OPDS`; los servidores se
  gestionan en `Ajustes → Conectividad → Servidores OPDS`. También aparece en
  Inicio si el sistema de plugins está desactivado y ya hay un servidor
  guardado.
- Nuevo ajuste **Mostrar extensiones de archivo**.
- **Lector**: margen inferior conservado con la barra de progreso, contador de
  página en la última página, sin división de palabras en títulos, redondeo de
  avances TTF y PageLink a cero.
- **Estabilidad**: rotación de capturas, tokens de plugin tras escrituras
  fallidas, credenciales WebDAV, Basic auth en clipping sync, marcas
  hebreas/árabes en el diccionario y caché de portadas del Home.
- Traducciones al español y guías actualizadas para las rutas nuevas.
- Build 5.432.192 B (82,8 % flash, 33,9 % RAM). Tests host 922/922; smoke de
  hardware 25 pasos.

### 2.0.0-3 — 2026-11-10

Sincronización con CrossPoint `8276d518` (3 commits) y FreeInk SDK `6a208c0c`.

- Home pinta la rejilla de portadas en un solo refresco con caché caliente.
- TLS vuelve a pedir registros de 2 KB con fallback a 16 KB.
- SecureNet descarta cabeceras `Content-Security-Policy` sobredimensionadas de
  GitHub en vez de fallar.
- Actualización del SDK para descargas de fuentes.
- Añadido `make smoke`: regresión determinista con fixtures EPUB/StarDict,
  aserciones OCR, backup/restore y `--restore-hold`.
- Validado: arranque, Home, A/B, lector con 9 page turns, OTA sin
  actualizaciones, catálogo y descarga/instalación de una fuente, orientación,
  OPDS con descarga y borrado, USB MSC, BLE activado/escaneo y servidor Calibre
  inalámbrico.
- Build 5.428.032 B (82,7 % flash, 33,9 % RAM). Tests host 914/914.

## Limitaciones conocidas

- Emparejamiento real con mando BLE sin validar.
- Envío completo desde Calibre y actualización OTA completa sin repetir.
- Sleep/wake, consumo en reposo y revisión visual de ghosting siguen
  pendientes (el refresco rápido por defecto es cada 5 páginas). La 604050
  extendida se midió en una descarga real (45,4 h / 5.448 páginas), pero ambas
  curvas de batería siguen pendientes de validar en lectura normal. La celda
  original de 140 mAh conserva su curva original.
- Sync On Sleep no se ha probado contra un servidor CrossPoint Sync real.
- La última ejecución completa de `make smoke` pasó en el árbol de `177d0694`
  (25 pasos, run `20261122-193337`); `2.0.0-11` solo cambia la versión y añade
  traducciones. El salto visual de la curva sigue pendiente con batería por
  debajo del ~90 %.
