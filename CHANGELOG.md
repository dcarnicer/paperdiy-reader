# Changelog

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
- Nuevo `Ajustes > General > Salir a M5Launcher`, visible siempre bajo
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
