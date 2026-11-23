# 15 — Waveshare ESP32-S3-ePaper-3.97 (experimental)

Segunda placa del fork: la [Waveshare ESP32-S3-ePaper-3.97](https://www.waveshare.com/esp32-s3-epaper-3.97.htm)
(ESP32-S3-WROOM-1-N16R8, panel SSD1677 de 3,97" 800×480, PMIC AXP2101, SD
SDMMC de 4 bits, reloj PCF85063 e IMU QMI8658). Las notas de hardware del SDK
están en
[`freeink-sdk/docs/waveshare-epaper-397-support.md`](../../freeink-sdk/docs/waveshare-epaper-397-support.md).

> **Estado:** experimental. Todavía no hay release ni asset OTA para esta
> placa: se compila desde el código. *Verificar actualizaciones* responde «No
> hay actualizaciones disponibles».

## Origen

El soporte viene de dos PRs de upstream que aún no están fusionados, ambos de
Alexey Pazyuk:
[CrossPoint #3386](https://github.com/crosspoint-reader/crosspoint-reader/pull/3386)
y [FreeInk SDK #218](https://github.com/Free-Ink/freeink-sdk/pull/218). El
perfil de la placa (`FREEINK_DEVICE_WS397`) ya estaba en el SDK. El fork lleva
esos commits tal cual y añade encima algunos cambios propios (env, OTA, fila de
pistas en placas de dos botones, CI): ver
[PRs de upstream que llevamos](10-fork-maintenance.md#prs-de-upstream-que-llevamos).

## Compilar

```bash
make build ENV=ws397        # firmware normal
make build ENV=ws397-test   # inyección de teclas por serie (solo desarrollo)
```

La PSRAM de 8 MB está activa (lo hace la definición de placa N16R8), igual que
en la PaperDIY.

## Grabar

Si el firmware que trae importa, haz antes una copia de seguridad (ver más
abajo).

Primera instalación, viniendo de otro firmware (imagen completa en `0x0`):

```bash
esptool --chip esp32s3 --port <PUERTO> write-flash 0x0 .pio/build/ws397/firmware.factory.bin
```

Actualizaciones posteriores:

```bash
make flash ENV=ws397 PORT=<PUERTO>
```

Los dos comandos se probaron en nuestra unidad. `write-flash` comprueba el
hash de lo escrito y resetea al terminar. El aviso del SDK de que la placa se
apaga tras un reset no se dio aquí.

La imagen completa usa la misma tabla de particiones que CrossPoint y que
CrossMux. Al escribirla en `0x0` se borra la NVS del firmware anterior. Los
libros y las cachés de la SD no se tocan.

> **Cuidado:** si un comando deja el stub de esptool cargado
> (`--after no-reset`) y el siguiente se conecta con `--before no-reset` y
> resetea, la placa se queda colgada en el bootloader al cargar la app: no
> arranca y no responde por serie. Un `esptool --chip esp32s3 --port <PUERTO>
> read-mac` normal la resetea y arranca.

### Copia de seguridad

En nuestra unidad, `esptool read-flash` de toda la flash se cortaba siempre en
el mismo bloque con `The chip stopped responding`. No era la alimentación: el
stub de esptool seguía cargado después de cada corte. Leer en bloques de 4 KB
sobre una sola conexión, repitiendo en trozos de 1 KB los bloques que fallan,
sí funcionó y sacó los 16 MB. Hace falta un script que use esptool como
biblioteca de Python; no hay uno en el repo. Comprueba la copia con
`esptool … verify-flash 0x0 copia.bin`: calcula el MD5 en el chip y no pasa
los datos por USB. Con nuestra copia coincidió.

## Controles

| Tecla | Acción |
|---|---|
| Arriba / Abajo (lateral) | Mover la selección; pasar página |
| OK (lateral, centro) | Seleccionar |
| BOOT, pulsación corta | Atrás |
| BOOT, mantener | Dormir |
| BOOT, pulsar y mantener un momento con la placa dormida | Despertar; si se durmió desde un libro, vuelve a él |
| PWR | No llega al firmware. Según el SDK, el AXP2101 enciende con 1 s y apaga con 4 s; en su puesta en marcha (con USB) mantenerla 4 s no la apagó |

- En esta placa no hay fila de pistas de botones (no tiene botones frontales).
- BOOT es a la vez Atrás y encendido, así que mantener Atrás en un libro no
  lleva a Home: esa pulsación larga duerme la placa.
- Al despertar, el firmware comprueba que BOOT sigue pulsado; un toque muy
  breve puede volver a dormirla.
- Deja el ajuste «Pulsación corta» del botón de encendido en «Ignorar» (el
  valor por defecto): en esta placa ese botón es BOOT, que ya hace de Atrás.
- Teclado en pantalla: Arriba/Abajo recorren todas las teclas en orden de
  lectura y OK escribe. Mantener Arriba entra en modo cursor, pero sin teclas
  izquierda/derecha no se puede mover el cursor (Abajo sale del modo) y el
  conmutador para mostrar la contraseña no es accesible.

## Validación (23/11/2026, una unidad)

Arranque, pantalla, SD SDMMC, RTC, IMU y batería/carga por el AXP2101. Home,
lector (paso de página, cambio de capítulo), Ajustes, popups, escaneo Wi-Fi,
botonera, BOOT para dormir y despertar, y teclado en pantalla. Con el bootloader
QIO actual: arranque, reinicio por software (`RTC_SW_CPU_RST`) y popups; dormir
y despertar se probó con el build anterior (flash en DIO). Capturas por serie
con `scripts/paperdiy_serial.py screenshot --width 800 --height 480`.

## Pendiente

- Release con assets `crosspoint-ws397-*` y OTA real.
- Evaluar el env `firmware_tuned` de upstream y la unidad USB (MSC).
- Medir el consumo en reposo (80 MHz con PSRAM) y en sueño profundo (el pin
  RST del panel queda en alto con el panel sin alimentación).
- Medir el refresco HALF y revisar la LUT de grises (heredada de la Sticky).
- Apagar los raíles del panel también tras pintar imágenes y portadas en
  grises absolutos (`Ssd1677Driver.cpp`): hoy solo se apagan tras la pasada de
  antialiasing.
- Una SD que venga de CrossMux tiene cachés con otro formato: se regeneran al
  abrir cada libro, y otra vez cada vez que se cambia de firmware.
