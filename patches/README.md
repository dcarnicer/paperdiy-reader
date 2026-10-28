# Patches

`paperdiy-support.patch` es el diff del soporte PaperDIY contra el snapshot de
CrossPoint 2.0 importado en `a54770e`. Sirve para:

- revisar el port sin navegar por todo el árbol;
- proponer el soporte upstream a CrossPoint (el perfil + el `BoardPaperDiy` son
  autocontenidos);
- reaplicar el port sobre una copia limpia de upstream.

Generación:

```bash
git diff a54770e -- \
  freeink-sdk/libs/hardware/BoardConfig \
  freeink-sdk/libs/hardware/BatteryMonitor \
  freeink-sdk/libs/hardware/PowerManager \
  freeink-sdk/libs/hardware/BoardPaperDiy \
  freeink-sdk/libs/display/FreeInkDisplay/src/driver/LgfxEpdDriver.cpp \
  platformio.ini src/network/FirmwareBoardTag.cpp \
  > patches/paperdiy-support.patch
```

Nota: `freeink-sdk` aquí está vendorizado (no es submódulo), así que el patch
incluye cambios del SDK. Para upstream habría que separar el PR del SDK y el
del firmware.
