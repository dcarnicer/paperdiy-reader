# 14 — Regresión determinista en hardware

`make smoke` ejecuta una secuencia fija sobre un PaperDIY conectado por USB.
No sustituye la validación física (ghosting, autonomía, botones power), pero
convierte las comprobaciones de UI y lector en algo repetible tras cada build.

## Requisitos

- Build `paperdiy-test` flasheado: la inyección de teclas no existe en el build
  de producción.
- `tesseract` con el modelo inglés (`brew install tesseract`).
- macOS, porque el montaje de la SD usa `diskutil`.
- El dispositivo conectado por USB y, preferiblemente, en Home.

## Uso

```bash
make build ENV=paperdiy-test
make flash ENV=paperdiy-test PORT=/dev/cu.usbmodemXXXX
make smoke PORT=/dev/cu.usbmodemXXXX
```

El runner se puede invocar directamente:

```bash
python3 scripts/device_regression.py --port /dev/cu.usbmodemXXXX
python3 scripts/device_regression.py --skip-prepare   # fixtures ya instalados
python3 scripts/device_regression.py --no-restore     # conservar estado para depurar
python3 scripts/device_regression.py --eject          # expulsar en vez de pedir power-cycle
python3 scripts/device_regression.py --restore-only build/device-regression/<run>
```

El script comprueba al arrancar que el firmware responde a `CMD:KEY`; si no,
falla con un mensaje que pide flashear `paperdiy-test`.

## Qué hace

1. Entra en **Unidad USB** y hace copia de seguridad de los ficheros que toca:
   `settings.json`, `recent.json`, `state.json`, `koreader.json`,
   `My Clippings.txt` y `Vocabulary.txt`.
2. Instala fixtures deterministas:
   - `/SmokeTest/paperdiy-smoke-<run>.epub`: EPUB con dos capítulos, enlace,
     nota al pie y texto suficiente para dos páginas.
   - `/dictionaries/smoke`: diccionario StarDict mínimo con las palabras del
     fixture.
3. Fija idioma inglés, tema Lyra, diccionario `smoke` y auto-suspensión nunca.
4. Ejecuta la secuencia y valida el texto visible con OCR:
   - Home y apertura del libro por el explorador de archivos.
   - Page turn y vuelta atrás.
   - Menú del lector y TOC, incluyendo volver al capítulo 1.
   - Selector de enlaces y nota al pie.
   - Entrada y cancelación del modo recorte.
   - Búsqueda en el diccionario y definición.
5. Restaura los ficheros originales, elimina fixtures y borra las cachés EPUB
   creadas durante la prueba. Por defecto **no expulsa**: deja la SD restaurada
   y el equipo en modo USB para que hagas un ciclo de power. Así el firmware no
   sobrescribe el estado restaurado con el que tenía en memoria. Con `--eject`
   se expulsa y se vuelve a Home, pero el estado en memoria puede pisar la
   restauración.

## Resultado actual

`2026-11-12`, PaperDIY `2.0.0-4` (`paperdiy-test`), run
`20261112-115404`: **PASS, 25 pasos**. Tras restaurar y hacer un ciclo de
power, el dispositivo volvió a Home en español con los recents originales y
sin `SmokeTest`.

El guardado de un recorte no se valida por serie: el modo selección consume
los `Confirm` de forma poco fiable con la inyección actual. El runner valida
que el modo recorte abre y se cancela; el guardado sigue siendo una prueba
manual con los botones físicos.

Las capturas, el `report.json` y la copia de seguridad quedan en
`build/device-regression/<fecha-hora>/`.

## Qué no cubre todavía

- OPDS, KOReader Sync y Calibre wireless (tienen su propio componente de red;
  se pueden añadir como escenarios separados).
- USB MSC como prueba funcional independiente: el runner lo usa para instalar
  fixtures, pero no valida escritura/expulsión como caso de test.
- Guardado de recortes (limitación del arnés serie; validar con botones
  físicos).
- BLE real (hace falta un mando), sleep/wake físico, corriente de sueño,
  autonomía y ghosting visual.
- El número exacto de refrescos e-ink: el Home se valida por contenido, no por
  contador de refrescos.

Los pendientes manuales siguen en
[`06-porting.md`](06-porting.md#checklist-de-validación-en-hardware).
