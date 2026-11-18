# Changelog de M5Burner

Última publicación registrada en este repositorio: **2.0.0-2** (tag
`v2.0.0-2`, 2026-11-09). Las entradas **2.0.0-3** a **2.0.0-9** documentan sus
cambios y el texto preparado para el diálogo Publish; no hay constancia en el
repositorio de que se hayan subido a M5Burner y el estado del catálogo no está
verificado.
La subida es manual: confirma el catálogo y actualiza esta línea solo después
de publicar.

## Short description for M5Burner (EN)

CrossPoint for PaperDIY 2.0.0-9 — cumulative update from 2.0.0-2.

- Synced with CrossPoint `b6b7a6c1` / FreeInk SDK `77ae8c75`: dictionary side
  buttons, font-cache release, Recent opened-only filter, OPDS redirect error,
  EEGO/Picco fixes and branch+hash versions.
- PM1 I²C bus serialized between tasks and battery status cached to avoid
  phantom power clicks and redundant reads.
- `Display Refresh` removed; use `Refresh Screen` and `Refresh Frequency`.
- Spanish/Catalan/Valencian translations for the new Recent strings.
- Controls reorganized into Power, Front, Side and Gestures submenus.
- OPDS browser moved to File Transfer; servers live in Settings > Connectivity.
- New "Show File Extensions" setting.
- Reader fixes: progress-bar margin, last-page counter, no hyphenation in
  headings, TTF advance rounding.
- Stability: screenshot rotation, PageLink, plugin tokens, WebDAV credentials,
  clipping-sync Basic auth, Hebrew/Arabic dictionary lookup, Home cover cache.
- Faster Home cover grid; TLS 2 KB records; updated FreeInk SDK for font
  downloads.
- Battery: selectable kit/extended profile, discharge log, measured 1500 mAh
  curve and percentage held while charging; profile changes now apply live
  from the UI and web and persist across reboots.
- Synced with CrossPoint `490813ff` / FreeInk SDK `3f3e4c1`: power-gesture
  disambiguation, reader/Home/WebDAV/font-download fixes and EPD/TTF
  improvements from the previous sync.
- Spanish translations and user-guide updates.

Known limitations: real BLE remote pairing, full Calibre transfer and full OTA
install remain pending, as do sleep/wake, idle current, autonomy and the visual
ghosting review. The full `make smoke` passed on `2.0.0-9` (25 steps, run
`20261118-121539`); `2.0.0-6` has no dedicated run. The visual battery-curve
jump still needs a battery below ~90%.

## Full changelog (EN)

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
  build and 25-step hardware smoke passed (`20261118-121539`).

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
- The latest full `make smoke` passed on `2.0.0-9` (25 steps, run
  `20261118-121539`); `2.0.0-6` has no dedicated run. The visual battery-curve
  jump still needs a battery below ~90%.

## Changelog completo (ES)

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
- La última ejecución completa de `make smoke` pasó en `2.0.0-9` (25 pasos,
  run `20261118-121539`); `2.0.0-6` no tiene una ejecución propia. El salto
  visual de la curva sigue pendiente con batería por debajo del ~90 %.
