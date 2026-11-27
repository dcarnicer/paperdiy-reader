# 10 — Mantener el fork

Este repo es un fork downstream de CrossPoint. La regla es simple: **el motor
se sigue de upstream; el hardware y la UX PaperDIY viven en nuestro fork**.

Última sincronización: CrossPoint `dd86a5ec` / FreeInk SDK `de19f154`
(27/11/2026).

## Ramas y remotos

| Rama | Qué es |
|---|---|
| `main` | Espejo local de `upstream/develop` (sin cambios nuestros) |
| `paperdiy` | Nuestro fork: `main` + FreeInk SDK vendorizado + port + docs |
| `sdk-baseline` | Rama local con el SDK pristine del pin, solo para generar `sdk.patch` |

`paperdiy-next` es una rama temporal que crea `scripts/sync-upstream.sh` para
preparar el siguiente sync; no se conserva entre sincronizaciones. El historial
anterior a la reestructuración queda archivado en el tag
`archive/pre-restructure-2026-10-28`.

Remotos:

```bash
git remote -v
# upstream  https://github.com/crosspoint-reader/crosspoint-reader.git
```

`main` sigue a `upstream/develop`. `paperdiy` es la rama de trabajo.

## Por qué el SDK está vendorizado

Upstream tiene `freeink-sdk` como submódulo. Para que el fork se clone y
componga sin depender de un commit de submódulo, `paperdiy` lo vendoriza como
archivos normales. Es la divergencia estructural principal; el pin de expat
2.10.0 es la otra dependencia vendorizada que el fork mantiene por su cuenta.

Ventaja: `make build` funciona en cualquier clon.
Coste: al actualizar upstream hay que re-vendorizar el SDK y reaplicar
`patches/sdk.patch`.

## Actualizar desde upstream

### Comprobación

```bash
git fetch upstream --prune
git log --oneline main..upstream/develop
```

### Comprobación rutinaria (CrossPoint, SDK y M5)

```bash
make check-upstreams
```

`scripts/check_upstreams.py` es de solo lectura y revisa siempre las mismas
fuentes contra las bases de `scripts/upstreams.json`: CrossPoint, el pin del SDK
FreeInk y los repos de M5 de los que salieron componentes (M5GFX, M5PM1,
M5IOE1, M5PaperDIY-UserDemo, M5PaperS3-UserDemo, uiflow-micropython, M5Unified
y M5_Hardware). Clasifica ficheros nuevos, dependencias y posibles componentes;
no sincroniza nada. La primera ejecución clona esos repos en
`~/.cache/paperdiy-reader/upstream-check`, fuera del repositorio; las
siguientes reutilizan la caché.

La skill `upstream-sync` obliga a ejecutar este chequeo antes de responder a
una petición de actualización. Si se acepta un cambio de base, se actualiza a
mano en `scripts/upstreams.json`; el script no mueve las bases solo.

El pin de CrossPoint manda: no se vendorizan commits del `main` del SDK que
CrossPoint todavía no pinnea, ni se sube M5GFX de versión sin compilar y probar
en hardware.

### Actualización asistida

```bash
./scripts/sync-upstream.sh --apply
```

El script:

1. Actualiza `main` con `--ff-only`.
2. Crea `paperdiy-next` desde `main`.
3. Vendoriza el SDK del nuevo upstream.
4. Aplica `patches/sdk.patch` y `patches/firmware.patch` con `--3way`.
5. Copia docs, Makefile, scripts, workflows y los ficheros con edición del fork
   (`.agents/rules/release-versioning.md`, `lib/expat`, `test/firmware_version`,
   `test/test_release_license.py`, `test/test_battery_log.py`, las pruebas de
   los scripts del fork, `AGENTS.md`, `CLAUDE.md`, `.gitattributes`,
   `.gitignore`, `LICENSE`) desde `paperdiy`; añade las líneas
   downstream de `.agents/README.md` y los `CMakeLists` con
   `scripts/apply_downstream_overlay.py`, y apunta en `NOTICE` el commit de
   CrossPoint y el pin del SDK nuevos con `scripts/update_notice_pins.py`.
6. Deja el árbol listo e imprime el comando `make build`; la compilación es
   manual.

Si hay conflictos, el script se detiene para resolverlos a mano. No borra
`paperdiy`; la revisión y el cambio de rama son manuales. Si upstream toca
`lib/expat`, `.gitattributes`, `.gitignore` o `LICENSE` (ficheros compartidos que
el overlay reemplaza), el script se detiene antes de mergear: hay que
reconciliar la edición del fork con la versión nueva en vez de pisarla.

`scripts/apply_downstream_overlay.py` solo añade las líneas propias del fork en
`.agents/README.md`, `test/CMakeLists.txt` y
`test/koreader_xpath_resolver/CMakeLists.txt`. Valida todas las anclas antes de
escribir y falla sin tocar el árbol si upstream movió alguna. Los cambios en
`scripts/` (incluido el propio helper) y en `.agents/skills/upstream-sync`
tienen que estar ya en `paperdiy` antes de ejecutar el sync: el overlay los
restaura desde esa rama.

### Actualización manual

```bash
# debe estar vacío: si no, reconcilia el overlay del fork antes de seguir
git diff --stat main..upstream/develop -- lib/expat .gitattributes .gitignore LICENSE

git checkout main
git merge --ff-only upstream/develop
git checkout -b paperdiy-next main

# vendorizar el SDK nuevo (sin .git)
git submodule update --init --recursive freeink-sdk
rm -rf /tmp/sdk-new && cp -R freeink-sdk /tmp/sdk-new
git rm -f freeink-sdk
mkdir -p freeink-sdk
rsync -a --exclude='.git' /tmp/sdk-new/ freeink-sdk/
git add freeink-sdk

# aplicar el port
git apply --3way patches/sdk.patch
git apply --3way patches/firmware.patch

# docs/infra y ficheros enteros del fork
git checkout paperdiy -- README.md README.en.md README.ja.md README.zh-CN.md \
  CHANGELOG.md Makefile NOTICE LICENSE .gitignore .gitattributes hardware m5burner \
  .agents/rules/release-versioning.md .agents/skills/upstream-sync \
  lib/expat test/firmware_version test/test_release_license.py test/test_battery_log.py \
  test/test_pio_core_dir.py test/test_pio_lock.py test/test_flash_script.py \
  test/test_m5burner_packages_dir.py AGENTS.md CLAUDE.md \
  docs/paperdiy docs/README.md docs/upstream scripts patches .github
rm -f ROADMAP.md SCOPE.md GOVERNANCE.md USER_GUIDE.md .gitmodules
rm -rf .github && git checkout paperdiy -- .github

# Líneas del fork en ficheros que upstream también edita. Falla si el ancla
# cambió, en vez de sustituir el fichero entero y perder cambios de upstream.
python3 scripts/apply_downstream_overlay.py

# NOTICE: commit de CrossPoint y pin del SDK del sync. El LICENSE de la release
# lee de aquí la revisión del SDK vendorizado.
python3 scripts/update_notice_pins.py

# Refrescar el snapshot de docs de upstream
for doc in README AGENTS GOVERNANCE ROADMAP USER_GUIDE; do
  git show main:"${doc}.md" > "docs/upstream/${doc}-crosspoint.md"
done

make build
```

Si el build y el smoke test de hardware pasan:

```bash
git diff paperdiy-next   # debe quedar vacío antes de regenerar parches
git checkout paperdiy
git merge --no-ff -X theirs paperdiy-next
git diff paperdiy-next   # debe quedar vacío tras el merge
```

`paperdiy-next` nace de `main` y lleva el port reaplicado como parche, no
comparte los commits downstream de `paperdiy`; por eso el merge no puede ser
`--ff-only`. Como `paperdiy-next` ya contiene el árbol final (upstream + port +
docs + SDK vendorizado), `-X theirs` resuelve los conflictos de SDK/parches a
favor del árbol nuevo; `git diff paperdiy-next` debe quedar vacío.

Después del merge hay que regenerar los parches contra las bases nuevas. El
`paperdiy-next` deja de coincidir con `paperdiy` solo por estos artefactos:

```bash
# sdk-baseline debe tener el SDK pristine del pin actual, sin cambios del port.
git diff sdk-baseline..paperdiy -- freeink-sdk > patches/sdk.patch
git diff main..paperdiy -- platformio.ini src lib/GfxRenderer lib/hal lib/JsonParser lib/I18n/translations > patches/firmware.patch
cat patches/sdk.patch patches/firmware.patch > patches/paperdiy-support.patch
git apply --check patches/sdk.patch   # sobre un worktree de sdk-baseline
git apply --check patches/firmware.patch  # sobre un worktree de main
```

Si `sdk-baseline` está desactualizada, recrearla desde el pin del submódulo
antes de generar el patch:

```bash
git checkout -B sdk-baseline main
rm -rf freeink-sdk  # el árbol vendorizado tapa el checkout del submódulo
git submodule update --init --recursive freeink-sdk
rm -rf /tmp/sdk-pristine && cp -R freeink-sdk /tmp/sdk-pristine
git rm -rf -q freeink-sdk
mkdir -p freeink-sdk && rsync -a --exclude='.git' /tmp/sdk-pristine/ freeink-sdk/
git add freeink-sdk && git commit -m "chore: vendor pristine SDK for patch baseline"
```

## Patches

| Patch | Base (destino) | Contenido |
|---|---|---|
| `patches/sdk.patch` | FreeInk SDK `de19f154` | perfil, BoardPaperDiy, PM1/I2C lock, InputManager, PowerManager, driver LGFX, batería; SDK #218 (ws397) |
| `patches/firmware.patch` | CrossPoint `dd86a5ec` | env, settings, UI, board tag, OTA, GfxRenderer, HalGPIO, HalPowerManager, main, batería; CrossPoint #3386 y envs ws397 |
| `patches/paperdiy-support.patch` | ambos | concatenación de los dos anteriores |

Orden de aplicación: `sdk.patch` y luego `firmware.patch`. Hasta regenerarlos
tras el merge, los parches del árbol siguen usando las bases del release
anterior.

### No reformatear el SDK vendorizado

`patches/sdk.patch` se genera como diff contra el SDK pristine de
`sdk-baseline`. No reformatees ni reordenes los archivos vendorizados
(`clang-format`, formato al guardar, saltos de línea o imports): ese ruido entra
en el parche, lo hincha y aumenta el riesgo de conflictos en el próximo
`git apply --3way`. Mantén los cambios limitados a hunks funcionales y regenera
el parche solo para esos hunks.

## PRs de upstream que llevamos

El fork lleva commits de PRs de upstream que aún no están fusionados. Al
regenerar `patches/` quedan mezclados con el port de PaperDIY, así que se
listan aquí para poder quitarlos cuando upstream los fusione.

| PR | Commits originales | Qué aporta |
|---|---|---|
| [FreeInk SDK #218](https://github.com/Free-Ink/freeink-sdk/pull/218) | `b328dc5b`, `0d20526e`, `906acd9c`, `a6c2c543` (aquí `a621e5ea`, `53e837b1`, `6f89481e`, `fa49c49e`) | ws397: HALF con la secuencia rápida del fabricante, apagado tras grises, `hasHorizontalKeys()`, config 3.97 solo para ws397 |
| [CrossPoint #3386](https://github.com/crosspoint-reader/crosspoint-reader/pull/3386) | `366ee088`, `c499e274`, `58d647e2`, `30910d4e` | envs ws397, board tag, teclado sin izquierda/derecha, pistas ocultas sin botones frontales, Atrás/encendido compartidos |

Cambios propios del fork encima de esos PRs:

- `[env:ws397]` y `[env:ws397-test]`: versión del fork, OTA a nuestras
  releases, PSRAM y flash QIO como `paperdiy`. Upstream tiene `ws397` sobre
  `firmware_tuned`, con sufijo `-ws397` y un `ws397-gh_release` aparte.
- `BaseTheme::buttonHintsHidden()` excluye `DigitalTwoButton`, para que la
  PaperDIY conserve la fila de pistas. `OptionPopup` usa ese mismo criterio.
- CI: `build-paperdiy.yml` compila también `ws397` y comprueba las imágenes de
  las dos placas; la release publica dos imágenes por placa.
- `[env:ws397]` activa la unidad USB (`FREEINK_CAP_USB_MSC`). Upstream compila
  `ws397` sobre `firmware_tuned`, cuyo core no lleva TinyUSB: al sincronizar,
  conservar nuestro env o se pierde la unidad USB.
- OPDS en placas con solo teclas laterales y sin táctil (PaperDIY, ws397):
  bloque propio al principio de `OpdsBookBrowserActivity::handleCustomInput()`
  y etiquetas de página en `drawFooter()`; la rama de upstream que reserva
  las teclas laterales para las páginas del feed queda intacta.
  `CatalogActivity` abre la búsqueda cuando pulsar y soltar llegan juntos
  (dos botones).

Al fusionar una rama que añade commits de este tipo, regenera `patches/` en el
mismo momento: `sync-upstream.sh` reconstruye `paperdiy-next` desde esos
parches, y un sync con parches viejos perdería esos commits sin avisar.

Cuando upstream fusione uno de estos PRs: en el sync, quédate con la versión
de upstream de sus hunks, conserva solo los cambios propios de arriba y borra
la fila de la tabla. Si el `[env:ws397]` de upstream entra en `platformio.ini`,
deja uno solo.

## Sync `dd86a5ec` (27/11/2026)

CrossPoint `a2b0d48b` → `dd86a5ec` (2 commits); el pin del SDK sigue en
`de19f154`. Los parches aplicaron sin conflictos y `patches/` no cambia: ningún
fichero que cambia upstream está en el port. Detalle y checks en el CHANGELOG.

## Release `2.1.0-1` (26/11/2026)

Sincronización con CrossPoint `a2b0d48b` / FreeInk SDK `de19f154`. Upstream
sube `[crosspoint] version` a `2.1.0` (`cfc76112`; tag `2.1.0rc` en
`d2270389`), así que la numeración del fork se reinicia en `2.1.0-1`.

El sync se preparó en dos tandas: hasta `d2270389` (conflictos resueltos en
`SDCardManager`, que conserva `StartupError` de upstream y
`isCardPresent`/`unmount`/`remount` del fork; el stub `SdFat.h`; y
`OpdsBookBrowserActivity`, donde upstream ya incluye nuestro #4576) y después
los cuatro commits hasta `a2b0d48b`. En esa segunda tanda solo chocaron las
traducciones ES/CA/VA: upstream (#4624) ya traduce cadenas que el fork
traducía por su cuenta (Sync On Sleep, pulsación larga, vocabulario, OPDS,
fuente de la interfaz, índice de la biblioteca). Se adoptan las de upstream y
el fork solo conserva las del perfil de batería; se eliminaron las claves
duplicadas `STR_UI_FONT` y `STR_UI_FONT_LOAD_FAILED`. Se quitan de la tabla
de PRs el `main` del SDK (CrossPoint ya fija `de19f154`) y CrossPoint #4576
(fusionado).

- Builds, tests y smoke: ver el CHANGELOG.
- El camino `@font-face` es nuevo y viene de upstream. Pendiente de medir en
  hardware el coste de un EPUB con fuentes incrustadas (PSRAM y reintentos si
  una fuente está corrupta), las fuentes distintas por página y el ghosting
  del camino PSRAM.

## Release `2.0.0-11` (22/11/2026)

Sincronización con CrossPoint `177d0694` / FreeInk SDK `995d9bd5`; mantiene
CrossPoint `2.0.0`. Conflictos resueltos en `BoardConfig.h` (E1001 junto a
PaperDIY), `HalPowerManager` (el nuevo `readBatteryPercentage` del Wi-Fi al
dormir usa la presentación de batería de PaperDIY bajo el mutex) y `main.cpp`.
Upstream quitó `UiListActivity::cleanNextRefresh` (`79ae14ff`); el fork lo
conserva porque el menú del lector lo usa para limpiar la página de debajo.
Parches regenerados y verificados con `git apply --check`.

- Build `paperdiy`: `firmware.bin` 5.528.960 B, 84,3 % de flash y 34,1 % de
  RAM. `paperdiy-test` compila; 1027 tests de host.
- Smoke 25/25 sobre el árbol del sync (`20261122-193337`); `2.0.0-11` solo
  cambia la versión y añade la traducción ES/CA/VA de `Sync On Sleep`.
- El build de producción `2.0.0-11` se flasheó en el PaperDIY y arranca en
  Home con el estado del usuario.
- `test/test_firmware_stats.py` falla en el fork desde antes de este sync: usa
  `.github/scripts/firmware-stats.py`, que el overlay de `.github` no lleva.
- Pendientes: ghosting (también el menú del lector), autonomía, sleep/wake,
  Sync On Sleep real, BLE real, Calibre completo y OTA completa; subida manual
  a M5Burner.

## Release `2.0.0-10` (19/11/2026)

Sincronización con CrossPoint `209cb53a` / FreeInk SDK `634a3f8c`; mantiene
CrossPoint `2.0.0`. Conflictos resueltos en `HalStorage` (se conservan
`ready`, `isCardPresent` y `remount`), `AboutActivity` (fila de batería sobre
el nuevo `ITEM_COUNT`) y `OtaUpdater` (camino de Launcher). Parches
regenerados y verificados con `git apply --check`.

- Build `paperdiy`: `firmware.bin` 5.446.032 B, 83,0 % de flash y 33,9 % de
  RAM. `paperdiy-test` compila.
- Smoke 25/25 sobre el árbol del sync (`20261119-120845`); `2.0.0-10` solo
  cambia la cadena de versión respecto a ese build.
- El build de producción `2.0.0-10` se flasheó en el PaperDIY y arranca en
  Home con el estado del usuario.
- Pendientes: ghosting, autonomía, sleep/wake, BLE real, Calibre completo y
  OTA completa; subida manual a M5Burner.

## Release `2.0.0-9` (18/11/2026)

Sincronización con CrossPoint `b6b7a6c1` / FreeInk SDK `77ae8c75`. Mantiene
CrossPoint `2.0.0`.

- Upstream: botones laterales en diccionario, liberación de cachés de fuentes
  al cerrar capítulos, opción de Recientes solo con libros abiertos, mensaje de
  error OPDS con redirects, fixes de EEGO A4/Picco y versión branch+hash.
- Port: conflictos resueltos en `CrossPointSettings`, `UiListActivity`
  (`cleanNextRefresh` de upstream sustituye a `cleanFirstRender`),
  `AboutActivity` (15 filas / 16 en EEGO) e `InputManager` (A+B + PaperDIY).
- PM1: el bus I²C se comparte con `I2cBusLock`, se configura una sola vez y el
  estado de batería se cachea durante `BATTERY_POLL_MS`; evita reinit y reads
  entre tareas.
- `Display Refresh` eliminado de Ajustes; las guías usan `Refresh Screen` +
  `Refresh Frequency`.
- Traducciones ES/CA/VA para las cadenas nuevas de Recientes.
- Build `paperdiy`: `firmware.bin` 5.446.272 B, 83,0 % de flash y 33,9 % de
  RAM. Tests: 935 host, `paperdiy-test` compila y `make smoke` 25/25
  (`20261118-132153`).
- Hardware: smoke completo sobre `paperdiy-test`; pendientes ghosting,
  autonomía, sleep/wake, BLE real, Calibre completo y OTA completa.

## Release `2.0.0-8` (16/11/2026)

Sincronización con CrossPoint `490813ff` / FreeInk SDK `3f3e4c1` y arreglos de
validación del port. Mantiene CrossPoint `2.0.0`.

- Upstream: desambiguación de gestos del botón power en reinicios suaves,
  arreglos varios de lector, Home, WebDAV, descarga de fuentes y servidor web,
  y stats de flash/RAM en CI.
- Port: reaplicado sobre el SDK nuevo. Los pulsos del PM1 se normalizan como
  clicks (duración 0) y el click que despierta no se reenvía a la app.
- Perfil de batería: el cambio Kit/Extendida se aplica en caliente desde la UI
  y la web, y persiste en `settings.json` con validación y fallback al kit.
- Traducción española de `Display Refresh`.
- Build `paperdiy`: `firmware.bin` 5.445.184 B, 83,0 % de flash y 33,9 % de
  RAM. Tests: 18 Python, 933 host, PMIC PaperDIY y `make smoke` 25/25
  (`20261116-194343`).
- Hardware: wake-click tras A+B, SD en caliente, persistencia y cambio web del
  perfil de batería validados. Pendiente el salto visual de la curva con
  batería <90 % y la autonomía.

## Release `2.0.0-7` (15/11/2026)

Corrección de la presentación de batería en carga sobre la `2.0.0-6`. Sin
cambios upstream: sigue CrossPoint `36b9430e` / FreeInk SDK `a8acebf`.

- Mientras hay USB, el porcentaje se congela en el último valor de descarga; al
  completar la carga muestra 100 % y, tras desenchufar, espera ~2 min antes de
  volver a la curva.
- El último porcentaje se guarda en NVS para sobrevivir al apagado.
- El hook `BATHOLD` es solo de `paperdiy-test`; no está en producción.
- Verificado en el PaperDIY: con el cargador aún activo, `BATHOLD:55` muestra
  55 % y el log registra `4168 mV / 55 % / chg=1`; el build de producción
  `2.0.0-7` arranca en Home.
- Build `paperdiy`: 5.438.679 B, 83,0 % de flash y 33,9 % de RAM.

## Release `2.0.0-6` (15/11/2026)

Estado: release `2.0.0-6` publicada (tag `v2.0.0-6`) sobre CrossPoint
`36b9430e` / FreeInk SDK `a8acebf`.

- Upstream: mejoras de refresco EPD para todos los paneles, optimizaciones TTF,
  profundidad de bits XTC, chevron de página anterior y los fixes de la sync
  anterior (Controles agrupados en la web y scroll de `OptionPopup`).
- Port: reaplicado sobre el SDK nuevo. Conflictos resueltos en la política
  PSRAM de `BoardConfig.h` y en las ventanas de refresco de `GfxRenderer.h`.
- Batería: log de descarga, `CMD:BATLOG`, modo de page-turning de test, curva
  medida de la 604050 (45,4 h / 5.448 páginas) y perfil kit/extendida. Todo
  forma parte de `paperdiy` en esta release.
- `patches/sdk.patch`, `patches/firmware.patch` y
  `patches/paperdiy-support.patch` regenerados y verificados con
  `git apply --check` contra `36b9430e` / `a8acebf`.
- Smoke básico de hardware de la release: Home, lector, giro de página, ajustes
  y perfil de batería (Extendida) OK. Pendiente la revisión visual de ghosting
  y sleep/wake.
- Smoke histórico pendiente: BLE real, Calibre completo y OTA completa.

> **Regresión.** La última ejecución completa de `make smoke` es la del
> 18/11/2026 sobre el árbol del sync `b6b7a6c1` (run `20261118-132153`, PASS 25
> pasos). `2.0.0-6` no tiene una ejecución propia. Queda pendiente completar la
> revisión de ghosting, autonomía y el salto visual de la curva de batería. Los
> resultados históricos no se reescriben como si hubieran pasado.

## OTA

El env `paperdiy` de `platformio.ini` fija dos cosas de la OTA standalone:

- `CROSSPOINT_OTA_RELEASES_URL`: las releases de este fork
  (`dcarnicer/paperdiy-reader`). Así un build local y el de CI son iguales.
- `CROSSPOINT_OTA_ASSET_FORMAT` = `crosspoint-paperdiy-%%s-ota.bin`: el
  nombre del asset que busca, con la versión del tag sin la `v`. El `%%` es el
  escape de `%` en `platformio.ini`.

El workflow `.github/workflows/release-paperdiy.yml` publica exactamente dos
`.bin`, que comprueba `scripts/check_release_assets.py` (la app de la imagen
completa debe ser idéntica a la de la OTA):

- `crosspoint-paperdiy-latest.bin`: imagen completa (`0x0`) para M5Burner,
  M5Launcher y esptool. Nombre fijo para que
  `releases/latest/download/crosspoint-paperdiy-latest.bin` dé siempre la
  última.
- `crosspoint-paperdiy-<versión>-ota.bin`: solo la app, para la OTA
  standalone.

Además adjunta `SHA256SUMS.txt` y `LICENSE`. Los binarios son GPLv3 porque
incluyen wolfSSL, así que cada release lleva los textos de licencia, los avisos
de terceros y las revisiones del código y del SDK
(`scripts/build_release_license.py`), y las notas lo indican. La revisión del
SDK sale de `NOTICE`; `python3 scripts/update_notice_pins.py --check` debe
pasar antes de crear el tag.

Tag: `v<versión>` (por ejemplo `v2.0.0-1`, ver Versionado).

Bajo M5Launcher el lector **no escribe en la flash**: `installUpdate` devuelve
`LAUNCHER_MANAGED` y `FirmwareFlasher` rechaza escribir otra partición.
`Verificar actualizaciones` consulta LauncherHub, que replica M5Burner, así
que **cada release debe subirse también a M5Burner** con el mismo nombre
(`CrossPoint for PaperDIY (community port)`) para que el aviso la vea: se sube
`crosspoint-paperdiy-latest.bin` y en el campo de versión va la del tag sin la
`v`. Ver `13-m5launcher.md`.

**No publiques** un `firmware.factory.bin` con `ota_0` si estás usando el
dual-boot de la PR de prateek; aquí no lo usamos.

## Versionado

La versión es la de CrossPoint sobre la que se construye más una revisión del
port, para que se vea de un vistazo qué upstream lleva cada release:
`<CrossPoint X.Y.Z>-<N>` (por ejemplo `2.0.0-1`). Es corta a propósito: el
campo de versión de M5Burner no admite cadenas largas y tiene que coincidir con
la de la release.

- `X.Y.Z` es `[crosspoint] version` de upstream `main` en el commit
  sincronizado (hoy `2.0.0`, `fa17b9ca`). No se inventa ni se sube por libre.
- `N` empieza en 1 y sube en cada release pública (fixes, features, docs).
  Un sync a otra versión de CrossPoint lo reinicia: `2.1.0-1`.
- Tag `v2.0.0-1`; `[crosspoint] version` / `CROSSPOINT_VERSION` es
  la misma cadena sin la `v`.
- RC: `v2.0.0-2-rc.1`; el workflow la publica como pre-release y no
  aparece en `/releases/latest`. No se sube a M5Burner.
- Los builds locales de `paperdiy` llevan la versión tal cual; no se publican.
- Nunca se reutiliza un tag; para reconstruir una release se sube `N`.
- Orden (`src/network/FirmwareVersion.h`, OTA de GitHub y aviso de
  LauncherHub): versión de CrossPoint, luego `N`, y una RC antes de su release.
- El commit upstream y el pin del SDK van en el CHANGELOG y en las notas.
- Todas las versiones subidas a M5Burner siguen este esquema: el aviso coge la
  más alta del catálogo, y una `2.1.0` suelta se ofrecería a todos los
  `2.0.0-N`.
- `v0.1.0` y `v2.1.0` son anteriores a este esquema; `v2.1.0` se retiró de
  GitHub antes de publicar `v2.0.0-1`. Un aparato en 2.1.0
  (standalone o bajo Launcher) la compara como más nueva y hay que
  actualizarlo una vez a mano.
- El workflow de release valida tag y versión con
  `scripts/check_release_version.py`.
- Changelog con: upstream base, cambios PaperDIY, hardware validado, notas de
  flash.
- `firmware.factory.bin` siempre probado en una unidad antes de publicar.
- Regla operativa para agentes:
  [`release-versioning.md`](../../.agents/rules/release-versioning.md).

## Qué se queda downstream

- Perfil PaperDIY, PM1, botones, energía.
- Pin de expat 2.10.0 (incluye `xcs.c` y el shim de RNG del ESP32) y los tests
  de `FirmwareVersion`.
- UX de dos botones y atajos.
- BLE page turner, USB MSC (cuando se validen).
- Diccionario español, colecciones/stats, exportar citas.
- Formatos extra (FB2/MD/HTML/CBZ) y flujo PDF.
- Mods de hardware (batería, RTC, encoder, Hall).

## Qué se intenta upstream

- Perfil de placa y driver de panel (limpios, sin features de producto).
- Cambios de `HalGPIO`/`HalPowerManager`/`main` que no sean PaperDIY-specific.
- Correcciones de OTA o de build que beneficien a todos.

La issue [#4005](https://github.com/crosspoint-reader/crosspoint-reader/issues/4005)
sigue abierta. Sin hardware validado no hay aceptación; el fork no depende de
eso.

## Checklist antes de release

- [ ] `main` actualizado y `paperdiy` rebasado.
- [ ] `make build` limpio.
- [ ] `make smoke` con `paperdiy-test` sin fallos.
- [ ] `scripts/flash.sh` flashea una placa de 16 MB y rechaza las demás.
- [ ] Backup del firmware original.
- [ ] Flash factory en una unidad real.
- [ ] Pantalla/rotación/ghosting.
- [ ] A/B, power PM1, A+B, wake.
- [ ] Batería/carga, sleep current, autonomía.
- [ ] SD, Wi-Fi, OPDS/Calibre, OTA.
- [ ] Recuperación por download mode.
- [ ] Release notes incluyen el aviso de OTA bajo M5Launcher y el enlace a
      `13-m5launcher.md`.
- [ ] `NOTICE` al día: `python3 scripts/update_notice_pins.py --check`.
- [ ] Changelog y artefactos; la release incluye `LICENSE`.
- [ ] Descripción de M5Burner con la licencia (GPLv3) y el enlace al código.
