# 10 — Mantener el fork

Este repo es un fork downstream de CrossPoint. La regla es simple: **el motor
se sigue de upstream; el hardware y la UX PaperDIY viven en nuestro fork**.

## Ramas y remotos

| Rama | Qué es |
|---|---|
| `main` | Espejo de `upstream/develop` (sin cambios nuestros) |
| `paperdiy` | Nuestro fork: `main` + FreeInk SDK vendorizado + port + docs |
| `backup/2026-10-28` | Historial anterior a la reestructuración (seguro) |
| `master` | Historia antigua, conservada por si acaso |

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
git checkout paperdiy -- README.md Makefile NOTICE LICENSE .gitignore \
  docs/paperdiy docs/README.md docs/upstream scripts patches .github
rm -f ROADMAP.md SCOPE.md GOVERNANCE.md AGENTS.md USER_GUIDE.md CLAUDE.md .gitmodules
rm -rf .github && git checkout paperdiy -- .github

make build
```

Si el build y el smoke test de hardware pasan:

```bash
git checkout paperdiy
git merge --ff-only paperdiy-next
```

## Patches

| Patch | Base | Contenido |
|---|---|---|
| `patches/sdk.patch` | FreeInk SDK `44427f8` | perfil, BoardPaperDiy, PM1, InputManager, PowerManager, driver LGFX |
| `patches/firmware.patch` | CrossPoint `31dc683` | env, board tag, OTA, HalGPIO, HalPowerManager, main |
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

Tag recomendado: `v2.1.0-paperdiy.1` o `2.1.0-paperdiy.1`. El parser de OTA
ignora el prefijo `v` y compara los tres primeros segmentos.

**No publiques** un `firmware.factory.bin` con `ota_0` si estás usando el
dual-boot de la PR de prateek; aquí no lo usamos.

## Versionado

- `CROSSPOINT_VERSION` = versión upstream + `-paperdiy`.
- Releases: `2.x.y-paperdiy.N`.
- Changelog con: upstream base, cambios PaperDIY, hardware validado, notas de
  flash.
- `firmware.factory.bin` siempre probado en una unidad antes de publicar.

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
- [ ] Changelog y artefactos.
