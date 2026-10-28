# 07 — Guía de usuario (PaperDIY)

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
| Power ~2 s | modo descarga (LED rojo) |

El clic del power ya no hace reset de fábrica: el PM1 se lo entrega al
firmware. Si prefieres el comportamiento original, compila con
`-DPAPERDIY_PM1_APP_POWER_BUTTON=0` y usa A+B para dormir.

En el lector, A/B pasan página. En listas, mueven la selección; B largo abre el
elemento; A largo vuelve.

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

- **Settings → Network**: escanea/une a Wi-Fi (2,4 GHz).
- **Web UI**: la dirección aparece en pantalla; desde el navegador puedes subir
  libros, ver archivos, cambiar ajustes y actualizar.
- **Calibre**: usa "Connect to wireless device" en Calibre; el lector muestra
  el flujo.
- **OPDS**: añade catálogos (Project Gutenberg, Standard Ebooks, etc.) y navega
  desde el lector.
- **KOReader Sync**: configura credenciales y sincroniza progreso.
- **OTA**: busca actualizaciones desde Settings; también puedes flashear por
  USB.

## Energía y sueño

- El lector duerme solo tras un timeout de inactividad.
- Para dormir manualmente: mantén A+B o pulsa el power (según la acción
  configurada).
- En batería, al dormir pide **apagado** al PM1: el equipo se apaga y un clic
  lo enciende de nuevo (la página queda en el panel).
- Con USB conectado, hace **deep sleep** y despierta con A o B.
- Si vas a estar mucho tiempo sin usar el equipo, apágalo con doble clic.
- La batería es de 140 mAh: la autonomía depende de dormir. Si lees con Wi-Fi
  encendida, baja mucho.

## SD: organización recomendada

```
/
├── Books/                 # tus EPUB (puedes usar carpetas)
├── fonts/                 # TTF/OTF
├── dictionaries/          # StarDict por carpeta
└── .crosspoint/           # caché del lector (no tocar salvo reset)
```

## Problemas comunes

| Síntoma | Qué probar |
|---|---|
| Pantalla en blanco | ¿PM1 GPIO2/GPIO46? ¿DCDC? ¿flasheo completo? |
| Imagen invertida | cambiar `rotation` en `paperdiyLgfxConfig` (0 ↔ 2) |
| Ghosting | refresco completo periódico; probar `cleanBankNeedsFreshBackground`/LUTs |
| No monta la SD | FAT32/exFAT, contacto, probar otra tarjeta |
| No pasa página | ¿batería? ¿A/B? ¿está en modo sleep? |
| No despierta | ¿el botón está bien? ¿`ext1` GPIO3/4? |
| Batería rara | leer VBAT del PM1; calibrar; comprobar carga |
| Wi-Fi no conecta | 2,4 GHz, contraseña, AP aislado; probar hotspot |
| Libro no abre | EPUB válido, tamaño, RAM; borrar caché del libro |
| UI rara tras update | borrar `/.crosspoint/` y reiniciar |

## Recuperación

Si algo falla:

1. Mantén power ~2 s hasta LED rojo → download mode.
2. Flashea `firmware.factory.bin` en `0x0`.
3. Si no entra en download mode, prueba otro cable/USB; el ESP32-S3 nativo no
   necesita adaptador.

Guarda siempre un backup del firmware original antes de experimentar.
