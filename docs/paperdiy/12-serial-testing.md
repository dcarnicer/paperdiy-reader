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
- Energía: en la pasada del 04/11/2026, A+B con USB hizo deep sleep y A
  despertó; el clic corto de power apaga vía PM1 y solo power vuelve a
  encender; A+B con batería apaga y power enciende. La página se conserva en
  todos los casos. En la pasada del 05/11/2026 el mismo A+B con USB apagó vía
  PM1 y A no despertó (ver más abajo).
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
- Cómic: 15 tomos convertidos con KCC (`Other` 540×960, PNG 16 niveles,
  recorte de márgenes, modo manga). TOMO1, TOMO2 y TOMO3 abren, muestran la
  portada y pasan página; la primera indexación de ~150 páginas tarda unos
  20–30 s. Los EPUB quedan en 9–15 MB por tomo.
- Ghosting real: leve y legible con refresco cada 5 páginas.

## Segunda pasada (05/11/2026)

Probado con `paperdiy-test` sobre `308cd522`, batería original de 140 mAh y USB
conectado al Mac.

- **Paginación**: 96 cambios de página (12 adelante / 12 atrás, repetido)
  sin entradas perdidas, reinicios ni cuelgues. En este EPUB de texto la ruta
  no ejecutó la pasada de grises; los tiempos son de la ruta B/W:
  - página normal: render 668–725 ms, display 576–621 ms, total percibido
    809–925 ms;
  - refresco completo cada 5 páginas: render ~1,64 s, display ~1,54 s,
    total ~1,77–1,85 s.
- **Memoria**: el heap queda igual antes y después de la tanda: 121.552 B
  libres, 110.732 B mínimo; PSRAM 6.367.560 B libres, 6.353.628 B mínimo.
  No se observó fuga. Tras el cambio de fuente y el reflow, el mínimo de heap
  bajó a 83.916 B durante la reconstrucción de la sección; el libre volvió a
  120.708 B.
- **OPDS**: se añadió Project Gutenberg por la API web
  (`https://www.gutenberg.org/ebooks/search.opds/?sort_order=downloads`), se
  navegó el catálogo, se descargó *Pride and Prejudice* a la raíz de la SD y
  se abrió y paginó correctamente. Standard Ebooks devuelve 401 y requiere
  credenciales.
- **Calibre wireless**: el servidor arranca en `192.168.1.154` y la web UI
  responde; la transferencia ya estaba validada el 04/11.
- **Fuentes**: cambio de 14 a 16 pt y vuelta a 14 pt; el reflow se aplica y
  el número de páginas de la sección cambia. Las pestañas
  Fuente/Tamaño/Diseño/Estilo y la lista de tamaños son operables con
  A/B/largos.
- **BLE**: el escaneo encuentra dispositivos (auriculares, tiras LED, etc.);
  no había un mando real para emparejar. El toggle se dejó desactivado.
- **CrossPoint Sync**: la pantalla de configuración funciona; no hay
  credenciales configuradas, así que no se probó el sync real.
- **Energía**: A+B con USB en este Mac apagó vía PM1, no hizo deep sleep; A
  no despertó. Power encendió y conservó la página (1/63). Esto corrige la
  nota anterior de que A+B con USB siempre despertaba con A.
- **Observación**: el puerto USB desapareció una vez tras abrir el EPUB
  descargado y volvió al reconectar/encender. No se reprodujo.
- **Ghosting**: la captura por serial devuelve el framebuffer, no la imagen
  física del panel. Revisión visual tras 24 páginas (05/11): sin ghosting
  apreciable con refresco cada 5 páginas. El contador pasó de 1/35 a 1/50 al
  completarse la construcción de la sección; parece un conteo parcial
  mientras se indexa. Falta lectura muy larga.

## Auto-suspensión y sleep screen (05/11/2026)

- `Pantalla > Auto suspensión` a 1 min. Con el USB desconectado, el equipo
  suspendió tras ~1 minuto.
- Con `Fondo de pantalla de suspensión = Oscuro` mostró el logo de CrossPoint
  sobre fondo oscuro.
- Con `Fondo = Portada` y `Modo = Ajustar` mostró la portada de *Pride and
  Prejudice* al suspenderse.
- Power despertó y volvió a la misma página (1/50) en ambos casos.
- La batería pasó de 100 % a 90 % tras el primer ciclo y luego osciló entre
  97–99 %; la curva de 140 mAh es gruesa y el consumo real sigue pendiente.
- Al terminar, `Auto suspensión` se dejó en 10 min; `Fondo = Portada` y
  `Modo = Ajustar` se mantuvieron.

Pendiente de probar: consumo/autonomía, emparejar un mando BLE real, ghosting
visual tras lectura muy larga y la batería 604050.

## BLE bring-up (06/11/2026)

- El Keychron Q1 Pro no aparece en un escaneo BLE del Mac (sí en Bluetooth
  Classic) ni en el del PaperDIY. Es un teclado Classic; el ESP32-S3 no tiene
  radio BR/EDR.
- Se emuló un teclado HID BLE en macOS con CoreBluetooth (BTHIDKit):
  `PaperDIY Test Keyboard`. El PaperDIY lo lista, pero el emparejamiento falla
  con `Pairing failed` (NimBLE `0x508`), también con Secure Connections y sin
  cifrado. Hace falta un mando BLE real para validar el flujo completo.
- El build de diagnóstico usó `FREEINK_BLE_HID_SHOW_UNNAMED_DEVICES`,
  `CONFIG_BT_NIMBLE_EXT_ADV` y `FREEINK_BLE_HID_SCAN_DEBUG` en un
  `platformio.local.ini` temporal; se revirtió y se volvió a flashear
  `paperdiy-test`.

## KOReader Sync local (06/11/2026)

- Se levantó un servidor KOSync mínimo en el Mac (`192.168.1.148:7200`) y se
  configuraron credenciales de prueba desde `/api/settings` de la web UI.
- Validado: autenticación, `GET /syncs/progress` sin progreso remoto, subida
  (`PUT`) con metadatos y locator, comparación remoto/local y aplicación del
  progreso remoto (salto de página 13→17 en *Reconciliación*).
- Las credenciales de prueba se borraron al terminar; el lector queda sin
  servidor configurado.
- No se probó contra un servidor oficial/remoto; el mock implementa los
  endpoints KOSync estándar.

## Lectura larga y tiempos de refresco (06/11/2026)

- **Lectura larga**: 250+ cambios de página por inyección USB (spines 10→24,
  varios capítulos) sin reinicios, errores de render ni fugas. Heap libre
  120,6–120,8 KB y PSRAM ~6,36 MB; mínimo transitorio de heap 81,7 KB.
- **Tiempos** con los logs `ERS` `Page render: ... display=... total=...` y
  `Rendered page in ...` (página completa, una sola base B/W porque el log no
  muestra pasada de grises):
  - `fast`: display 569–620 ms, total 651–726 ms.
  - `text` limpio: display 1538–1542 ms, total 1637–1651 ms.
  - `quality`: el port mapea `Full/Half` a `epd_text`, así que no se usa. Con
    un mapeo temporal `Half→quality` midió 1538 ms, igual que `text`; el
    código se restauró después.
  - Prewarm 38–58 ms; render B/W 49–59 ms.
- **Auto-suspensión**: `CMD:KEY` no reinicia el temporizador de actividad. A
  los 10 min el equipo se durmió en plena prueba y el USB desapareció; power
  despertó conservando la página. Para pruebas largas, poner
  `Pantalla > Auto suspensión = Nunca` (y restaurarlo al terminar) o hacer que
  la inyección cuente como actividad.
- **Ghosting**: la captura devuelve el framebuffer. La estabilidad está
  validada, pero el ghosting físico tras la lectura larga requiere revisión
  visual del panel.

## Benchmark de cómics y modos de imagen (07/11/2026)

Probado con `paperdiy-test`, TOMO2 de *Seitokai ni mo Ana wa* y los logs
`ERS Page render: ... total=...`. No se modificó firmware; solo se cambiaron
ajustes del lector y se compararon varios EPUB.

| Configuración | Page turn | Peso | Observación |
|---|---:|---:|---|
| KCC PNG 540 px + grises | 8,0–8,3 s | 13 MB | Ruta completa con dos pasadas de grises |
| KCC JPEG 540 px + grises | 8,0–8,3 s | 19 MB | JPEG no es más rápido que PNG |
| KCC PNG + `Imágenes: B/N`, AA on | 4,8–6,8 s | 13 MB | El AA de texto sigue activando las pasadas de grises |
| KCC PNG + `Imágenes: B/N`, AA off | 3,0–3,1 s | 13 MB | Dither 2×2 del lector; refresco completo ocasional ~4,6 s |
| 1-bit Floyd–Steinberg + B/N, AA off | **2,3–2,5 s** | **4,7 MB** | Dither fino precalculado; refresco completo ~3,3 s |

Desglose típico en grises (KCC PNG): prewarm ~25 ms, render B/W 3,0–3,8 s,
display 1,54 s, `gray_lsb` ~0,9 s, `gray_msb` ~0,9 s, `gray_display` ~1,3 s,
limpieza ~56 ms. El cuello de botella es el render de la imagen y las pasadas
de grises, no el formato de compresión.

Notas:

- KCC entrega 540 px de ancho, pero el lector usa ~530 px por el margen de
  pantalla de 5 px; la imagen se reduce ~2%. Un perfil KCC a 530 px evitaría
  ese reescalado (no probado en hardware).
- Para que `Imágenes: B/N` salte las pasadas de grises hace falta desactivar
  también el antialiasing de texto; si no, `needsAnyGrayscale` sigue siendo
  cierto. Es un ajuste global, no por libro.
- El prototipo 1-bit se generó posprocesando los PNG de KCC con Floyd–
  Steinberg (`PIL`, modo `1`). El lector lo dibuja sin dither adicional y el
  archivo baja a ~1/3 del tamaño.
- Los ajustes de imagen/AA se cambiaron solo para medir; hay que restaurarlos
  (`Imágenes: Mostrar`, `Antialiasing: activado`) al terminar.


## Tercera pasada — stack de dependencias (08/11/2026)

Probado con `paperdiy-test` sobre `paperdiy-m5gfx`: upstream CrossPoint
`818a1540`, expat 2.10.0, ArduinoJson 7.4.3, NimBLE-Arduino 2.5.2 y M5GFX
0.2.36. La unidad tenía batería al 100 % y la SD original.

- Arranque, Home, menú, Ajustes, Sistema, Lector, About, Biblioteca y lector:
  correctos. La captura de Home mostró la portada y el libro reciente sin
  artefactos.
- About: `2.0.0-paperdiy` en el build de prueba (la release `v2.1.0` reporta
  `2.1.0`), ESP32-S3 rev 2, 16 MB, SD 7,4 GB (555 MB usados),
  batería 4,14 V, `LovyanGFX EPD` a 960×540, sin táctil/frontlight/RTC/IMU.
- Paginación: 1/31 → 2/31 → 6/31 → 4/31 con A/B, sin entradas perdidas.
- Orientación: vertical, horizontal horario y horizontal antihorario. En
  horizontal, la captura nativa sale derecha con `--rotate 0` para
  antihorario y con `--rotate 180` para horario; el texto y los márgenes son
  correctos en ambos.
- USB MSC: monta `DABI`, expulsa desde el Mac y el lector vuelve solo a Home.
- Diccionario StarDict de prueba (creado al efecto) y vocabulario:
  - La búsqueda desde el lector y la pantalla de definición funcionan.
  - `/Vocabulary.txt` se escribe con `v`, palabra, headword, definición,
    capítulo, página, spine y offset correctos.
  - Encontrados y corregidos dos defectos: el terminador NUL de StarDict se
    guardaba como `\u0000` y `definition_truncated` quedaba en `true` aunque
    solo se hubiera recortado ese byte.
  - El ajuste nuevo salía en inglés; ahora es `Guardar vocabulario`.
- Limitación de la inyección serie: en el lector, A/B cortos se enrutan a
  `remoteTurn()` y solo pasan página; no mueven el cursor de selección de
  palabras. B_LONG/CONFIRM y A_LONG/BACK sí funcionan. Para probar el
  diccionario se añadió al diccionario de prueba la palabra que ya quedaba
  seleccionada («entre»).
- El diccionario y `/Vocabulary.txt` de prueba se borraron y los ajustes
  tocados (archivos ocultos, diccionario, vocabulario) se restauraron. La SD
  vuelve a mostrar solo las carpetas originales.
- Queda pendiente: Wi-Fi/OPDS/OTA, BLE, ghosting físico, autonomía y ciclos de
  suspensión con esta base.

## Sync `f8db833f` (09/11/2026)

Probado con `paperdiy-test` sobre `paperdiy-next` (`2.0.0-1`, CrossPoint
`f8db833f`, SDK `ac146e4`) y después con el build normal `paperdiy`.

- Arranque, Home, lector y page turn: correctos.
- `Crear recorte`: el cursor resalta palabras sin borrar el texto. Con los
  botones físicos, A/B mueven el cursor, B largo fija el ancla y el segundo
  B largo guarda un recorte de varias palabras. Confirmado por el usuario.
- `Enlaces y notas al pie`: el selector abre con B largo; el resaltado
  conserva el subrayado del enlace y B largo salta al destino.
- TOC: selección y salto de capítulo con A/B.
- Orientación: vertical, horizontal horario y vuelta a vertical, con la UI
  correcta en las tres.
- About: `2.0.0-1`, ESP32-S3, 16 MB, SD 7,4 GB (560 MB usados), batería
  4,12 V 100 %, LovyanGFX EPD 960×540, sin táctil/frontlight/RTC/IMU.
- USB MSC: monta `DABI`, copia de un EPUB de prueba, expulsión desde el Mac y
  vuelta automática a Home.
- Build `paperdiy`: flash correcto y arranque correcto.
- Limitación del arnés: `CMD:KEY:A/B` se enrutan a `remoteTurn()` con el
  lector en primer plano y no mueven el cursor dentro de recorte o enlaces;
  esa parte se validó con los botones físicos.
- No repetido con esta base: sleep/wake y botón power (el camino de energía no
  cambia en este sync), ghosting físico, Wi-Fi/OPDS/OTA, BLE y autonomía.
- Para la prueba se copió `PaperDIY-Link-Test.epub` a `Books/`; se puede
  borrar cuando no haga falta.
- La release `2.0.0-2` solo cambia la cadena de versión respecto al build
  `2.0.0-1` probado. El binario de release se flasheó y arrancó correctamente;
  la cadena `2.0.0-2` está presente en el binario y la Home es correcta. No se
  repitió el recorrido completo de ajustes/About sobre este binario.

## Sync `8276d518` (10/11/2026)

Probado por serie con `paperdiy-test` sobre `paperdiy-next` (`2.0.0-3`,
CrossPoint `8276d518`, SDK `6a208c0c`, commit `c50630b0`). Flash solo app,
hash verificado; bootloader y particiones intactos. Al terminar se flasheó el
build de producción `paperdiy` (`2.0.0-3`), que arranca en Home.

- Arranque y Home: rejilla de portadas y menú correctos.
- Navegación A/B y selección en Home y Ajustes.
- Lector: apertura del último libro; 10 intentos de page turn, 9 aceptados y
  uno ignorado mientras el panel estaba ocupado. Llegó a la página 10/23 sin
  errores.
- OTA: conecta a la Wi-Fi guardada y responde «No hay actualizaciones
  disponibles».
- Tipografías: catálogo de 35 fuentes; descarga e instalación de Alef correcta
  (valida el fix de cabeceras CSP del SDK).
- Orientación: horizontal (horario) redibuja Home y vuelve a vertical sin
  restos.
- OPDS: conecta a Shimokitazawa, lista el catálogo de Project Gutenberg y
  descarga `Austen, Jane - Pride and Prejudice.epub` (609.138 B) en la raíz de
  la SD. El fichero se verificó por USB y se borró después.
- USB MSC: monta `DABI` (FAT32, 8 GB), escritura y lectura de un fichero de
  prueba, expulsión desde el Mac y vuelta automática a Home. El puerto serie se
  recupera al expulsar.
- BLE: activación, escaneo con dispositivos visibles (L121240, LE_WH-1000XM5,
  ELK-BLEDOM, etc.) y desactivación. No había mando para probar el
  emparejamiento real.
- Calibre inalámbrico: arranca el servidor en Shimokitazawa y muestra la IP
  `192.168.1.154`; el plugin CrossPoint Reader está instalado en el Mac. No se
  repitió un envío completo desde Calibre.
- Observación: un `A_LONG` se ignoró durante una secuencia rápida de «atrás»;
  el reintento del arnés funcionó. No se reprodujo como fallo.
- Pendiente: ghosting/autonomía, sleep/wake, emparejamiento BLE real, envío
  Calibre completo y una instalación OTA completa. No se instrumentó el número
  exacto de refrescos e-ink; el Home se validó visualmente con caché caliente.

## Regresión determinista

`make smoke` ejecuta una secuencia fija con fixtures y aserciones OCR. Cubre
Home, apertura por explorador, page turn, TOC, enlaces, entrada/cancelación de
recorte y diccionario. Ver
[`14-device-regression.md`](14-device-regression.md) para requisitos,
limitaciones y el ciclo de power necesario para restaurar el estado.
