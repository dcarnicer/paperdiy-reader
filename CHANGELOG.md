# Changelog

## 2.1.0-1 — 2026-11-26

Sincronización con CrossPoint `a2b0d48b` y FreeInk SDK `de19f154`. Upstream
sube la versión a **CrossPoint 2.1.0** (tag `2.1.0rc` en `d2270389`), así que
la numeración del fork se reinicia en `2.1.0-1`. Primera release del fork con
las fuentes incrustadas en el EPUB y el render PSRAM nuevo.

- Lector: fuentes `@font-face` incrustadas en el EPUB, con el ajuste
  **Publisher Fonts** en el menú del lector → **Ajustes de texto → Estilo**:
  `Off`, `Ignore Body Font` (por defecto: solo los estilos que no son el
  cuerpo) y `All Text`. Solo en las placas con PSRAM (PaperDIY y ws397) y con
  **Estilo integrado** activado; el EPUB debe traer fuentes incrustadas
  compatibles. Los bytes de cada familia se leen a PSRAM y se cachean por
  tamaño; un EPUB con muchas familias puede ocupar varios cientos de KB de
  PSRAM.
- Render: en placas con PSRAM y páginas sin imágenes, el paso de grises usa
  dos planos a la vez y elimina una pasada de render (#4601); el lector
  reutiliza el EPUB abierto en vez de reabrir el ZIP (#4619). Falta medir la
  mejora y revisar el ghosting en hardware.
- Caché: sube la versión de las secciones y de las fuentes incrustadas
  (77/20). Tras actualizar, la primera apertura de cada libro reconstruye sus
  secciones; es esperado y ocurre una sola vez por libro.
- Biblioteca: los títulos largos se ajustan en varias líneas; los BMP nativos
  de 4 bits ya no salen lavados; los iconos de la cabecera se alinean con el
  texto.
- Flash: se elimina la lista de glifos Adobe y se recortan las features de
  FreeType que no usamos.
- OPDS/TLS: llega el fix completo de reserva de registro TLS y rango de
  descarga (#4576); el fork ya llevaba la parte de `src/`, ahora upstream
  incluye también los parches de wolfSSL. El reserve de entradas OPDS cuenta
  la PSRAM.
- SD: errores de arranque clasificados y protección de guardados y
  transferencias USB frente a interrupciones. La detección de tarjeta y
  `unmount`/`remount` del fork se conservan.
- Barra de estado: se refresca de forma independiente en páginas con
  antialiasing; redondeo de AA corregido.
- Traducciones: upstream actualiza doce idiomas (#4624), incluidos ES/CA/VA.
  El fork adopta las traducciones de upstream para las cadenas que antes
  traducía por su cuenta (Sync On Sleep, pulsación larga, vocabulario, OPDS,
  fuente de la interfaz, índice de la biblioteca) y solo conserva las del
  perfil de batería.
- Sincronización: CrossPoint `92e8714a` → `a2b0d48b` (13 commits) y SDK
  `995d9bd5` → `de19f154` (27 commits, 4 ya adelantados). Se quitan de la
  tabla los PRs ya fusionados (CrossPoint #4576 y los commits del `main` del
  SDK hasta `a7eb4cc`); siguen SDK #218 y CrossPoint #3386 (ws397).
- Port: conflictos resueltos en `SDCardManager` (se conservan `StartupError`
  de upstream y `isCardPresent`/`unmount`/`remount` del fork), el stub
  `SdFat.h`, `OpdsBookBrowserActivity` (se elimina el hunk duplicado de
  #4576) y las traducciones ES/CA/VA. `patches/` regenerados contra
  `de19f154` / `a2b0d48b` y verificados con `git apply --check`.
- Build `paperdiy`: `firmware.bin` 5.658.768 B, 86,3 % de flash y 34,4 % de
  RAM. Build `ws397`: `firmware.bin` 5.638.320 B, 86,0 % de flash y 34,5 % de
  RAM. `paperdiy-test` y `ws397-test` compilan. Tests de host: 1157/1157;
  tests de host del SDK (SD, USB, OPDS, InputManager y su variante PaperDIY):
  OK.
- Pendiente de hardware: fuentes `@font-face`, ghosting del camino PSRAM, SD
  sin tarjeta e inserción en caliente, unidad USB y catálogo OPDS grande.

## 2.0.0-12 — 2026-11-24

Primera release con dos placas: M5Stack PaperDIY y Waveshare
ESP32-S3-ePaper-3.97 (experimental). Sincronización con CrossPoint `92e8714a`
y FreeInk SDK `995d9bd5` más su `main` hasta `a7eb4cc`; M5GFX `0.3.0`.
Mantiene CrossPoint `2.0.0`.

- Waveshare 3.97: primera release con la placa. Cada release publica también
  `crosspoint-ws397-latest.bin` (imagen completa, se instala con esptool en
  `0x0`) y `crosspoint-ws397-<versión>-ota.bin` (actualización desde el
  lector). Activa la unidad USB (`Transferir archivos → Unidad USB`); con ella
  el heap libre baja de unos 209 KB a 172 KB. READMEs en los cuatro idiomas con
  una sección para la placa y nota de usuario
  [`15-waveshare-397.md`](docs/paperdiy/15-waveshare-397.md) ampliada.
- Smoke en hardware: `device_regression.py --board ws397` (capturas de
  800×480, SD `NO NAME`) y una segunda lectura OCR sin el tramado de la fila
  seleccionada, que el texto más pequeño de la Waveshare confundía.
- PaperDIY: en los catálogos OPDS con varias páginas, A/B vuelven a mover la
  selección; antes B cargaba la página siguiente y no se podía elegir nada.
  B en la última entrada carga la página siguiente y A en la primera, la
  anterior; la fila de pistas lo indica. A en la primera entrada abre la
  búsqueda también en la PaperDIY, que antes no reaccionaba. El mismo cambio
  aplica a la Waveshare 3.97, probado allí con el mismo catálogo. Las demás
  placas no cambian.
- Sincronización con CrossPoint `92e8714a` (10 commits desde `177d0694`):
  ajuste de fuente personalizada para la interfaz, selección de estilos de
  fuentes vectoriales por nombre de fichero, caché de prefijos TTF según el
  directorio sfnt, carpetas de diccionario con nombres de más de 31 bytes,
  cajas sombreadas legibles en EPUB, cabecera compacta de Home, detalle HTTP
  en errores al descargar plugins, limpieza de la caché DNS en el contexto
  TCP/IP y luz frontal apagada antes al dormir. El pin del SDK no cambia
  (`995d9bd5`). Conflicto resuelto en `SettingsActivity`: los popups siguen
  con refresco parcial, salvo cuando falla cargar una fuente de la interfaz y
  hay que redibujar el fondo.
- FreeInk SDK: se adelantan los 4 commits de `main` hasta `a7eb4cc` que
  CrossPoint aún no ha fijado. El login OPDS solo se envía al servidor
  configurado (también en la primera petición) y las credenciales no siguen a
  otro origen. Además, despierta el táctil de la Picco al arrancar. El
  explorador OPDS se adapta a la API nueva con el commit `15b04ea8` del PR
  de upstream #4576.
- PaperDIY: M5GFX `0.2.36` → `0.3.0`. En el bus y el panel EPD que usamos
  solo cambian comentarios; la versión trae además la nueva detección de
  placas, que no usamos porque configuramos el panel a mano.
- Waveshare ESP32-S3-ePaper-3.97 (experimental): envs `ws397` y `ws397-test`.
  Lleva los PRs de upstream CrossPoint #3386 y FreeInk SDK #218 (Alexey
  Pazyuk), todavía sin fusionar. En el SDK: el refresco HALF usa la secuencia
  rápida del fabricante, los raíles del panel se apagan tras la pasada de
  grises (solo ws397) y se añade `hasHorizontalKeys()`. Ver
  [`15-waveshare-397.md`](docs/paperdiy/15-waveshare-397.md).
- PaperDIY: en el teclado en pantalla, A/B recorren ahora todas las teclas en
  orden de lectura y saltan de fila al final de cada una; antes solo se
  llegaba a la primera columna. La fila de pistas de botones se mantiene en
  las placas de dos botones; en las de botonera lateral (ws397) se oculta.
- En placas donde Atrás y encendido son la misma tecla, Atrás actúa solo con
  pulsación corta. No afecta a la PaperDIY.
- Validado el 23/11/2026: `make smoke` PaperDIY PASS 25 pasos (run
  `20261123-173924`) y teclado probado a mano en las dos placas; ws397 en una
  unidad (arranque, lector, Ajustes, Wi-Fi, botonera, dormir y despertar con
  BOOT). El CI compila también `ws397`.
- Hardware: carcasa v21 en STL (`hardware/3d/v21/`): tapa trasera con
  hendidura para un anillo MagSafe (Ø 56,4/44,6 mm, 0,8 mm), marco frontal
  orientado boca abajo, barra basculante A/B y palanca del botón C
  (power), con vista previa. El remix `PaperDIY_kit_completo.3mf` se conserva
  como versión anterior.
- Licencias: el firmware compilado es GPLv3 (incluye wolfSSL). Las releases
  adjuntan `LICENSE` con los textos completos, los avisos de terceros y las
  revisiones del código y del SDK, y sus notas lo indican; se añadió a
  `v2.0.0-11`. Los READMEs distinguen código MIT y binario GPLv3, y el enlace
  de FreeInk apunta a su repositorio. La descripción de M5Burner incluye la
  licencia.
- M5Burner: descripción de la app al día y guardada en `m5burner/README.md`;
  `m5burner.json` usa el nombre del catálogo, `CrossPoint for PaperDIY
  (community port)`, el mismo que busca el aviso de actualizaciones, y
  `PACKAGE_README.md` añade funciones, actualizaciones bajo M5Launcher y
  limitaciones vigentes.
- `NOTICE` vuelve a registrar el commit de CrossPoint y el pin del SDK
  (estaban en `b6b7a6c1` / `77ae8c75`); `scripts/update_notice_pins.py` los
  actualiza en cada sync.

## 2.0.0-11 — 2026-11-22

Sincronización con CrossPoint `177d0694` y FreeInk SDK `995d9bd5`. Mantiene
CrossPoint `2.0.0`.

- CrossPoint `209cb53a` → `177d0694` (14 commits): Sync On Sleep, sesiones de
  lectura y sincronización de marcadores con servidores CrossPoint Sync;
  soporte de escrituras índicas sin HarfBuzz; reloj y batería normalizados en
  las cabeceras de los temas; progreso de lectura en Lyra; navegación de
  plugins en la WebUI; nombre del fichero en el popup del explorador;
  renombrar en la web conserva la extensión; la imagen de sleep se limpia al
  sustituirla; y fixes de recortes y BMP.
- SDK `634a3f8c` → `995d9bd5` (8 commits): nuevo Seeed reTerminal E1001,
  lectura de ficheros de la SD con límite de tamaño, y mejoras de refresco en
  modo oscuro y del driver UC8279C A4. Sin cambios previstos en PaperDIY.
- Conflictos resueltos: `BoardConfig.h` lista E1001 junto a PaperDIY;
  `HalPowerManager::readBatteryPercentage` (nuevo, usado por el Wi-Fi al
  dormir) pasa en PaperDIY por la presentación de batería del PM1 y el mutex;
  `main.cpp` conserva los dos includes. Upstream quitó
  `UiListActivity::cleanNextRefresh`; el fork lo mantiene para limpiar la
  página bajo el menú del lector.
- Traducción ES/CA/VA de `Sync On Sleep`.
- `patches/sdk.patch`, `patches/firmware.patch` y
  `patches/paperdiy-support.patch` regenerados contra `995d9bd5` / `177d0694`
  y verificados con `git apply --check`.
- Build `paperdiy`: `firmware.bin` 5.528.960 B, 84,3 % de flash y 34,1 % de
  RAM. `paperdiy-test` compila, 1027 tests de host y `make smoke` 25/25
  (`20261122-193337`).
- `2.0.0-11` solo cambia la cadena de versión y las traducciones respecto al
  árbol probado en el smoke; el build de producción se flasheó en el PaperDIY
  y arranca en Home con el estado del usuario.
- Hardware: smoke completo sobre `paperdiy-test`; pendientes ghosting (incluido
  el menú del lector), autonomía, sleep/wake, Sync On Sleep real, BLE real,
  Calibre completo y OTA completa.

## 2.0.0-10 — 2026-11-19

Sincronización con CrossPoint `209cb53a` y FreeInk SDK `634a3f8c`. Mantiene
CrossPoint `2.0.0`.

- CrossPoint `b6b7a6c1` → `209cb53a`: full-tone para imágenes en EPUB en
  EEGO/Picco, conservación de KOReader Sync al apagar Bluetooth, auto-sleep sin
  contar el tiempo bloqueado y limpieza de código muerto.
- SDK `77ae8c75` → `634a3f8c`: refresco rápido tras Gray3, overlay de grises,
  LUTs/drivers SSD2677 y UC8279C A4, y orden hold/release de pines en Picco.
  El port se reaplicó; no hay cambios de comportamiento previstos en PaperDIY.
- Conflictos resueltos: `HalStorage` conserva `ready`, `isCardPresent` y
  `remount`; `AboutActivity` mantiene la fila de batería sobre el nuevo
  `ITEM_COUNT`; `OtaUpdater` conserva el camino de Launcher.
- `patches/sdk.patch`, `patches/firmware.patch` y
  `patches/paperdiy-support.patch` regenerados contra `634a3f8c` / `209cb53a`
  y verificados con `git apply --check`.
- Build `paperdiy`: `firmware.bin` 5.446.032 B, 83,0 % de flash y 33,9 % de
  RAM. `paperdiy-test` compila y `make smoke` 25/25 (`20261119-120845`).
- `2.0.0-10` solo cambia la cadena de versión respecto al árbol probado en el
  smoke; el build de producción se flasheó en el PaperDIY y arranca en Home
  con el estado del usuario.
- Hardware: smoke completo sobre `paperdiy-test`; pendientes ghosting,
  autonomía, sleep/wake, BLE real, Calibre completo y OTA completa.

## 2.0.0-9 — 2026-11-18

Sincronización con CrossPoint `b6b7a6c1` y FreeInk SDK `77ae8c75`. Mantiene
CrossPoint `2.0.0`.

- CrossPoint `490813ff` → `b6b7a6c1`: botones laterales en páginas de
  diccionario, liberación de cachés de fuentes al cerrar capítulos, opción de
  Recientes solo con libros abiertos, mensaje de error OPDS con redirects,
  auto-sleep y UID de EEGO A4, upload app-only de Picco y versión branch+hash.
- SDK `3f3e4c1` → `77ae8c75`: nuevo `InputManager` con supresión del chord A+B,
  listas interactivas, mejoras de pantalla para Picco/EEGO y cabeceras de
  `SecureNet`. Port reaplicado sobre el pin nuevo.
- PM1: el bus I²C se serializa con `I2cBusLock` entre las tareas de render y
  loop, se configura una sola vez y el estado de batería se cachea durante
  `BATTERY_POLL_MS`. Evita reinit y lecturas entre tareas.
- `Display Refresh` eliminado de Ajustes (upstream); las guías usan `Refresh
  Screen` y `Refresh Frequency`.
- Traducciones ES/CA/VA para las nuevas cadenas de Recientes; ayuda de
  recuperación CA/VA alineada con `-ota.bin`.
- Build `paperdiy`: `firmware.bin` 5.446.272 B, 83,0 % de flash y 33,9 % de
  RAM. Tests: 935 host, `paperdiy-test` compila y `make smoke` 25/25
  (`20261118-132153`).
- Hardware: smoke completo sobre `paperdiy-test`; pendientes ghosting,
  autonomía, sleep/wake, BLE real, Calibre completo y OTA completa.

## 2.0.0-8 — 2026-11-16

Sincronización con CrossPoint `490813ff` y FreeInk SDK `3f3e4c1`, más los
arreglos de validación del port. Mantiene CrossPoint `2.0.0`.

- CrossPoint `36b9430e` → `490813ff`: desambiguación de gestos del botón power
  en reinicios suaves, arreglos varios de lector, Home, WebDAV, descarga de
  fuentes y servidor web, y stats de flash/RAM en CI.
- SDK `a8acebf` → `3f3e4c1`, con el port de PaperDIY reaplicado y el nuevo
  `InputManager` de gestos. Los pulsos del PM1 se normalizan como clicks
  (duración 0) y el click que despierta no se reenvía a la app.
- Perfil de batería: el cambio Kit/Extendida se aplica en caliente desde la UI
  y desde la web, sin reinicio. Se persiste en `settings.json` con validación
  y fallback a `Kit original`.
- Traducción española de `Display Refresh`.
- Docs: pins de sync, estado de release/M5Burner, checklist de hardware y
  resultados del smoke.
- Build `paperdiy`: `firmware.bin` 5.445.184 B, 83,0 % de flash y 33,9 % de
  RAM. Tests: 18 Python, 933 host, PMIC PaperDIY y `make smoke` 25/25.
- Hardware: wake-click/A+B, SD en caliente, persistencia y cambio web del
  perfil de batería validados. Pendiente el salto visual de la curva con
  batería <90 % y la autonomía.

## 2.0.0-7 — 2026-11-15

Corrección de la presentación de batería en PaperDIY. Mantiene CrossPoint
`36b9430e` y FreeInk SDK `a8acebf`.

- El PM1 no tiene coulomb counter y la tensión de carga no sirve para estimar
  el estado de carga. Mientras hay USB, el porcentaje se congela en el último
  valor de descarga; al completar la carga muestra 100 %.
- Tras desenchufar, se mantiene el último valor durante ~2 min para que la
  celda se relaje, y después vuelve a la curva de descarga.
- El último porcentaje de descarga se guarda en NVS, así que sobrevive al
  apagado y a un arranque mientras carga.
- Hook `BATHOLD` solo en `paperdiy-test` para verificar el camino de retención.
- Build `paperdiy`: `firmware.bin` 5.438.679 B, 83,0 % de flash y 33,9 % de
  RAM. `paperdiy-test` compila. Tests de batería 5/5.

## 2.0.0-6 — 2026-11-15

Revisión sobre CrossPoint `2.0.0` (`36b9430e`) y FreeInk SDK `a8acebf`.
Mantiene el esquema `<CrossPoint X.Y.Z>-<N>`.

- CrossPoint `622e5de9` → `36b9430e`: mejoras de refresco EPD para todos los
  paneles, optimizaciones TTF, profundidad de bits XTC, chevron de página
  anterior y los fixes de la sync anterior (Controles agrupados en la web y
  scroll de `OptionPopup`).
- SDK: `6a208c0c` → `a8acebf`. Se reaplicó el port de PaperDIY y se resolvieron
  los conflictos de la política PSRAM y de `GfxRenderer` (ventana de refresco).
- Batería: log de descarga en `/battery-log.csv` (muestra cada 5 min, rotación
  a 1 MB), descarga por serie con `CMD:BATLOG` y modo de page-turning autónomo
  en `paperdiy-test` con contador `pages`.
- Curva de la 604050 de 1500 mAh medida con una descarga real de **45,4 h y
  5.448 páginas** (30 s/página, sin WiFi). Ancla superior en **4,10 V en
  reposo** y anclajes inferiores ajustados para no mostrar 0 % durante horas.
- Nuevo ajuste **Ajustes > Sistema > Perfil de batería**: `Kit original
  (140 mAh)` por defecto o `Extendida (1500 mAh)`. Solo cambia la curva del
  porcentaje; la carga no cambia.
- Lecturas de batería del PM1 serializadas en la HAL y `About` usando el mismo
  camino.
- Build `paperdiy`: `firmware.bin` 5.438.295 B, 83,0 % de flash y 33,9 % de
  RAM. `paperdiy-test` compila. Tests de batería 5/5; test de selección y
  `OptionPopup` OK.

## 2.0.0-5 — 2026-11-12

Revisión de mantenimiento sobre CrossPoint `2.0.0` (`fa17b9ca`) y FreeInk SDK
`6a208c0c`, sin cambios de firmware. Mantiene el esquema
`<CrossPoint X.Y.Z>-<N>`.

- Corrige `test/test_release_license.py` para el SDK vendorizado: el mock de
  `git` incluye la llamada `cat-file -t` que distingue submódulo de árbol
  vendorizado. `scripts/sync-upstream.sh` preserva el test como archivo propio
  del fork.
- Tests Python 15/15.
- Build `paperdiy`: idéntico a `2.0.0-4` salvo la cadena de versión;
  `firmware.bin` 5.432.192 B, 82,8 % de flash y 33,9 % de RAM.
- Smoke de hardware repetido sobre las mismas fuentes (`paperdiy-test`, run
  `20261112-124506`): **PASS, 25 pasos**. El build de producción `2.0.0-5` se
  flasheó y arranca en Home.

## 2.0.0-4 — 2026-11-12

Cuarta revisión del port sobre CrossPoint `2.0.0` (`fa17b9ca`) y FreeInk SDK
`6a208c0c`. Mantiene el esquema `<CrossPoint X.Y.Z>-<N>`. Commit de sync:
`f82a332f` en `paperdiy-next`; merge en `paperdiy`: `1c420918`.

- CrossPoint `8276d518` → `fa17b9ca` (16 commits): Controles reorganizado en
  submenús (botón de encendido, botones frontales, laterales y gestos), OPDS
  movido a File Transfer, ajuste «Mostrar extensiones de archivo», corrección
  de rotación de capturas, margen inferior del lector con barra de progreso,
  contador de página en la última página, sin división de palabras en títulos,
  redondeo de avances TTF, PageLink a cero, tokens de plugin, credenciales
  WebDAV, Basic auth en clipping sync, marcas hebreas/árabes en el diccionario
  y caché de portadas del Home.
- FreeInk SDK sin cambios (`6a208c0c`). La `main` del SDK ya está en `e637713`
  e incluye `d2600e9`, que corrige el límite de cabeceras de SecureNet; se
  adopta cuando CrossPoint mueva el pin.
- Traducciones nuevas al español para los grupos de Controles, extensiones de
  archivo y descripción de OPDS; las guías recogen las rutas nuevas de
  Controles y OPDS.
- Build `paperdiy`: `firmware.bin` 5.432.192 B, 82,8 % de flash
  (5.426.903 / 6.553.600 B) y 33,9 % de RAM (110.932 B).
- Tests host 922/922.
- Smoke determinista en PaperDIY real (`paperdiy-test`, `2.0.0-4`, run
  `20261112-115404`): PASS 25 pasos (Home, explorador, page turn, menú, TOC,
  enlaces, nota al pie, cancelación de recorte y diccionario). El build de
  producción `paperdiy` (`2.0.0-4`) se flasheó y arranca en Home.
- `patches/sdk.patch`, `patches/firmware.patch` y
  `patches/paperdiy-support.patch` regenerados y verificados con
  `git apply --check` contra `fa17b9ca` / `6a208c0c`.
- Pendiente de validación física: ghosting/autonomía, sleep/wake, emparejamiento
  BLE real, envío Calibre completo y una instalación OTA completa. Riesgos y
  estado en `docs/paperdiy/10-fork-maintenance.md`.

## 2.0.0-3 — 2026-11-10

Tercera revisión del port sobre CrossPoint `2.0.0` (`8276d518`) y FreeInk SDK
`6a208c0c`. Sustituye a `2.0.0-2` y mantiene el esquema de versión
`<CrossPoint X.Y.Z>-<N>`. Commit de sync: `c50630b0` en `paperdiy-next`.

- CrossPoint `f8db833f` → `8276d518` (3 commits): Home pinta la rejilla de
  portadas en un solo refresco con caché caliente; TLS vuelve a pedir registros
  de 2 KB (`HAVE_MAX_FRAGMENT`) con fallback a 16 KB; actualización del SDK para
  descargas de fuentes.
- FreeInk SDK `ac146e4` → `6a208c0c` (1 commit): SecureNet descarta cabeceras
  `Content-Security-Policy` sobredimensionadas de GitHub en vez de fallar.
- Build `paperdiy`: `firmware.bin` 5.428.032 B, 82,7 % de flash
  (5.422.747 / 6.553.600 B) y 33,9 % de RAM.
- Tests host 914/914; tests host de SecureNet OK.
- Smoke por serie en PaperDIY real (`paperdiy-test`, `2.0.0-3`): arranque, Home,
  navegación A/B, lector con 9 page turns, OTA sin actualizaciones, catálogo y
  descarga/instalación de una fuente, orientación, OPDS con descarga y borrado
  del EPUB, USB MSC (DABI, escritura/lectura y expulsión), BLE activado/escaneo
  y servidor de Calibre inalámbrico. El build de producción `paperdiy` se
  flasheó y arranca en Home.
- `sdk-baseline` recreada en `6a208c0c`; `patches/sdk.patch`,
  `patches/firmware.patch` y `patches/paperdiy-support.patch` regenerados y
  verificados contra `8276d518` / `6a208c0c`.
- Añadido `make smoke`: runner determinista con fixtures EPUB/StarDict,
  aserciones OCR, backup/restore del estado y `--restore-hold` para el ciclo de
  power. Ver `docs/paperdiy/14-device-regression.md`.
- Pendiente de validación física (no repetida en esta release):
  ghosting/autonomía, sleep/wake, emparejamiento BLE real, envío Calibre
  completo y una instalación OTA completa. Riesgos y estado en
  `docs/paperdiy/10-fork-maintenance.md`.

## 2.0.0-2 — 2026-11-09

Segunda revisión del port sobre CrossPoint `2.0.0` (`f8db833f`) y FreeInk SDK
`ac146e4`. Mantiene el esquema de versión `<CrossPoint X.Y.Z>-<N>` y publica
las mismas dos imágenes que `2.0.0-1`.

- CrossPoint actualizado de `818a1540` a `f8db833f` (3 commits): la selección
  de palabras para enlaces y footnotes reutiliza la del diccionario y respeta
  el formato; corregido el subrayado al seleccionar en clipping; el catálogo
  de Manage Fonts incluye `NotoSansCJKJP` (aparecerá cuando se republique el
  manifiesto externo de fuentes).
- FreeInk SDK actualizado de `fb7e926` a `ac146e4` (8 commits): correcciones
  de EEGO A4 (pantalla grisácea en idle, estabilidad Gray3, toque en el borde
  inferior, arranque del táctil en background y brillo del frontlight). No
  cambia el comportamiento esperado del PaperDIY; los parches se reaplican
  limpios.
- El overlay de `scripts/sync-upstream.sh` conserva `.agents/rules/release-versioning.md`,
  `lib/expat` y `test/firmware_version`; las líneas del fork en
  `.agents/README.md` y los `CMakeLists` las añade
  `scripts/apply_downstream_overlay.py`. Si upstream toca `lib/expat`,
  `.gitattributes`, `.gitignore` o `LICENSE`, el sync se detiene en vez de
  pisar la versión nueva.
- `patches/sdk.patch`, `patches/firmware.patch` y
  `patches/paperdiy-support.patch` regenerados contra `ac146e4` / `f8db833f`;
  `git apply --check` limpio sobre `sdk-baseline` y `main`.
- Build `paperdiy` correcto: `firmware.bin` 5.427.376 B y 82,7 % de uso de
  flash (5.422.079 / 6.553.600 B). Tests host 914/914 en serie.
- Smoke en un PaperDIY real (09/11): arranque, Home, lector, page turn,
  recorte multipalabra con A/B, selector de enlaces con subrayado, TOC,
  orientación, About y USB MSC. Sleep/wake no se repitió; el camino de
  energía no cambia en este sync. Quedan pendientes ghosting físico,
  autonomía y Wi-Fi/OPDS/OTA/BLE con esta base.

## 2.0.0-1 — 2026-11-08

Primera release con el esquema de versión `<CrossPoint X.Y.Z>-<N>`:
CrossPoint `2.0.0` (`818a1540`) y revisión 1 del port. Es corta porque el
campo de versión de M5Burner no admite cadenas largas. Sustituye a `v2.1.0`,
que se retiró porque su número no correspondía a ninguna versión de
CrossPoint. Un PaperDIY en 2.1.0, standalone o bajo M5Launcher, ve 2.1.0
como más nueva: hay que actualizarlo una vez a mano.

- La OTA de GitHub y el aviso de Launcher comparan versión de CrossPoint,
  revisión del port y RC (`FirmwareVersion`, con tests de host).
- La release publica solo dos `.bin`: `crosspoint-paperdiy-latest.bin`
  (imagen completa para M5Burner, M5Launcher y esptool, con enlace `latest`
  permanente) y `crosspoint-paperdiy-<versión>-ota.bin` (solo para la OTA
  standalone). Desaparecen `firmware.bin`, los `.bin` de Launcher solo-app y
  `scripts/make_launcher_package.py`: Launcher instala la imagen completa.
- La URL de releases del fork se fija en `platformio.ini`, así que un build
  local busca actualizaciones en este repo igual que el de CI.
- Un PaperDIY en v0.1.0 busca el asset con el nombre antiguo y no verá esta
  actualización: hay que instalarla una vez a mano.
- Si guardaste en Favoritos de Launcher el enlace a
  `PaperDIYReader-launcher.bin`, cámbialo por
  `…/releases/latest/download/crosspoint-paperdiy-latest.bin`.

### Aviso de actualización bajo M5Launcher

- Bajo M5Launcher vuelve `Verificar actualizaciones`, solo como aviso: busca
  `CrossPoint for PaperDIY (community port)` en LauncherHub (réplica de
  M5Burner) y, si hay versión nueva, ofrece `Salir a M5Launcher` para
  instalarla desde `OTA`, y recuerda borrar la versión anterior: Launcher
  instala cada versión junto a la vieja. El lector sigue sin escribir en la
  flash bajo Launcher; la actualización por SD sigue oculta.
- Validado en un PaperDIY con M5Launcher 3.0.0 con un build temporal: aviso,
  salida con tecla A, por deep sleep y por reset del PM1. Falta probarlo con la
  app publicada en M5Burner.

## 2.1.0 — 2026-11-08 (retirada, ver 2.0.0-1)

Primera release sobre CrossPoint `818a1540`. Incluye el sync del motor, la
actualización de expat/ArduinoJson/NimBLE/M5GFX y las correcciones encontradas
en la prueba de hardware. El detalle está en las entradas siguientes.

- Build `paperdiy` correcto y 905/905 tests host.
- Smoke validado en un PaperDIY real: arranque, Home, menús, About, lector,
  paginación, orientación vertical/horizontal, USB MSC, diccionario StarDict y
  `/Vocabulary.txt`.
- Pendiente: Wi-Fi/OPDS/OTA, BLE, ghosting físico y autonomía.

## 2026-11-08 — correcciones de la prueba en hardware

- `VocabularyStore`: elimina el terminador NUL de las definiciones StarDict y
  ya no marca `definition_truncated` cuando el único recorte era ese byte.
- Traducido al español el nuevo ajuste `Guardar vocabulario`.
- Verificado en un PaperDIY real: arranque, Home, menús, About, lector,
  paginación, orientación vertical/horizontal y USB MSC. Diccionario StarDict
  y `/Vocabulary.txt` probados con un diccionario de prueba.

## 2026-11-08 — dependencias

- expat vendorizado actualizado de 2.7.3 a 2.10.0. El firmware usa el RNG del
  ESP32 para la sal del hash (`lib/expat/esp_random_shim.c`); los tests host
  que compilan expat incluyen ahora `xcs.c`.
- ArduinoJson 7.4.2 → 7.4.3 y NimBLE-Arduino 2.5.1 → 2.5.2.
- M5GFX 0.2.33 → 0.2.36 dentro de la serie 0.2.x; no se sube a 0.3.0 por el
  cambio de semántica de rotación. Build correcto; falta validar pantalla,
  rotación y refresco en hardware.

## 2026-11-08 — upstream `818a1540`

- CrossPoint actualizado de `5d731041` a `818a1540` (9 commits): historial de
  vocabulario del diccionario, `FtFont` compartido entre tamaños de la misma
  fuente, exclusión de carpetas especiales de la Library, fixes de portadas en
  Home/Classic y de navegación del diccionario.
- SDK sin cambios: sigue en `fb7e926`; `patches/sdk.patch` no cambia.
  `patches/firmware.patch` regenerado contra `818a1540`.
- El overlay de `scripts/sync-upstream.sh` conserva ahora `m5burner/`.
- Build `paperdiy` correcto: firmware 5.413.083 B, 82,6 % de la partición de
  app. Falta el smoke test en una unidad real antes de mergear a `paperdiy`.

## 2026-11-07 — compatibilidad con M5Launcher

- Añadido `src/platform/LauncherEnv`: detecta el firmware residente de
  [bmorcelli/Launcher](https://github.com/bmorcelli/Launcher) por su partición
  `APP_TEST` y lee la configuración de arranque de Launcher (`DDLB`,
  `LauncherOnKey`, `LauncherKeyLvl`), que registra en el log de arranque.
- Nuevo `Ajustes > Sistema > Salir a M5Launcher`, visible siempre bajo
  Launcher y adaptado a su modo de arranque: con tecla configurada pide
  mantenerla y reinicia con ella pulsada (`LauncherExitActivity`); sin tecla
  usa un deep sleep de 1 ms o, si `DeepSleep starts Launcher` está desactivado,
  un reset del ESP32 a través del M5PM1 (`SYS_CMD 0xA2`), que el bootloader ve
  como encendido.
- Documentada la configuración recomendada para despertar directamente en el
  lector: `CFG > GPIO on boot starts Launcher` = A. El sueño del PaperDIY es un
  apagado del PM1, así que despertar es un encendido; por defecto Launcher se
  muestra en cada encendido y `DeepSleep starts Launcher` no lo cambia. Con
  tecla configurada, el bootloader solo abre Launcher si A está pulsado.
- Bajo Launcher no se entra en el modo recuperación por SD al arrancar con A
  pulsado: es la forma de abrir Launcher.
- Bajo Launcher se ocultan `Buscar actualizaciones` y `Actualizar firmware por
  tarj. SD`; `OtaUpdater` y `FirmwareFlasher` rechazan escribir particiones OTA
  para no pisar otras apps ni el registro de Launcher.
- Nuevo `scripts/make_launcher_package.py` y `make launcher`: empaqueta el
  `firmware.bin` solo de aplicación como
  `PaperDIYReader-<versión>-launcher.bin` y genera el alias estable
  `PaperDIYReader-launcher.bin`. El workflow de release publica ambos; para
  instalar y actualizar hay que usar siempre el alias estable, porque Launcher
  crea una app por nombre de archivo y el archivo versionado crearía una app
  nueva.
- Documentación en `docs/paperdiy/13-m5launcher.md` (ES/EN) con instalación,
  actualización, salida a Launcher y notas de particiones.
- Validado en hardware (07/11/2026) con M5Launcher 3.0.0: instalación por
  consola serie (`flash firmware`), arranque, reentrada y actualización con
  `flash overwrite` conservando la SD y la posición de lectura. Salida a
  Launcher validada en los tres modos (deep sleep, reset del PM1 y tecla A).
  Con tecla A, suspender y encender arranca el lector directamente.
- Publicado el release `v0.1.0` con el `.bin` de Launcher y el factory
  image. Instalación limpia validada: borrado de 16 MB, M5Launcher 3.0.0
  oficial e instalación del asset desde la SD; la partición `paperd` coincide
  byte a byte con el release (`sha256 05f68e10…`) y se conservan los datos de
  la SD (`/.crosspoint/`) y la configuración de Launcher (`/config.conf`).

## 2026-11-06 — paquete M5Burner

- Añadido `m5burner/m5burner.json`, README de publicación y
  `scripts/make_m5burner_package.py`: genera un `.bin` para el diálogo Publish
  de M5Burner y un ZIP (`m5burner.json`, `firmware/`, portada, README y
  `LICENSE`) para la ruta de repositorio/PR.
- El paquete usa solo el build `paperdiy`; no incluye `paperdiy-test` ni
  credenciales NVS.
- `scripts/build_release_license.py` entiende el SDK vendorizado (no submódulo)
  y toma la revisión de `NOTICE`, necesario para el `LICENSE` GPLv3 del paquete.
- Checklist legal/publicación en `m5burner/README.md`: fuente por tag, avisos,
  LPPL pendiente y revisión de M5Stack.
- M5Burner usa versionado propio independiente de CrossPoint: primera
  publicación `0.1.0`; la base upstream va en la descripción.

## 2026-11-06 — upstream `5d731041` y SDK `fb7e926`

- CrossPoint actualizado de `bb93a462` a `5d731041` (About con tamaño/usado/libre
  de la SD).
- FreeInk SDK actualizado de `5e94fe7` a `fb7e926` (38 commits): mejoras de
  BLE HID, SD, táctil EEGO/Picco, waveforms Murphy y varios fixes.
- Conflictos resueltos en `BoardConfig.h` (renombrado de-link → Silkscreen
  conviviendo con PaperDIY) y en `AboutActivity` (filas SD + batería PM1 +
  controlador en vivo; 15 filas).
- `paperdiy` y `paperdiy-test` compilan; tests host de BLE, SD e InputManager
  pasan; About muestra SD 7,4 GB / 550 MB / 6,9 GB y batería 4,10 V / 100 %.
- `sdk.patch` y `firmware.patch` regenerados contra `fb7e926` y `5d731041`, y
  verificados aplicándolos sobre árboles limpios (pre y post-imagen).
- Las traducciones propias pasan a `firmware.patch`; el overlay ya no pisa
  `lib/I18n/translations` de upstream.
- `FirmwareBoardTag` reconoce el nuevo flag `FREEINK_DEVICE_SILKSCREEN`.

## 2026-11-06 — bring-up BLE

- El Keychron Q1 Pro no es un periférico BLE HID: no aparece en un escaneo
  CoreBluetooth del Mac y tampoco en el del PaperDIY; usa Bluetooth Classic,
  que el ESP32-S3 no soporta.
- Se levantó un teclado HID BLE de prueba en macOS con CoreBluetooth
  (`PaperDIY Test Keyboard`). El PaperDIY lo ve en el escaneo, pero el
  emparejamiento falla con `Pairing failed` (NimBLE `0x508`) incluso probando
  Secure Connections y sin cifrado. Falta un mando BLE real para cerrar la
  validación.
- El build de diagnóstico usó `FREEINK_BLE_HID_SHOW_UNNAMED_DEVICES`,
  `CONFIG_BT_NIMBLE_EXT_ADV` y `FREEINK_BLE_HID_SCAN_DEBUG`; se revirtió. El
  equipo queda con `paperdiy-test` normal y BLE desactivado.

## 2026-11-06 — sincronización con upstream `bb93a462`

- CrossPoint actualizado de `308cd522` a `bb93a462` (6 commits): remapeo de
  botones al soltar, `HalDisplay::controllerName()`, navegación/previsualización
  rotada, ajuste “Orient Side Buttons” y captura en EEGO A4.
- SDK FreeInk sin cambios de pin (`5e94fe7`); `sdk.patch` se reaplicó limpio.
- `firmware.patch` aplicó con un conflicto en `AboutActivity`: se combinó el
  nombre de controlador en vivo de upstream con la lectura de VBAT/estado del
  PM1 del fork.
- `paperdiy` y `paperdiy-test` compilan. Tests de remapeo y orientación pasan.
  Smoke test en hardware: arranque, Home, A/B, lectura y `About`
  (VBAT 4,08 V, 90 %, `LovyanGFX EPD`).
- `sdk.patch` y `firmware.patch` regenerados contra las bases nuevas y
  verificados con `git apply --check` sobre árboles limpios.
- KOReader Sync validado antes del sync contra un servidor KOSync local:
  autenticación, pull sin progreso, subida, comparación y aplicación de
  progreso remoto (página 13→17). Credenciales de prueba eliminadas después.

## 2026-11-06 — lectura larga y tiempos de refresco

- Lectura larga automatizada por USB: 250+ cambios de página (spines 10→24,
  varios capítulos) sin reinicios, errores de render ni fugas. Heap libre
  120,6–120,8 KB y PSRAM ~6,36 MB; mínimo transitorio de heap 81,7 KB.
- Tiempos medidos con los logs `ERS` (página completa, una sola base B/W porque
  el log no muestra pasada de grises): `fast` 569–620 ms de display (total
  651–726 ms); `text` limpio 1538–1542 ms (total 1637–1651 ms). Prewarm
  38–58 ms; render B/W 49–59 ms.
- `quality` no lo usa el port (`Full/Half` van a `epd_text`). Con un mapeo
  temporal `Half→quality` el refresco limpio midió 1538 ms, prácticamente igual
  que `text`; el código se restauró después de medir.
- La inyección `CMD:KEY` no reinicia el temporizador de actividad: a los 10 min
  el equipo se auto-suspendió en plena prueba y el USB desapareció. Power
  despertó conservando la página. Para pruebas largas hay que poner
  `Auto suspensión = Nunca` o hacer que el comando cuente como actividad; el
  ajuste se restauró a 10 min.
- La captura por serial devuelve el framebuffer: la estabilidad está validada,
  pero el ghosting físico tras la lectura larga sigue pendiente de revisión
  visual.

## 2026-11-05 — validación OPDS, fuentes y energía

- OPDS validado con Project Gutenberg: alta del servidor por la API web,
  navegación del catálogo, descarga de *Pride and Prejudice* a la raíz de la
  SD y lectura posterior. Standard Ebooks devuelve 401 y requiere
  credenciales.
- Estrés de paginación: 96 cambios de página sin entradas perdidas, reinicios
  ni fugas de heap/PSRAM. Página normal ~0,86 s; refresco completo cada 5
  páginas ~1,8 s (EPUB de texto, ruta B/W).
- Cambio de tamaño de fuente 14/16 pt y reflow verificados.
- BLE: el escaneo de mandos funciona; falta emparejar un mando real.
- CrossPoint Sync: pantalla de configuración correcta; falta probar el sync
  con credenciales.
- Auto-suspensión a 1 min con sleep screen de portada (`Fondo = Portada`,
  `Modo = Ajustar`); power despierta y conserva la página.
- Energía: A+B con USB en el equipo de prueba apagó vía PM1 y A no despertó;
  power encendió conservando la página. Corregida la nota de testing.
- La captura serial devuelve el framebuffer, no el ghosting físico del panel.
  Revisión visual tras 24 páginas: sin ghosting apreciable; falta lectura
  muy larga. El contador de páginas pasó de 1/35 a 1/50 al completarse la
  construcción de la sección.

## 2026-11-04 — sincronización con upstream

- CrossPoint actualizado a `308cd522` (18 commits): web/plugins, diccionario,
  bidi, selección de texto, fuentes TTF, traducciones y avisos de licencia.
- FreeInk SDK vendorizado en `5e94fe7`.
- `sdk.patch` y `firmware.patch` reaplicados sin conflictos.
- `scripts/sync-upstream.sh` recupera `patches/` tras cambiar a `main` y limpia
  el SDK vendorizado antes de inicializar el submódulo.
- Añadida la carcasa 3D `hardware/3d/PaperDIY_kit_completo.3mf`, un remix del
  modelo oficial del M5Stack PaperDIY Complete Kit (MIT).
- README principal, README de hardware, índice de documentación, guía de
  usuario y notas de hardware/port traducidos al inglés, chino simplificado y
  japonés (`*.en.md`, `*.zh-CN.md`, `*.ja.md`).
- Añadido el entorno `paperdiy-test` con `CMD:KEY` por USB y
  `scripts/paperdiy_serial.py` para capturas y pruebas de UI automatizadas.
- Corregida la recuperación de SD en caliente: reintentos de montaje y pantalla
  de error recuperable; al reinsertar la tarjeta reinicia y vuelve a Home.

## 2026-10-31 — refresco parcial y detección de SD

- `GfxRenderer::displayWindow()` y `HalDisplay::displayWindow()` exponen el
  refresco de una región; `LgfxEpdDriver` lo implementa sobre `Panel_EPD`
  empujando solo el rectángulo solicitado.
- `OptionPopup` refresca solo el diálogo y la tira de botones. Activado en
  Settings, File Browser, Library y el menú del lector. El resto de pantallas
  conserva el refresco completo.
- `SdPins.detect` (GPIO48 en PaperDIY, activo bajo) y
  `SDCardManager::isCardPresent()/remount()`. Al arrancar sin tarjeta se espera
  la inserción; en caliente se reintenta el montaje al insertar.
- Test host de SD ampliado con la lógica de card-detect.
- Log de diagnóstico de refresco parcial en `GFX`.
- El firmware se mantiene despierto mientras haya un host CDC USB conectado,
  para no competir con el auto-sleep durante desarrollo/flasheo.

## 2026-10-31 — batería, carga y PM1

- PaperDIY: curva de porcentaje propia para la celda de 140 mAh. El LGS4056H
  termina la carga y la celda queda en ~4,10 V; la curva genérica de 4,20 V
  mostraba 90 % con la batería llena. Ahora 4,10 V = 100 %.
- `About` muestra `VBAT`, porcentaje y estado de carga (charging/idle/USB) para
  diagnosticar la batería sin conectar el serial.
- El icono de rayo usa `CHG_STAT` real, no solo la presencia de USB.
- PM1: protección de baja tensión configurada a 3,4 V (`REG_BATT_LVP`).
- Log de arranque con `VBAT`, `VIN`, `5VOUT`, `PWR_SRC`, `PWR_CFG` y
  `GPIO_IN` para futuras calibraciones.
- Nota de hardware: el esquema K159 usa `R11=2K` en el LGS4056H (500 mA). Para
  la celda de 140 mAh era ~3,6C; una 604050 de ~2000 mAh queda en ~0,25C.

## 2026-10-31 — sincronización con upstream `b6605a51`

- `main` avanza de `31dc683f` a `b6605a51` (20 commits).
- SDK de FreeInk actualizado de `44427f8` a `2d383f8` (52 commits) y
  re-vendorizado; el port PaperDIY se reaplicó sobre la base nueva.
- Incluye mejoras de diccionario, fuentes, plugins, portal cautivo, imágenes
  de suspensión aleatorias y correcciones de red/UI de upstream.
- `patches/sdk.patch` y `patches/firmware.patch` regenerados contra las nuevas
  bases; `firmware.patch` ahora incluye también settings y UI propios.
- Build `paperdiy` correcto tras resolver el conflicto árbol/submódulo del SDK.

## 2026-10-31 — ajuste de ghosting al pasar página

- PaperDIY: se probó `cleanBankNeedsFreshBackground=true` con una LUT
  no-drive en `lutFastest`. No redujo el ghosting y añadía refrescos completos
  visibles, así que se revirtió.
- PaperDIY: `lutFast`/`lutFastest` usan ahora la waveform AA de ED047TC1 que
  ya usa el LilyGo T5 S3. Mantiene la base B/W y el plano de grises en el
  mismo offset de LUT, evita el flash negro de `lut_fast` y da un empuje
  específico a los grises del antialiasing.
- El intervalo de refresco limpio por defecto pasa de 15 a 5 páginas. La
  migración única también mueve el 1 heredado de la prueba anterior a 5 para
  evaluar la LUT con pasada rápida; después se respeta lo que elija el lector.
- `Settings > Display > Refresh Frequency` sigue permitiendo volver a 1 página.

## 2026-10-28 — primera validación PaperDIY

- Port de CrossPoint 2.0 a M5Stack PaperDIY K159:
  - perfil `M5PAPER_DIY` y `BoardPaperDiy`;
  - bus ED047TC1 en paralelo, rail EPD del M5PM1;
  - batería/carga por PM1 (VBAT, PWR_SRC, CHG_STAT);
  - botón power del PM1 como `BTN_POWER`;
  - shutdown en batería y deep sleep con wake A/B por USB;
  - framebuffer en PSRAM, OTA configurable y tag `paperdiy`.
- Fork downstream: `main` espejo de upstream, `paperdiy` de trabajo, SDK
  vendorizado y patches separados.
- Primera validación en hardware:
  - pantalla/UI correctas en vertical;
  - A/B, batería, SD FAT32 y lectura EPUB;
  - lectura de `Amar-o-depender.epub` y `Reconciliacion.epub`;
  - Wi-Fi, web UI y subida de libros verificadas.
- Fix de ghosting al abrir el menú del lector: la primera pintada usa
  `HALF_REFRESH` y limpia la página anterior; el resto de la navegación del
  menú sigue en `FAST_REFRESH`.
- Pendiente: OPDS, Calibre/KOReader Sync, consumo/autonomía, power/shutdown,
  wake, OTA y ghosting general tras muchas páginas.
