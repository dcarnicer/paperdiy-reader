# 10 — Mantener el fork

Este repo es un fork downstream de CrossPoint. La regla es simple: **el motor
se sigue de upstream; el hardware y la UX PaperDIY viven en nuestro fork**.

Última sincronización: CrossPoint `818a1540` / FreeInk SDK `fb7e926`
(08/11/2026).

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
archivos normales. Es la única divergencia estructural importante.

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
5. Copia docs, Makefile, scripts y workflows desde `paperdiy`.
6. Compila `paperdiy`.

Si hay conflictos, el script se detiene para resolverlos a mano. No borra
`paperdiy`; la revisión y el cambio de rama son manuales.

### Actualización manual

```bash
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

# docs/infra
git checkout paperdiy -- README.md README.en.md README.ja.md README.zh-CN.md \
  CHANGELOG.md Makefile NOTICE LICENSE .gitignore .gitattributes hardware m5burner \
  docs/paperdiy docs/README.md docs/upstream scripts patches .github
rm -f ROADMAP.md SCOPE.md GOVERNANCE.md AGENTS.md USER_GUIDE.md CLAUDE.md .gitmodules
rm -rf .github && git checkout paperdiy -- .github

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
git diff main..paperdiy -- platformio.ini src lib/GfxRenderer lib/hal lib/I18n/translations > patches/firmware.patch
cat patches/sdk.patch patches/firmware.patch > patches/paperdiy-support.patch
git apply --check patches/sdk.patch   # sobre un worktree de sdk-baseline
git apply --check patches/firmware.patch  # sobre un worktree de main
```

Si `sdk-baseline` está desactualizada, recrearla desde el pin del submódulo
antes de generar el patch:

```bash
git checkout -B sdk-baseline main
git submodule update --init --recursive freeink-sdk
rm -rf /tmp/sdk-pristine && cp -R freeink-sdk /tmp/sdk-pristine
git rm -rf -q freeink-sdk
mkdir -p freeink-sdk && rsync -a --exclude='.git' /tmp/sdk-pristine/ freeink-sdk/
git add freeink-sdk && git commit -m "chore: vendor pristine SDK for patch baseline"
```

## Patches

| Patch | Base | Contenido |
|---|---|---|
| `patches/sdk.patch` | FreeInk SDK `fb7e926` | perfil, BoardPaperDiy, PM1, InputManager, PowerManager, driver LGFX |
| `patches/firmware.patch` | CrossPoint `818a1540` | env, settings, UI, board tag, OTA, GfxRenderer, HalGPIO, HalPowerManager, main |
| `patches/paperdiy-support.patch` | ambos | concatenación de los dos anteriores |

Orden de aplicación: `sdk.patch` y luego `firmware.patch`.

## OTA

El código usa `CROSSPOINT_OTA_RELEASES_URL`, por defecto el repo oficial de
CrossPoint. Eso es **seguro**: el asset se busca como
`crosspoint-<tag>-paperdiy.bin`, que no existe en las releases oficiales, así
que el PaperDIY no se actualiza con firmware ajeno.

Para publicar releases propias, descomenta en `platformio.ini`:

```ini
-DCROSSPOINT_OTA_RELEASES_URL=\"https://api.github.com/repos/TUUSUARIO/paperdiy-reader/releases/latest\"
```

El workflow `.github/workflows/release-paperdiy.yml` ya compila y publica:

- `crosspoint-<tag>-paperdiy.bin` (asset que consume la OTA)
- `firmware.bin` (actualización de app)
- `firmware.factory.bin` (instalación completa/recuperación)

Tag: `vMAJOR.MINOR.PATCH` (por ejemplo `v2.1.0`). El parser de OTA ignora el
prefijo `v` y compara los tres primeros segmentos. El asset que consume la OTA
se llama `crosspoint-v2.1.0-paperdiy.bin`: el sufijo `-paperdiy` es el board
tag, no la versión.

Bajo M5Launcher la OTA interna está **desactivada por diseño**: `OtaUpdater`
devuelve `LAUNCHER_MANAGED` y `FirmwareFlasher` rechaza escribir otra
partición. La actualización va por el paquete de Launcher
(`PaperDIYReader-launcher.bin`), no por `Buscar actualizaciones`. Ver
`13-m5launcher.md`.

**No publiques** un `firmware.factory.bin` con `ota_0` si estás usando el
dual-boot de la PR de prateek; aquí no lo usamos.

## Versionado

La versión pública es semver limpio del fork, sin sufijos:

- Release: tag `vMAJOR.MINOR.PATCH` y `[crosspoint] version` /
  `CROSSPOINT_VERSION` igual a `MAJOR.MINOR.PATCH` (por ejemplo `v2.1.0` →
  `2.1.0`).
- MAJOR: cambios incompatibles (particiones, migración de ajustes, etc.).
- MINOR: features nuevas o sync de upstream que las trae.
- PATCH: fixes, dependencias y documentación.
- RC: `v2.2.0-rc.1`; se publica como pre-release y no aparece en
  `/releases/latest`.
- Builds internos: sin tag, `2.2.0-dev.<sha>`.
- Nunca se reutiliza un tag; para reconstruir una release se sube PATCH.
- El commit upstream y el pin del SDK van en el CHANGELOG y en las notas de la
  release, no en el tag.
- `-paperdiy` solo queda en el nombre del asset OTA
  (`crosspoint-v2.1.0-paperdiy.bin`), porque es el board tag que espera la OTA.
- El workflow de release valida tag y versión con
  `scripts/check_release_version.py`.
- Changelog con: upstream base, cambios PaperDIY, hardware validado, notas de
  flash.
- `firmware.factory.bin` siempre probado en una unidad antes de publicar.
- Regla operativa para agentes:
  [`release-versioning.md`](../../.agents/rules/release-versioning.md).

## Qué se queda downstream

- Perfil PaperDIY, PM1, botones, energía.
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
