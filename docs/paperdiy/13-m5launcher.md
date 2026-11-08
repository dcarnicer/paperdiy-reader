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
> `M5Launcher > OTA`. `OtaUpdater::installUpdate` y `FirmwareFlasher` siguen
> devolviendo `LAUNCHER_MANAGED`. **No flashees `firmware.bin`
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
   `Salir a M5Launcher` para instalarla desde `OTA`. Se oculta
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
| Standalone | Sí, `crosspoint-<tag>-paperdiy.bin` desde `Verificar actualizaciones` | OTA o SD |
| Bajo M5Launcher | Solo aviso: `Verificar actualizaciones` consulta LauncherHub | `M5Launcher > OTA` (catálogo) o `PaperDIYReader-launcher.bin` desde SD/WUI |

Bajo Launcher la app corre en una partición OTA dinámica. Escribir la
"siguiente" partición podría machacar otra app instalada o romper el registro
de Launcher, así que el lector nunca escribe en la flash: el actualizador
rechaza la escritura aunque se llegue por otra vía.

El aviso busca en `https://api.launcherhub.net/firmwares?category=paper-diy`
la app llamada **`CrossPoint for PaperDIY (community port)`** (sin distinguir
mayúsculas), que
es el nombre publicado en M5Burner (LauncherHub replica M5Burner), y toma la
versión más alta de `?fid=<fid>`. Si la app aún no está en el catálogo, el
lector dice que no hay actualizaciones. Si se renombra en M5Burner, hay que
cambiar `launcherHubAppName` en `src/network/OtaUpdater.cpp`.

Pendiente de validar en hardware: la instalación de Launcher (catálogo o SD)
elige una etiqueta libre (`paper1` si `paperd` existe) y, si hay espacio,
puede crear una segunda app en vez de reemplazar la existente
(`installFirmwareDynamic` → `launcherInstallNextAppLabel`). Si ocurre, borra la
versión antigua desde el menú de la app en Launcher.

## Instalar

Requisitos:

- M5Launcher **3.0.0 o superior** con soporte PaperDIY.
- Un `.bin` **solo de aplicación** (`firmware.bin`), no la imagen combinada de
  M5Burner ni `firmware.factory.bin`.

### Desde la tarjeta SD

1. Copia `PaperDIYReader-launcher.bin` (el alias estable del release) a una
   tarjeta FAT32/exFAT.
2. Inserta la tarjeta y abre M5Launcher.
3. Entra en **SD**, selecciona el archivo y elige **Install**.
4. Arranca el lector desde el menú de Launcher.

Usa siempre el mismo nombre de archivo (`PaperDIYReader-launcher.bin`) para
instalar y actualizar. Launcher nombra la app según el archivo: instalar
`PaperDIYReader-<versión>-launcher.bin` crea una app nueva en vez de
sobrescribir la existente. El archivo versionado es solo para archivar. Aun
con el mismo nombre, no está verificado que una instalación desde SD o desde
el catálogo reemplace `paperd`: ver [OTA y actualizaciones](#ota-y-actualizaciones).

### Desde el WebUI o Favoritos

También puedes subir el `.bin` desde **WUI > OTA Update** o guardar la URL
directa del asset de release en **Favoritos**. Para Favoritos usa la URL
estable:

```
https://github.com/dcarnicer/paperdiy-reader/releases/latest/download/PaperDIYReader-launcher.bin
```

El archivo debe ser el binario de aplicación; Launcher lo detecta por la
cabecera ESP (`0xE9`).

## Compilar y empaquetar

```bash
make build ENV=paperdiy
python3 scripts/make_launcher_package.py --version 2.0.0-paperdiy.1
```

El script genera:

```
dist/launcher/
├── PaperDIYReader-2.0.0-paperdiy.1-launcher.bin
└── README.md
```

`make launcher LAUNCHER_VERSION=2.0.0-paperdiy.1` hace lo mismo. El workflow de release
publica además `PaperDIYReader-<versión>-launcher.bin` y el alias estable
`PaperDIYReader-launcher.bin` junto al factory image.

## Actualizar

1. Descarga el nuevo `PaperDIYReader-launcher.bin` (el alias estable).
2. Instálalo desde Launcher (SD, WUI o Favoritos) sobre la app existente.
3. Los datos de la SD no se tocan. `flash overwrite` por consola serie
   reutiliza la partición `paperd`; desde SD, WUI o el catálogo, Launcher
   puede crear una segunda app (`paper1`) si hay espacio libre (sin verificar).
   Si aparece duplicada, borra la versión antigua desde Launcher.

No uses `make flash` ni `esptool ... write_flash 0x10000` con Launcher
instalado: escribirías en la partición residente de Launcher. Para volver a
una instalación standalone, flashea `firmware.factory.bin` en `0x0` y borra la
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
- [x] El empaquetador valida cabecera ESP, chip ESP32-S3 y genera el asset.
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
- [ ] Actualizar desde el catálogo o la SD reemplaza `paperd` en vez de crear
  `paper1`.
