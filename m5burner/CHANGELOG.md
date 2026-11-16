# Changelog de M5Burner

Última versión publicada en M5Burner: **2.0.0-2** (2026-11-10). Esta entrada
acumula los cambios de **2.0.0-3**, **2.0.0-4** y **2.0.0-5**.

## Short description for M5Burner (EN)

CrossPoint for PaperDIY 2.0.0-5 — cumulative update from 2.0.0-2.

- Controls reorganized into Power, Front, Side and Gestures submenus.
- OPDS browser moved to File Transfer; servers live in Settings > Connectivity.
- New "Show File Extensions" setting.
- Reader fixes: progress-bar margin, last-page counter, no hyphenation in
  headings, TTF advance rounding.
- Stability: screenshot rotation, PageLink, plugin tokens, WebDAV credentials,
  clipping-sync Basic auth, Hebrew/Arabic dictionary lookup, Home cover cache.
- Faster Home cover grid; TLS 2 KB records; updated FreeInk SDK for font
  downloads.
- Spanish translations and user-guide updates.

Known limitations: real BLE remote pairing, full Calibre transfer, full OTA
install, sleep/wake and battery/ghosting measurements remain pending.

## Full changelog (EN)

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
- Sleep/wake, idle current and battery life have not been measured in this
  release.
- Ghosting is pending a physical visual review; the default fast refresh is
  every 5 pages.
- The original 140 mAh cell gives short battery life; a 604050 cell is planned
  but not validated.

## Changelog completo (ES)

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
- Sleep/wake, consumo en reposo y autonomía sin medir en esta release.
- Ghosting pendiente de revisión visual física; el refresco rápido por defecto
  es cada 5 páginas.
- La batería original de 140 mAh da poca autonomía; la 604050 está prevista
  pero no validada.
