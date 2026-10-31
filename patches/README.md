# Patches

El port está separado en dos patches para poder reaplicarlo sobre nuevas
versiones de upstream:

| Archivo | Base | Contenido |
|---|---|---|
| `sdk.patch` | FreeInk SDK `2d383f8` | Perfil PaperDIY, `BoardPaperDiy`, PM1, InputManager, PowerManager, driver LGFX |
| `firmware.patch` | CrossPoint `b6605a51` | Env `paperdiy`, settings, UI, board tag, OTA, `HalGPIO`, `HalPowerManager`, `main` |
| `paperdiy-support.patch` | ambos | Concatenación de `sdk.patch` + `firmware.patch` |

Orden de aplicación:

```bash
git apply --3way patches/sdk.patch
git apply --3way patches/firmware.patch
```

El repo `paperdiy` ya incluye ambos aplicados y el SDK vendorizado. Estos
patches son para:

- revisar el port sin navegar por todo el árbol;
- reaplicarlo sobre una copia limpia de upstream;
- proponer la capa de placa upstream (separando SDK y firmware).

Generación:

```bash
# sdk.patch: diff entre el SDK pristine vendorizado y el SDK de paperdiy
git diff sdk-baseline..paperdiy -- freeink-sdk > patches/sdk.patch

# firmware.patch: diff de todo el código no-SDK propio
git diff main..paperdiy -- platformio.ini src lib/hal > patches/firmware.patch

cat patches/sdk.patch patches/firmware.patch > patches/paperdiy-support.patch
```

`sdk-baseline` es una rama local con el SDK pristine vendorizado; ver
`docs/paperdiy/10-fork-maintenance.md`.
