# 07 — Guía de usuario (PaperDIY)

**Idiomas:** **Español** · [English](07-user-guide.en.md) · [简体中文](07-user-guide.zh-CN.md) · [日本語](07-user-guide.ja.md)

Esta guía asume que ya has flasheado el firmware. Si todavía no, mira el
[README](../../README.md) y `06-porting.md`.

## Primer arranque

1. Copia libros `.epub` a la SD (FAT32 o exFAT). Puedes usar carpetas.
2. Inserta la SD.
3. Enciende con un clic al botón de power.
4. La primera pantalla es la biblioteca/home. Con A/B te mueves; B largo
   confirma; A largo vuelve atrás.

La primera apertura de un libro genera caché en `/.crosspoint/` (tarda unos
segundos). Las siguientes son mucho más rápidas.

## Controles

| Gesto | Acción |
|---|---|
| A corto | arriba / página anterior |
| B corto | abajo / página siguiente |
| A largo | atrás / salir |
| B largo | confirmar / seleccionar |
| A+B | power (menú/dormir) |
| Power clic | encender; en marcha, acción configurada (por defecto dormir/apagar) |
| Power doble clic | apagar (hardware, si el PM1 lo mantiene) |
| Power ~10 s | modo descarga (LED rojo; la pantalla puede congelarse) |

El clic del power ya no hace reset de fábrica: el PM1 se lo entrega al
firmware. Si prefieres el comportamiento original, compila con
`-DPAPERDIY_PM1_APP_POWER_BUTTON=0` y usa A+B para dormir.

En el lector, A/B pasan página. En listas, mueven la selección; B largo abre el
elemento; A largo vuelve.

Los controles están agrupados en `Ajustes > Controles` en **Botón de
encendido**, **Botones frontales**, **Botones laterales** y **Toques y gestos**.
En `Ajustes > Controles > Botones laterales > Orientar botones laterales` puedes
hacer que A/B inviertan la dirección al pasar a horizontal; en vertical
invertida se invierten siempre. Está desactivado por defecto, también al
actualizar desde una versión anterior.

Los clics cortos se registran **al soltar**, no al pulsar: es lo que permite
distinguir un clic de una pulsación larga con solo dos botones. Si se cambia a
“page on press”, la pulsación larga puede disparar antes una página/movimiento
antes de abrir el menú; es un compromiso de UX pendiente de decidir.

## Biblioteca

- La home muestra recientes/portadas; el navegador de archivos permite entrar
  en carpetas.
- B largo sobre un libro abre el menú (abrir, detalles, borrar, etc.).
- Los metadatos y portadas se cachean en `/.crosspoint/`; si algo queda raro,
  borra esa carpeta y se regenera.

## Leer

- B largo abre el menú del lector: TOC, bookmarks, highlights, diccionario,
  ir a %, ajustes de texto, orientación, etc.
- A largo vuelve al menú anterior.
- La posición se guarda automáticamente.
- Los highlights/clippings se guardan en la SD (ver menú del lector).

## Cómics

- El firmware no abre `.cbz`/`.cbr` directamente: primero hay que convertirlos a
  EPUB con una página XHTML por imagen.
- **Máxima calidad (recomendado): Kindle Comic Converter (KCC)**. Usa el perfil
  `Other` con ancho 540 y alto 960, modo manga, recorte de márgenes + números
  de página, separación de páginas dobles, escala de grises y PNG de 16
  niveles. En la app de escritorio, activa el modo experto para elegir `Other`
  y el tamaño personalizado. Con KCC 12.1.3 por CLI:

  ```sh
  kcc-c2e tomo.pdf -p OTHER --customwidth 540 --customheight 960 \
    -f EPUB --nokepub -c 2 -r 0 -m -q -u --forcepng \
    -t "Tomo 1" -a "Autor" -o tomo.epub
  ```

  KCC recorta los márgenes, ajusta el ancho a los 540 px reales del panel y
  evita que el lector tenga que reescalar. En TOMO2 el contenido quedó ~20% más
  grande y el archivo pasó de 23 MB a 13 MB.
- **Alternativa sin KCC**: `scripts/comic_to_epub.py`, que genera un XHTML por
  página. Acepta CBZ/ZIP o PDF:

  ```sh
  python3 scripts/comic_to_epub.py tomo.cbz tomo.epub
  python3 scripts/comic_to_epub.py tomo.pdf tomo.epub --title "Tomo 1" --author "Autor"
  ```

  Para PDF necesita `pdftoppm` (`brew install poppler` en macOS).
- Calibre también puede convertir CBZ a EPUB, pero no recorta ni ajusta al
  panel; úsalo solo si no tienes KCC.
- Copia los EPUB a `/Comics/` en la SD. En la primera apertura el lector indexa
  el libro: puede tardar decenas de segundos y los botones no responden hasta
  que termina.
- El EPUB debe tener una página XHTML por imagen. Los EPUB de PDF-reflow con un
  único HTML (o pasados por el optimizador del plugin de Calibre) pueden
  quedarse en `1/1` y no paginar.
- El menú puede mostrar `Cap.: 1/1 pág.` porque cada página es un documento
  distinto; el avance real se ve en `Página N` y `Libro: %`.

## Fuentes

- Copia `.ttf`, `.otf` o `.ttc` a `/fonts/` o `/.fonts/` en la SD.
- Puedes agrupar una familia en una subcarpeta.
- En ajustes de lectura selecciona la fuente; los estilos regular/bold/italic
  se emparejan por familia.
- Para IPA (diccionario) necesitas una fuente que cubra esos glifos.

## Diccionarios

- Copia cada diccionario StarDict a `/dictionaries/<nombre>/` (o
  `/.dictionaries/`), con `.idx` sin comprimir y `.dict`/`.dict.dz`.
- En **Settings → Reader → Dictionary** selecciona el diccionario.
- La primera búsqueda indexa (genera `.qidx`/`.sidx`); luego es rápida.
- Para español, busca un StarDict de Wiktionary/RAE/WikDict y prueba.

## Wi-Fi, Calibre, OPDS y web UI

- **Ajustes → Conectividad**: escanea/une a Wi-Fi (2,4 GHz).
- **Web UI**: la dirección aparece en pantalla; desde el navegador puedes subir
  libros, ver archivos, cambiar ajustes y actualizar.
- **Calibre**: usa "Connect to wireless device" en Calibre; el lector muestra
  el flujo.
- **OPDS**: añade catálogos (Project Gutenberg, Standard Ebooks, etc.) en
  `Ajustes → Conectividad → Servidores OPDS` y ábrelos desde
  `Transferir archivos → Navegador OPDS` (o desde Inicio si el sistema de
  plugins está desactivado y ya hay un servidor guardado).
- **KOReader Sync**: configura credenciales y sincroniza progreso contra el
  servidor oficial o uno propio (KOSync).
- **OTA**: busca actualizaciones desde Settings; también puedes flashear por
  USB.

## Energía y sueño

- El lector duerme solo tras un timeout de inactividad.
- Para dormir manualmente: mantén A+B o pulsa el power (según la acción
  configurada).
- En batería, al dormir pide **apagado** al PM1: el equipo se apaga y un clic
  lo enciende de nuevo (la página queda en el panel).
- Con USB conectado, el PM1 también puede cortar la alimentación; en ese caso
  solo power enciende. El fallback **deep sleep** con wake A/B solo ocurre si
  el USB mantiene la placa viva.
- Si vas a estar mucho tiempo sin usar el equipo, apágalo con doble clic.
- La batería es de 140 mAh: la autonomía depende de dormir. Si lees con Wi-Fi
  encendida, baja mucho.

## SD: organización recomendada

```
/
├── Books/                 # tus EPUB (puedes usar carpetas)
├── Comics/                # cómics convertidos a EPUB
├── fonts/                 # TTF/OTF
├── dictionaries/          # StarDict por carpeta
└── .crosspoint/           # caché del lector (no tocar salvo reset)
```

`Ajustes > Acerca de` muestra el tamaño total, usado y libre de la SD. La
primera consulta puede tardar unos segundos porque recorre la FAT.

## Problemas comunes

| Síntoma | Qué probar |
|---|---|
| Pantalla en blanco | ¿PM1 GPIO2/GPIO46? ¿DCDC? ¿flasheo completo? |
| Imagen invertida | cambiar `rotation` en `paperdiyLgfxConfig` (0 ↔ 2) |
| Ghosting al pasar páginas | probar `Refresh Frequency` en 5 y luego en 1 en Ajustes > Pantalla; la LUT rápida nueva está en validación |
| No monta la SD | FAT32/exFAT, contacto, probar otra tarjeta; si no hay tarjeta al arrancar, insertarla y el equipo reinicia |
| No pasa página | ¿batería? ¿A/B? ¿está en modo sleep? |
| No despierta | ¿el botón está bien? ¿`ext1` GPIO3/4? |
| Batería rara | mirar `About > Battery` (VBAT/estado) o el log `[PWR] Battery:`; recalibrar si se cambia la celda |
| Wi-Fi no conecta | 2,4 GHz, contraseña, AP aislado; probar hotspot |
| Libro no abre | EPUB válido, tamaño, RAM; borrar caché del libro |
| UI rara tras update | borrar `/.crosspoint/` y reiniciar |

## Recuperación

Si algo falla:

1. Mantén power ~10 s hasta LED rojo → download mode.
2. Flashea `crosspoint-paperdiy-latest.bin` de la release (o
   `firmware.factory.bin` de un build local) en `0x0`.
3. Si no entra en download mode, prueba otro cable/USB; el ESP32-S3 nativo no
   necesita adaptador.

Guarda siempre un backup del firmware original antes de experimentar.
