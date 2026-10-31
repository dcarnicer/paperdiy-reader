# Changelog

## 2026-10-31 — sincronización con upstream `b6605a51`

- `main` avanza de `31dc683f` a `b6605a51` (20 commits).
- SDK de FreeInk actualizado de `44427f8` a `2d383f8` (52 commits) y
  re-vendorizado; el port PaperDIY se reaplicó sobre la base nueva.
- Incluye mejoras de diccionario, fuentes, plugins, portal cautivo, imágenes
  de suspensión aleatorias y correcciones de red/UI de upstream.
- `patches/sdk.patch` y `patches/firmware.patch` regenerados contra las nuevas
  bases; `firmware.patch` ahora incluye también settings y UI propios.
- Build `paperdiy` correcto tras resolver el conflicto árbol/submódulo del SDK.

## 2026-10-31 — ajuste de ghosting al pasar página

- PaperDIY: se probó `cleanBankNeedsFreshBackground=true` con una LUT
  no-drive en `lutFastest`. No redujo el ghosting y añadía refrescos completos
  visibles, así que se revirtió.
- PaperDIY: `lutFast`/`lutFastest` usan ahora la waveform AA de ED047TC1 que
  ya usa el LilyGo T5 S3. Mantiene la base B/W y el plano de grises en el
  mismo offset de LUT, evita el flash negro de `lut_fast` y da un empuje
  específico a los grises del antialiasing.
- El intervalo de refresco limpio por defecto pasa de 15 a 5 páginas. La
  migración única también mueve el 1 heredado de la prueba anterior a 5 para
  evaluar la LUT con pasada rápida; después se respeta lo que elija el lector.
- `Settings > Display > Refresh Frequency` sigue permitiendo volver a 1 página.

## 2026-10-28 — primera validación PaperDIY

- Port de CrossPoint 2.0 a M5Stack PaperDIY K159:
  - perfil `M5PAPER_DIY` y `BoardPaperDiy`;
  - bus ED047TC1 en paralelo, rail EPD del M5PM1;
  - batería/carga por PM1 (VBAT, PWR_SRC, CHG_STAT);
  - botón power del PM1 como `BTN_POWER`;
  - shutdown en batería y deep sleep con wake A/B por USB;
  - framebuffer en PSRAM, OTA configurable y tag `paperdiy`.
- Fork downstream: `main` espejo de upstream, `paperdiy` de trabajo, SDK
  vendorizado y patches separados.
- Primera validación en hardware:
  - pantalla/UI correctas en vertical;
  - A/B, batería, SD FAT32 y lectura EPUB;
  - lectura de `Amar-o-depender.epub` y `Reconciliacion.epub`;
  - Wi-Fi, web UI y subida de libros verificadas.
- Fix de ghosting al abrir el menú del lector: la primera pintada usa
  `HALF_REFRESH` y limpia la página anterior; el resto de la navegación del
  menú sigue en `FAST_REFRESH`.
- Pendiente: OPDS, Calibre/KOReader Sync, consumo/autonomía, power/shutdown,
  wake, OTA y ghosting general tras muchas páginas.
