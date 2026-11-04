# 12 — Testing por USB

El firmware incluye un modo de desarrollo para automatizar pruebas de UI y
capturar la pantalla sin pulsar los botones físicos.

> Este modo **no debe publicarse**. El entorno normal `paperdiy` no compila la
> inyección de teclas; solo la incluye `paperdiy-test`.

## Build de pruebas

```bash
make build ENV=paperdiy-test
make flash ENV=paperdiy-test PORT=/dev/cu.usbmodemXXXX
```

`paperdiy-test` extiende `paperdiy` y añade `-DPAPERDIY_SERIAL_TEST=1`. El
firmware resultante queda en `.pio/build/paperdiy-test/`.

## Comandos serie

Con el puerto USB conectado (115200 baudios):

| Comando | Efecto | Disponible en |
|---|---|---|
| `CMD:SCREENSHOT` | Devuelve el framebuffer 1 bpp por serie | `paperdiy` y `paperdiy-test` |
| `CMD:KEY:A` | A corto: arriba / página anterior | solo `paperdiy-test` |
| `CMD:KEY:B` | B corto: abajo / página siguiente | solo `paperdiy-test` |
| `CMD:KEY:A_LONG` | A largo: atrás / salir | solo `paperdiy-test` |
| `CMD:KEY:B_LONG` | B largo: confirmar / seleccionar | solo `paperdiy-test` |
| `CMD:KEY:NEXT` | Igual que `B` | solo `paperdiy-test` |
| `CMD:KEY:PREV` | Igual que `A` | solo `paperdiy-test` |
| `CMD:KEY:CONFIRM` | Igual que `B_LONG` | solo `paperdiy-test` |
| `CMD:KEY:BACK` | Igual que `A_LONG` | solo `paperdiy-test` |

La respuesta es `KEY:<nombre>:1` si la entrada se aceptó, o `KEY:<nombre>:0`
si se ignoró (por ejemplo, porque hay una pulsación física o el lector está
ocupado).

En el lector, `A`/`B` hacen page turn; en listas y menús mueven la selección.
`A_LONG`/`B_LONG` cubren los atajos de atrás/confirmar sin necesidad de simular
una pulsación mantenida.

**Limitación:** no se inyectan power ni A+B. Para dormir o apagar usa el botón
físico; para un reset de prueba usa `esptool` o el modo descarga.

## Script de ayuda

`scripts/paperdiy_serial.py` usa solo la librería estándar de Python:

```bash
# Captura la pantalla actual (rota a 540x960, como las capturas del lector)
python3 scripts/paperdiy_serial.py screenshot /tmp/home.png

# Pulsa B (siguiente) y luego confirma
python3 scripts/paperdiy_serial.py key B
python3 scripts/paperdiy_serial.py key B_LONG

# Guarda también el framebuffer raw
python3 scripts/paperdiy_serial.py screenshot /tmp/home.png --raw /tmp/home.bin

# Si la imagen sale invertida
python3 scripts/paperdiy_serial.py screenshot /tmp/home.png --invert

# En orientación horizontal, el framebuffer nativo ya es 960x540:
python3 scripts/paperdiy_serial.py screenshot /tmp/landscape.png --rotate 0
```

El puerto se autodetecta como `/dev/cu.usbmodem*`; también se puede pasar con
`--port`. El script espera la respuesta `KEY:...:1` y devuelve código de salida
distinto de cero si la entrada se ignora. `key` reintenta 2 veces por defecto
cuando el lector está ocupado (`--retry`) y espera 0,5 s tras una tecla
aceptada (`--settle`) para que el panel termine de refrescar.

## Flujo típico

1. Flashea `paperdiy-test`.
2. Captura la Home.
3. Envía `B`, `B_LONG` o `A_LONG` y captura después de cada paso.
4. Compara las imágenes o revisa los logs para detectar regresiones de UI.

El comando de screenshot devuelve el framebuffer tal cual; el script lo rota
90° en sentido horario para obtener la vista vertical de 540×960 que ve el
usuario. `--rotate 0` deja la orientación nativa del panel, y `--invert`
intercambia blanco/negro si hiciera falta.

## Resultados de la primera pasada (04/11/2026)

Probado con `paperdiy-test` sobre el firmware `308cd522`:

- Home, navegador de archivos, biblioteca, ajustes (Sistema, Pantalla, Lector,
  Controles, Biblioteca y Conectividad), About, lector, menú del lector,
  ajustes de texto y orientación horizontal/vertical: pantallas correctas.
- OTA: conecta con la Wi-Fi guardada y responde “No hay actualizaciones
  disponibles”; no instala firmware oficial.
- Tiempos observados en lectura: portada ~1,08 s; primera página con caché
  nueva ~3,16 s; páginas siguientes ~1,38–1,44 s (display ~0,59 s + gris
  ~0,50 s + limpieza ~0,06 s).
- Una captura mostró un frame intermedio con un bloque blanco tras volver de
  Wi-Fi/OTA; la pantalla se estabilizó a los ~2 s. Revisar si es un artefacto
  de refresco parcial o de la propia captura.
- Las secuencias de teclas muy rápidas pueden adelantar la selección; el
  script espera 0,5 s por defecto. Para pruebas de listas conviene subir
  `--settle`.
- La biblioteca mostró un libro con nombre de archivo hash como título
  (`b090d610…`); parece un problema de metadatos del EPUB, no de la UI.
- Energía: A+B con USB hace deep sleep y A despierta; el clic corto de power
  apaga vía PM1 y solo power vuelve a encender; A+B con batería apaga y power
  enciende. La página se conserva en todos los casos.
- Download mode: requiere ~10 s, no 2 s. `esptool --before no-reset` confirma
  que el chip está en bootloader. Tras el hard reset hay que pulsar power para
  arrancar la app.
- Recuperación: `firmware.factory.bin` en `0x0` verificado; arranca y conserva
  la página.
- SD en caliente: quitar/reinsertar en Home funciona. Quitarla **leyendo**
  muestra “Insert SD card”; al reinsertar, el equipo reinicia, monta la tarjeta
  y vuelve a Home. Verificado con el fix de reintentos de montaje (04/11/2026).
- USB MSC: la SD aparece como volumen `DABI` (FAT32, 8 GB); al expulsar, la
  placa vuelve sola a Home.
- EPUB grande (7,3 MB): abre sin OOM; primera sección ~3,0 s y páginas
  siguientes ~1,3 s.
- Ghosting real: leve y legible con refresco cada 5 páginas.

Pendiente de probar: consumo/autonomía, OPDS/Calibre con contenido, BLE page
turner y lectura muy larga.
