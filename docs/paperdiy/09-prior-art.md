# 09 — Prior art: ¿alguien más ha portado PaperDIY a CrossPoint?

Sí. La idea ya está sobre la mesa en el repo de CrossPoint, con una issue y
varios PRs en borrador. **No hay soporte upstream mergeado ni validación en
hardware**, así que el trabajo sigue abierto.

## CrossPoint: issue #4005

- **Título:** Proposal: M5Stack PaperDIY K159 support
- **Autor:** `prateek`
- **Abierta:** 17/10/2026
- **Estado:** abierta
- **Enlace:** <https://github.com/crosspoint-reader/crosspoint-reader/issues/4005>

La propuesta describe exactamente el hardware que hemos analizado: ESP32-S3,
16 MB flash, 8 MB PSRAM, ED047TC1 960×540 en paralelo, microSD, dos botones y
M5PM1, sin táctil. Propone repartir el trabajo:

- **FreeInk SDK:** perfil de placa, bus paralelo, PMIC, batería, botones.
- **CrossPoint:** build target, identidad de placa, shutdown/wake.
- **Simulador:** perfil nativo después de acordar el soporte.

También propone el mismo esquema de dos botones que usamos nosotros: A/B cortos
para anterior/siguiente, A largo = Back, B largo = Confirm. Y una diferencia
importante: **el clic del botón de power en el dispositivo encendido apagaría
el equipo**, en vez del single-click reset de fábrica; el modo descarga por USB
debe seguir funcionando.

### Respuesta del mantenedor

`Uri-Tauber` respondió el 20/10/2026:

- la batería de 140 mAh no es suficiente para un e-reader;
- haría falta una carcasa impresa en 3D;
- “tres botones no son suficientes sin pantalla táctil”;
- revisaría el PR si alguien le envía una unidad + carcasa 3D.

Es decir: el bloqueo no es solo técnico; es de **validación en hardware y de
producto**. La issue sigue abierta y sin decisión.

## PRs de prateek (borradores, forks personales)

Todos son **draft**, contra forks personales, no contra upstream. No están
mergeados y **no han sido probados en un PaperDIY físico**.

| PR | Qué hace | Estado |
|---|---|---|
| [`prateek/freeink-sdk#1`](https://github.com/prateek/freeink-sdk/pull/1) | Perfil PaperDIY, `PaperDiyBoard.h`, `BoardPaperDIY`, `PaperDiyLgfxConfig`, InputManager, tests host | Draft, abierto |
| [`prateek/crosspoint-reader#1`](https://github.com/prateek/crosspoint-reader/pull/1) | Env `paperdiy`, identidad de placa, shutdown PMIC, fallback de sueño con A/B, cambios HalGPIO/HalPowerManager/main | Draft, abierto |
| [`prateek/crosspoint-reader#2`](https://github.com/prateek/crosspoint-reader/pull/2) | Dual-boot con el firmware Companion (ota_0/ota_1) | Draft, fork-only |
| [`prateek/crosspoint-simulator#1`](https://github.com/prateek/crosspoint-simulator/pull/1) | Perfil PaperDIY en el simulador nativo + fixes de compatibilidad | Draft, abierto |

### Evidencia que aporta

- Build `pio run -e paperdiy` correcto.
- ~80.676 bytes de RAM estática y ~6,2 MB de la partición de app (94,7 %).
- Tests host de InputManager/PMIC y regresiones vecinas.
- Lectura/resume y sync nativos en simulador.
- **Nada de hardware real:** panel, SD, botones, recuperación, batería/USB wake,
  carga y consumo en sleep siguen pendientes. Ellos mismos lo dicen.

### Diferencias con nuestro port

| Tema | prateek | Nuestro repo |
|---|---|---|
| Perfil de placa | `PAPER_DIY` | `M5PAPER_DIY` |
| Bus ED047TC1 | `PaperDiyLgfxConfig` | `paperdiyLgfxConfig` |
| Rail EPD PM1 | `setEpdPower()` en `PaperDiyBoard.h` | `BoardPaperDiy::prepareEpdPower()` |
| CHG/DCDC del PM1 | No lo fuerza explícitamente | `CHG_EN | DCDC_EN` explícito |
| Botón power PM1 | Lo sondea y sintetiza `BTN_POWER`; `configureAppPowerButton()` | Integrado: `BoardPaperDiy::pollPowerButtonClicked()` + `BTN_POWER` |
| Sueño en batería | Pide shutdown al PM1; si USB sigue, deep sleep con A/B | Integrado igual |
| USB/wake | Ajusta `HalGPIO`/`HalPowerManager`/`main` | Integrado (HalGPIO/HalPowerManager/main) |
| Framebuffer | `FREEINK_FB_PSRAM` (PSRAM) | `FREEINK_FB_PSRAM` (PSRAM) |
| Tests host/simulador | Sí | No (solo build) |
| Documentación | `docs/paperdiy.md` corto | Investigación, hardware, matriz, roadmap, port, guía, fork |
| Tamaño build | ~6,2 MB / 94,7 %; ~80.676 B RAM | 5,35 MB / 81,6 %; 111.076 B RAM |
| Validación hardware | Pendiente | Parcial: pantalla/UI, A/B, batería, SD, lectura EPUB y Wi-Fi/web UI |

En resumen: **son dos implementaciones muy parecidas y ya convergen**. Hemos
integrado el botón power del PM1, el shutdown en batería, el fallback USB y el
framebuffer en PSRAM de prateek. Lo que nos falta respecto a él son los tests
host y el perfil del simulador; lo que aportamos es más documentación, más
margen de flash y una política PM1 explícita. Ninguna está validada en
hardware.

## Otros esfuerzos PaperDIY (no CrossPoint)

- [`nenipresotReta/paperdiy-reader`](https://github.com/nenipresotReta/paperdiy-reader):
  lector offline EPUB/TXT/Markdown, tipografía CJK y vertical japonesa, math
  offline, progreso por libro y paginación progresiva. Actualizado el 28/10/2026.
  Es la referencia más interesante para formatos y tipografía.
- [`RadioDisney/paperdiy-reader`](https://github.com/RadioDisney/paperdiy-reader):
  lector chino EPUB/TXT, biblioteca de 22 líneas, refresco parcial y sleep por
  inactividad; sin Wi-Fi/BLE.
- [`looher/paper-diy`](https://github.com/looher/paper-diy): mod personal chino
  con biblioteca, ajustes, Wi-Fi para subir libros, giro de 4 direcciones y
  swap A/B. Útil como referencia de UX de dos botones.

## Evidencia de hardware de otro firmware

[`dmellok/tesserae-device-firmware#55`](https://github.com/dmellok/tesserae-device-firmware/pull/55)
está **mergeado** y validado en una unidad real (no es CrossPoint):

- selftest con 16 bandas de gris alimentadas solo por el rail PM1;
- Wi-Fi y registro como `m5stack_paperdiy`;
- frame 960×540 upright en el panel;
- deep sleep por intervalo del servidor.

No probaron los dos botones ni la caída de batería durante un paint, pero
confirma que el panel, el rail PM1 y el sueño funcionan. Es una buena
referencia para el bring-up.

## Qué implica para nosotros

1. **No abrir un PR duplicado** en CrossPoint. Lo correcto es comentar en la
   issue #4005, enlazar nuestro build y ofrecer validación en hardware.
2. **No partir de cero otra vez.** Nuestro repo y el de prateek son compatibles;
   ya hemos integrado lo mejor de ambos:
   - de prateek: sondeo del botón power, shutdown en batería, fallback USB,
     `HalGPIO`/`HalPowerManager`/`main`, `FREEINK_FB_PSRAM`;
   - nuestro: política CHG/DCDC explícita, documentación, build con más margen,
     BLE page turner + USB MSC.
   Queda pendiente adoptar sus tests host y el perfil del simulador.
3. **La pieza que falta es hardware.** El mantenedor quiere una unidad y una
   carcasa para revisar; al menos hacen falta logs/fotos/medidas de una unidad
   real. Tú tienes una; ahí podemos aportar algo que ninguno de los PRs tiene.
4. **La UX de dos botones y la batería son el argumento de producto.** Si el
   port no resuelve eso, el mantenedor no lo aceptará aunque compile.

## Recomendación

- Comentar en #4005 con: build propio, diferencias, disposición a probar en
  hardware y resultados de la validación.
- Ya está integrado el power/USB/wake de prateek; el siguiente paso es **probar
  el build en hardware**, no seguir moviendo código.
- Si el port funciona, proponer un PR conjunto (o dejar que prateek lidere el
  upstream) en vez de mantener dos forks divergentes.
- Mantener el fork downstream para las features PaperDIY-specific (UX, docs,
  BLE, mods) y seguir upstream para el motor.
