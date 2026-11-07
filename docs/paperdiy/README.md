# Documentación PaperDIY

**Idiomas:** **Español** · [English](README.en.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

Índice de la documentación propia del port (la documentación original de
CrossPoint sigue en `docs/` y `docs/upstream/`).

> El README principal, la guía de usuario y las notas de hardware y port están
> traducidos al inglés, chino simplificado y japonés. El resto de la
> documentación detallada está por ahora en español.

1. [Investigación y estado actual](00-research.md)
2. [Hardware y pines](01-hardware.md) — [English](01-hardware.en.md) · [简体中文](01-hardware.zh-CN.md) · [日本語](01-hardware.ja.md)
3. [Análisis del POC y del ecosistema](02-current-state.md)
4. [Matriz de funcionalidades](03-feature-matrix.md)
5. [Arquitectura](04-architecture.md)
6. [Roadmap](05-roadmap.md)
7. [Notas del port y validación](06-porting.md) — [English](06-porting.en.md) · [简体中文](06-porting.zh-CN.md) · [日本語](06-porting.ja.md)
8. [Guía de usuario](07-user-guide.md) — [English](07-user-guide.en.md) · [简体中文](07-user-guide.zh-CN.md) · [日本語](07-user-guide.ja.md)
9. [Fuentes](08-sources.md)
10. [Prior art: issue #4005 y PRs de PaperDIY](09-prior-art.md)
11. [Mantener el fork y actualizar upstream](10-fork-maintenance.md)
12. [Borrador de comentario para la issue #4005](11-upstream-note.md)
13. [Testing por USB](12-serial-testing.md)
14. [M5Launcher](13-m5launcher.md) — [English](13-m5launcher.en.md)

## Estado en una frase

El port **compila, arranca y se ha validado en un PaperDIY real** (pantalla,
botones, SD, batería, Wi-Fi, lectura EPUB, OPDS y Calibre wireless). También
se validaron auto-suspensión y sleep screen con portada. La lectura larga
automatizada aguantó 250+ cambios de página sin errores ni fugas (06/11).
KOReader Sync se validó contra un servidor KOSync local (06/11). Quedan
pendientes emparejar un mando BLE, consumo en sleep/autonomía, validar la
batería 604050 y la revisión visual física del ghosting. Empieza por
`06-porting.md`.
