# 10 — Mantener el fork

Este repo es un fork downstream de CrossPoint. La regla es simple: **el motor
se sigue de upstream; el hardware y la UX PaperDIY viven en nuestro fork**.

Última sincronización: CrossPoint `8276d518` / FreeInk SDK `6a208c0c`
(10/11/2026).

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
   `.gitattributes`, `.gitignore`, `LICENSE`) desde `paperdiy`; añade las líneas
   downstream de `.agents/README.md` y los `CMakeLists` con
   `scripts/apply_downstream_overlay.py`.
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
`scripts/` (incluido el propio helper) tienen que estar ya en `paperdiy` antes de
ejecutar el sync: el overlay restaura `scripts/` desde esa rama.

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
  .agents/rules/release-versioning.md lib/expat test/firmware_version \
  docs/paperdiy docs/README.md docs/upstream scripts patches .github
rm -f ROADMAP.md SCOPE.md GOVERNANCE.md AGENTS.md USER_GUIDE.md CLAUDE.md .gitmodules
rm -rf .github && git checkout paperdiy -- .github

# Líneas del fork en ficheros que upstream también edita. Falla si el ancla
# cambió, en vez de sustituir el fichero entero y perder cambios de upstream.
python3 scripts/apply_downstream_overlay.py

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

| Patch | Base | Contenido |
|---|---|---|
| `patches/sdk.patch` | FreeInk SDK `6a208c0c` | perfil, BoardPaperDiy, PM1, InputManager, PowerManager, driver LGFX |
| `patches/firmware.patch` | CrossPoint `8276d518` | env, settings, UI, board tag, OTA, GfxRenderer, HalGPIO, HalPowerManager, main |
| `patches/paperdiy-support.patch` | ambos | concatenación de los dos anteriores |

Orden de aplicación: `sdk.patch` y luego `firmware.patch`.

## Pendientes de la sync `8276d518` (10/11/2026)

Estado: merge `a9cff597` en `paperdiy`, sin release. Hecho: pins de `NOTICE`,
`CHANGELOG.md` y `docs/paperdiy/06-porting.*`; smoke registrado en
`12-serial-testing.md`; `sdk-baseline` recreada en `6a208c0c` y los tres parches
regenerados y verificados con `git apply --check` contra `8276d518` /
`6a208c0c`. Antes de publicar `2.0.0-3`:

- El overlay de `sync-upstream.sh` restaura `NOTICE`, `CHANGELOG.md` y
  `docs/paperdiy` desde `paperdiy`; en el próximo sync hay que llevar estos
  cambios a `paperdiy` antes del overlay.
- Riesgo upstream aceptado en `SecureHttpClient::readHeaderLine`: una respuesta
  con exactamente 64 cabeceras, o cuyo presupuesto de 8 KB se agote en la línea
  en blanco final, puede rechazarse. No divergir del SDK sin necesidad; si se
  corrige, hacerlo como parche del fork y añadir test.
- El «un solo refresco» del Home es con caché caliente. Con caché fría o cambio
  de altura de miniatura siguen los refrescos de popup por portada generada
  (comportamiento previo, no regresión); no se ha instrumentado el contador.
- Smoke pendiente: ghosting/autonomía, sleep/wake, USB MSC, BLE, OPDS/Calibre y
  una instalación OTA completa.

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
  sincronizado (hoy `2.0.0`, `8276d518`). No se inventa ni se sube por libre.
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
- [ ] `scripts/flash.sh` rechaza placas que no sean de 16 MB.
- [ ] Backup del firmware original.
- [ ] Flash factory en una unidad real.
- [ ] Pantalla/rotación/ghosting.
- [ ] A/B, power PM1, A+B, wake.
- [ ] Batería/carga, sleep current, autonomía.
- [ ] SD, Wi-Fi, OPDS/Calibre, OTA.
- [ ] Recuperación por download mode.
- [ ] Release notes incluyen el aviso de OTA bajo M5Launcher y el enlace a
      `13-m5launcher.md`.
- [ ] Changelog y artefactos.
