# 11 — Borrador de comentario para la issue #4005

> **No publicado.** Es un borrador para que lo revises antes de pegarlo en
> <https://github.com/crosspoint-reader/crosspoint-reader/issues/4005>.
> El tono es deliberadamente de coordinación, no de “mi PR es mejor”.

---

Hi @prateek, @Uri-Tauber,

I’ve been following #4005 and built an independent downstream fork for the
PaperDIY K159. I don’t want to duplicate the draft PRs; I’m mostly interested in
getting the hardware validated and coordinating on the board layer.

What I have:

- `main` mirrors `upstream/develop`; `paperdiy` is the fork. `freeink-sdk` is
  vendored so the repo builds without submodules.
- `pio run -e paperdiy` passes: 5.35 MB / 81.6% of the app partition, 111 KB
  static RAM. Board tag is `paperdiy`.
- I integrated prateek’s PM1 power-button/USB-wake/shutdown approach and the
  `FREEINK_FB_PSRAM` change, plus an explicit `CHG_EN | DCDC_EN` PM1 policy and
  CHG_STAT battery status.
- The port is split into `patches/sdk.patch` and `patches/firmware.patch` so it
  can be rebased on new upstream releases.
- Docs: hardware notes, feature matrix, roadmap, validation checklist, fork
  maintenance.

What I don’t have yet: physical validation. I have an assembled PaperDIY K159
and can test the panel/rotation/LUTs/ghosting, A/B and PM1 power button,
battery/charging, sleep current, SD, Wi-Fi, OTA and recovery. I haven’t flashed
it yet because I want to keep a backup of the stock firmware and do a controlled
bring-up.

Questions:

1. Would it be more useful to test prateek’s `feat/paperdiy` branch first, or my
   fork, or both and compare?
2. Where would you like the results: this issue, a new “PaperDIY bring-up”
   issue, or a PR comment?
3. Would a combined upstream PR (board layer from FreeInk + the minimal
   HalGPIO/HalPowerManager/main changes) be welcome once there are hardware
   results, or do you prefer to keep the device downstream for now?

I’m happy to provide logs, photos, refresh timings and current measurements, and
to adjust the design if the 2-button UX or the 140 mAh battery turn out to be a
blocker. I’m not asking for maintainer time until there is real hardware
evidence.

---

## Notas para publicarlo

- Adjuntar el enlace al repo/fork cuando exista un remoto público.
- No afirmar “funciona en hardware” hasta tener las medidas.
- Si se publica, incluir fotos del montaje, versión del panel, y el resultado de
  `esptool flash-id` (16 MB).
- Ofrecer datos, no pedir que acepten el PR.
