# 13 — M5Launcher

**Idiomas:** **Español** · [English](13-m5launcher.en.md)

[bmorcelli/Launcher](https://github.com/bmorcelli/Launcher) —conocido como
**M5Launcher**— es un firmware residente que instala y arranca otras
aplicaciones desde particiones OTA dinámicas. La versión 3.0.0 incluye el port
del **M5Stack PaperDIY**, así que el lector puede convivir con otros firmwares
en la misma placa.

> **OTA bajo M5Launcher: la instala Launcher.** El lector no escribe en la
> flash: `Verificar actualizaciones` consulta el catálogo de Launcher
> (LauncherHub) y avisa si hay versión nueva; se instala desde
> `M5Launcher > OTA` y después se borra la versión anterior en Launcher, que
> instala cada versión junto a la vieja. `OtaUpdater::installUpdate` y
> `FirmwareFlasher` siguen devolviendo `LAUNCHER_MANAGED`. **No flashees `firmware.bin`
> en `0x10000`** con Launcher instalado: sobrescribirías su partición
> residente.

## Configuración recomendada

Por defecto, Launcher muestra su pantalla en **cada encendido**, y en el
PaperDIY eso incluye despertar de la suspensión: el lector duerme pidiendo
apagado al PM1, así que despertar es un encendido en frío. Para que el lector
despierte directamente, configura en Launcher:

**`CFG > GPIO on boot starts Launcher` = `A`** (con `GPIO Level` = `0`).

Con eso, Launcher solo aparece si **A** está pulsado al arrancar. El resto de
arranques (encendido, despertar, reinicios) van directos al lector. Para entrar
en Launcher, mantén A y pulsa power, o usa `Salir a M5Launcher` desde el lector.

## Cómo decide Launcher qué arrancar

El bootloader de Launcher 3.0.0 lee su configuración del namespace NVS
`launcher` en cada reset:

| Configuración de Launcher | Encendido (PM1) | Despertar de deep sleep | Reinicio por software |
|---|---|---|---|
| Por defecto | Launcher | Launcher | Lector |
| `DeepSleep starts Launcher` desactivado | Launcher | Lector | Lector |
| `GPIO on boot starts Launcher` = A | Lector (Launcher con A pulsado) | Lector (ídem) | Lector (ídem) |

`DeepSleep starts Launcher` no afecta a la suspensión normal del PaperDIY,
porque es un apagado del PM1, no un deep sleep. Solo cambia el fallback de deep
sleep que ocurre cuando el PM1 no corta la alimentación.

## Qué cambia en el lector

El binario es el mismo que el de una instalación normal: no hay un build
distinto para Launcher. En tiempo de ejecución el lector detecta que está bajo
M5Launcher, registra su configuración en el log de arranque
(`M5Launcher detected: DDLB=… LauncherOnKey=… LauncherKeyLvl=…`) y adapta
cuatro cosas:

1. **Salir a M5Launcher.** Aparece en `Ajustes > General` y funciona en los
   tres modos:
   - **Con tecla configurada:** muestra "Mantén pulsado A para abrir
     M5Launcher". Al mantener A 0,3 s, el lector se reinicia con A todavía
     pulsado; el bootloader lo detecta y arranca Launcher. Sigue pulsando hasta
     que aparezca su menú. Cualquier otro botón cancela.
   - **Sin tecla y `DeepSleep starts Launcher` activado:** confirma y hace un
     deep sleep de 1 ms; el reset `DEEPSLEEP` abre Launcher.
   - **Sin tecla y `DeepSleep starts Launcher` desactivado:** confirma y pide al
     PM1 un reset del ESP32, que el bootloader ve como encendido.

   En los dos últimos casos aparece la pantalla de arranque de Launcher: pulsa
   **A** largo para entrar en el menú antes de que arranque la última app.
2. **Actualizaciones gestionadas por Launcher.** `Verificar actualizaciones`
   solo avisa: consulta LauncherHub y, si hay versión nueva, ofrece
   `Salir a M5Launcher` para instalarla desde `OTA` y recuerda borrar la
   versión anterior. Se oculta
   `Actualizar firmware por tarjeta SD`. Bajo Launcher la app corre en una
   partición OTA elegida dinámicamente; escribir en la "siguiente" partición
   podría machacar otra app instalada y romper el registro de Launcher.
3. **Protección en profundidad.** Aunque se llegue al actualizador por otra vía,
   `OtaUpdater` y `FirmwareFlasher` rechazan escribir particiones OTA mientras
   Launcher esté presente.
4. **Sin modo recuperación al arrancar.** Bajo Launcher, mantener A al encender
   es la forma de abrir Launcher, así que el lector no entra en el selector de
   firmware por SD aunque arranque con A pulsado.

Los ajustes, la biblioteca, las cachés, los libros y el progreso de lectura
siguen en la tarjeta SD (`/.crosspoint/`), así que sobreviven a reinstalar la
app o a borrar la flash. Launcher guarda además su propia configuración en
`/config.conf` en la raíz de la SD, así que la tecla A y `DDLB` también se
conservan. Lo que sí se pierde al borrar la flash son las credenciales Wi-Fi
del lector (`nvs.net80211`); hay que volver a introducirlas.

## OTA y actualizaciones

| Instalación | OTA interna | Cómo actualizar |
|---|---|---|
| Standalone | Sí: `Verificar actualizaciones` descarga `crosspoint-paperdiy-<versión>-ota.bin` de la última release | OTA, o ese mismo `-ota.bin` desde `Actualizar firmware por tarjeta SD` |
| Bajo M5Launcher | Solo aviso: `Verificar actualizaciones` consulta LauncherHub | `M5Launcher > OTA` (catálogo) o `crosspoint-paperdiy-latest.bin` desde SD, WebUI o Favoritos |

Bajo Launcher la app corre en una partición OTA dinámica. Escribir la
"siguiente" partición podría machacar otra app instalada o romper el registro
de Launcher, así que el lector nunca escribe en la flash: el actualizador
rechaza la escritura aunque se llegue por otra vía. Otros firmwares que
conviven con Launcher, como Bruce o SigurdOS, hacen lo mismo.

El aviso busca en `https://api.launcherhub.net/firmwares?category=paper-diy`
la app llamada **`CrossPoint for PaperDIY (community port)`** (sin distinguir
mayúsculas), que es el nombre publicado en M5Burner (LauncherHub replica
M5Burner), y toma la versión más alta de `?fid=<fid>`. Si la app aún no está
en el catálogo, el lector dice que no hay actualizaciones. Si se renombra en
M5Burner, hay que cambiar `launcherHubAppName` en `src/network/OtaUpdater.cpp`.

**Launcher instala cada versión junto a la anterior.** Mientras quede espacio
libre, instalar desde el catálogo, la SD, la WebUI o Favoritos crea una app
nueva con una etiqueta libre (`crossp`, `cross1`…) en vez de reemplazar la
existente; solo pregunta qué app sustituir cuando ya no cabe
(`installFirmwareDynamic` y `launcherSelectInstallLayout` en Launcher 3.0.0).
Es el diseño de Launcher desde la 2.7.0, que admite varias apps a la vez. Por
eso el aviso dice "Después borra la versión anterior en Launcher". Solo
`flash overwrite` por la consola serie reutiliza la misma partición. Esto sale
del código de Launcher; aún no lo hemos visto en hardware con la app del
catálogo.

## Instalar

Requisitos:

- M5Launcher **3.0.0 o superior** con soporte PaperDIY.
- La imagen completa de la release, `crosspoint-paperdiy-latest.bin` (la misma
  que se publica en M5Burner). Launcher lee la tabla de particiones que lleva
  dentro y copia solo la app de `0x10000`. Desde SD, WebUI o Favoritos crea
  además una partición SPIFFS vacía de 448 KB, porque la tabla declara una
  `spiffs`; el lector no la usa.

### Desde el catálogo

1. Abre **M5Launcher > OTA** y entra en la categoría del PaperDIY.
2. Elige **CrossPoint for PaperDIY (community port)** e instala la última
   versión.

### Desde la tarjeta SD

1. Copia `crosspoint-paperdiy-latest.bin` a una tarjeta FAT32/exFAT.
2. Inserta la tarjeta y abre M5Launcher.
3. Entra en **SD**, selecciona el archivo y elige **Install**.
4. Arranca el lector desde el menú de Launcher.

### Desde la WebUI o Favoritos

Sube el mismo `.bin` desde **WUI > OTA Update**, o guarda en **Favoritos** el
enlace que siempre apunta a la última versión:

```
https://github.com/dcarnicer/paperdiy-reader/releases/latest/download/crosspoint-paperdiy-latest.bin
```

## Archivos de la release

Cada release publica dos `.bin`. Los genera
`.github/workflows/release-paperdiy.yml` y los comprueba
`scripts/check_release_assets.py`, que verifica que la app de la imagen
completa es idéntica a la de la OTA:

| Archivo | Qué es |
|---|---|
| `crosspoint-paperdiy-latest.bin` | Imagen completa (`0x0`) para M5Burner, M5Launcher y esptool. El nombre es fijo para que el enlace `latest` dé siempre la última |
| `crosspoint-paperdiy-<versión>-ota.bin` | Solo la app, para un lector standalone: la descarga `Verificar actualizaciones`, o se copia a la raíz de la SD para `Actualizar firmware por tarjeta SD`. No se instala con esptool, M5Burner ni Launcher |

En local, `make build ENV=paperdiy` deja la imagen completa en
`.pio/build/paperdiy/firmware.factory.bin`.

## Actualizar

1. Instala la versión nueva desde **M5Launcher > OTA**, o el nuevo
   `crosspoint-paperdiy-latest.bin` desde SD, WebUI o Favoritos.
2. En el menú de Launcher, abre la versión anterior y elige **Delete**.
3. Los datos de la SD (`/.crosspoint/`) no se tocan.

No uses `make flash` ni `esptool ... write_flash 0x10000` con Launcher
instalado: escribirías en la partición residente de Launcher. Para volver a
una instalación standalone, flashea `crosspoint-paperdiy-latest.bin` en `0x0` y borra la
flash antes si quieres eliminar las particiones dinámicas.

## Notas técnicas

- Launcher marca su partición residente con el subtipo `test` (`0x20`), en
  `0x10000`. El lector busca ese subtipo con `esp_partition_find_first()`; es
  la señal que activa la integración y no aparece en `partitions.csv` de una
  instalación normal.
- La lógica del bootloader está en
  `patches/esp-idf/components/bootloader/subproject/main/bootloader_start.c`
  de la rama `launcher_keyboot` de
  [bmorcelli/myLibBuilder](https://github.com/bmorcelli/myLibBuilder). Lee las
  claves `DDLB` (u8), `LauncherOnKey` (i32) y `LauncherKeyLvl` (u8); el lector
  lee las mismas, solo una vez por arranque.
- Con tecla configurada, el bootloader ignora el motivo del reset y solo mira la
  tecla. Ni el deep sleep ni el reset del PM1 abren Launcher en ese modo; por
  eso la salida reinicia con la tecla pulsada.
- El reset del PM1 es `SYS_CMD` = `0xA2` (`KEY` 0xA, comando 2). Reinicia el
  ESP32 por `CHIP_EN` y el bootloader lo ve como encendido.
- La app ocupa unos 5,2 MB. Launcher crea una partición OTA del tamaño
  necesario dentro del espacio libre; no se usa la partición `spiffs` del
  `partitions.csv` del lector.
- La salida no borra `otadata`: la app sigue seleccionada para el autoarranque
  de Launcher.

## Estado de validación

Validado el 07/11/2026 en un PaperDIY con M5Launcher 3.0.0, antes de que
`Verificar actualizaciones` volviera a mostrarse bajo Launcher como aviso (por
eso varias entradas dicen que las actualizaciones internas están ocultas):

- [x] Compila el entorno `paperdiy` con los cambios.
- [x] El empaquetador de Launcher (ya retirado) validaba cabecera ESP y chip
  ESP32-S3.
- [x] Instalación desde M5Launcher (consola serie, `flash firmware`).
- [x] La app arranca bajo Launcher, muestra `Salir a M5Launcher` y oculta las
  actualizaciones internas.
- [x] Actualización desde Launcher (`flash overwrite`) conservando la tarjeta
  SD y la posición de lectura.
- [x] Salida con `DeepSleep starts Launcher` activado (deep sleep de 1 ms).
- [x] Salida con `DeepSleep starts Launcher` desactivado (reset del PM1): abre
  la pantalla de arranque de Launcher.
- [x] Con `GPIO on boot starts Launcher` = A: suspender y encender arranca el
  lector directamente (dos veces); la salida manteniendo A abre el menú de
  Launcher; B cancela la salida.
- [x] Instalación limpia desde cero: borrado de los 16 MB, M5Launcher 3.0.0
  oficial en `0x0` e instalación del release `v0.1.0` desde la SD. La
  partición `paperd` coincide byte a byte con el asset
  (`sha256 05f68e10…`).
- [x] La instalación limpia conserva biblioteca, ajustes y progreso de lectura
  de la SD, y la configuración de Launcher (`/config.conf`). Solo se pierden
  las credenciales Wi-Fi de NVS.
- [x] Tras la instalación limpia: `Salir a M5Launcher` visible, actualizaciones
  internas ocultas, salida con A y cancelación con B, y despertar directo al
  lector.
- [ ] Instalación desde WUI/Favoritos: usa el mismo instalador de Launcher, pero
  no se probó por separado en esta unidad.

Aviso de actualización, validado el 08/11/2026 con M5Launcher 3.0.0 (lector
instalado con `flash firmware` y `flash overwrite`):

- [x] Bajo Launcher, `Sistema` muestra `Verificar actualizaciones` y
  `Salir a M5Launcher`, y oculta la actualización por SD.
- [x] Con un build temporal 1.0.0 que buscaba la app `PaperDIY Reader` del
  catálogo: muestra `Versión actual: 1.0.0`, `Nueva versión: 1.0.1`,
  `Instálala desde M5Launcher > OTA` y `Cancelar` / `Salir a M5Launcher`.
- [x] `Salir a M5Launcher` desde el aviso, con tecla A configurada: abre la
  pantalla de mantener A y llega al menú de Launcher.
- [x] `Salir a M5Launcher` desde el aviso sin tecla configurada: con
  `DeepSleep starts Launcher` activado sale por deep sleep y, desactivado, por
  reset del PM1; en ambos casos aparece Launcher y luego vuelve al lector.
- [ ] Aviso con la app real publicada en M5Burner.
- [ ] Ver en hardware que actualizar desde el catálogo instala la versión nueva
  junto a la anterior y que la vieja se borra bien desde Launcher.
