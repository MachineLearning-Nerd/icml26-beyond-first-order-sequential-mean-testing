---
title: "Repro - Beyond First-order Asymptotics in Sequential Mean Testing"
emoji: 🎯
colorFrom: yellow
colorTo: red
sdk: static
pinned: false
tags:
 - trackio
 - trackio-logbook
 - open-experiment
 - icml2026-repro
 - paper-HMyCBL2yMV
---

# Repro - Beyond First-order Asymptotics in Sequential Mean Testing

Current verification begins at [Claim 4 — FALSIFIED as literally supplied](#/current-claim-4): Proposition 4.5 covers the deterministic `1/KL_inf`, not a random stopping time, while its actual same-path formula is calibrated at 0.9513/0.5010 for nominal 95%/50% coverage. It is followed by [Claim 3 — VERIFIED for the declared finite contract](#/current-claim-3), [Claim 2 — VERIFIED at the paper setting](#/current-claim-2), and the preserved [Claim 1 — VERIFIED](#/current-claim-1). Each current page exposes the exact contract, assumption audit, executable verifier, full raw output, independent checker, negative controls, fixed command, locked environment, and CPU/runtime provenance.

Pages labeled **Historical rejected baseline** are preserved evidence from judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`; they are not the current verifier.

An open experiment logbook, published with [Trackio](https://github.com/gradio-app/trackio).
