# Changelog

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
