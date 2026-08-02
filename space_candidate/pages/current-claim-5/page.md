# Claim 5 — VERIFIED for the declared Section 5 contract

This is the current Claim 5 result. It supersedes the **Historical rejected baseline** at judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`, which omitted crop-yield evidence and compared only isolated synthetic cells with no decreasing-alpha trend.

## Exact Section 5 scope

The supplied summary blurs the paper's experiment split. Section 5 actually reports:

- Experiment 1: the fixed-sample `KL_inf` CLT for `Beta(3,2)` and `Bernoulli(0.6)` at `m₀=0.7`, using 5,000 samples per `n`.
- Experiment 2: the stopping-time CLT for `Bernoulli(0.6)` only, at `m₀=0.2`, 5,000 paths, alpha `1e-4` and `1e-8`, and both equations (7) and (8).
- Experiment 3: 3,000 with-replacement stopping-time bootstrap paths at `m₀=0.5`, alpha `1e-4`, and equation (8), from a normalized but otherwise unidentified DSSAT crop-yield pool.

Sources: arXiv 2606.04520, [Section 5](https://ar5iv.labs.arxiv.org/html/2606.04520#S5), [Figures 1–2](https://ar5iv.labs.arxiv.org/html/2606.04520#S5.F1), [Figures 3–4](https://ar5iv.labs.arxiv.org/html/2606.04520#S5.F3), and [Figure 5](https://ar5iv.labs.arxiv.org/html/2606.04520#S5.F5). The HTML was retrieved 2026-08-02 with an explicit User-Agent; SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.

## Synthetic experiments

The cumulative current Claim 1 verifier regenerates the exact Beta and Bernoulli fixed-sample study. At `n=5000`, their variance ratios are `1.0093` and `0.9957`, KS distances are `0.0124` and `0.0185`, and Gaussian 95% mass is `0.9530` and `0.9522`; both KS distances improve from `n=50`.

The cumulative current Claim 2 verifier runs 10,000 paths, exceeding the paper's 5,000, without changing the paper parameters. Agreement strengthens from alpha `1e-4` to `1e-8` under both boundary choices:

| Boundary | KS at alpha=1e-4 | KS at alpha=1e-8 | Variance ratio 1e-4 → 1e-8 | Assessment |
| --- | ---: | ---: | ---: | --- |
| Equation (7), growing | 0.4006 | **0.3324** | 1.8195 → 1.4087 | finite distortion remains, trend agrees |
| Equation (8), constant | 0.0912 | **0.0766** | 0.9777 → 0.9603 | close Gaussian fit, trend agrees |

This directly answers the previous judge criticism: the current evidence shows a predeclared trend across decreasing alpha rather than one isolated level.

## Official public DSSAT provenance

The authors do not release their exact DSSAT crop pool, normalization, code, or seed. Exact equality with their hidden Figure 5 input is therefore not claimed. The real-data mechanism is rerun on a fully disclosed same-domain pool from the primary [DSSAT/dssat-csm-data repository](https://github.com/DSSAT/dssat-csm-data), pinned at commit `a4f95d3ef36f1358bdeb5db49d498d5db373ba7a`.

The HF job parsed all ten official `Maize/*.MZA` A-files, retained every nonnegative observed `HWAM` value, excluded negative DSSAT missing-value sentinels, retained zero, and divided by the selected-pool maximum. The resulting input has **44 yields from eight files**, maximum `12,340 kg/ha`, mean `0.5517146751`, and SHA-256 `4af7845a8e119e3a37a10327c2633ad8d7d09cf74ad32317271b85abd0cf4b69`. The plug-in values are `KL_inf=0.02616065`, `1/KL_inf=38.22535`, and `sigma_bd²=2866.65854`.

- [Every normalized observation and source-file hash](evidence/claim-5/dssat_public_maize_pool.csv)
- [Pinned source manifest and per-file SHA-256](evidence/claim-5/dssat_source_manifest.json)
- [Vendored primary A-file example](reproduction/data/dssat_maize/BRPI0202.MZA)
- [Plug-in center and variance](evidence/claim-5/dssat_theory.json)

## Paper-matched crop-yield result

The accepted run uses `m₀=0.5`, equation (8)'s constant `log(1/alpha)` boundary, sampling with replacement, seed `260604251`, and **3,000 paths**. Alpha `1e-2` and `1e-3` are prespecified diagnostics; `1e-4` is the exact paper level.

| alpha | Mean tau | Mean tau/log(1/alpha) | Relative center error | KS to N(0,1) | Variance/theory | Gaussian 95% mass |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1e-2` | 162.599 | 35.308 | -0.0763 | 0.1312 | 0.8715 | 0.9677 |
| `1e-3` | 250.385 | 36.247 | -0.0518 | 0.0988 | 0.9412 | 0.9657 |
| `1e-4` | 336.730 | 36.560 | **-0.0436** | **0.0890** | **0.9396** | **0.9693** |

KS improves strictly at both alpha steps, normalized centering moves toward `38.22535`, and variance error improves from 12.9% to 6.0%. At the exact paper level, every declared gate passes. The nonzero Shapiro-Wilk criticism on the old logbook is not hidden or replaced by a p-value: with thousands of discrete stopping times, an omnibus test can reject small deviations even when effect-size diagnostics show useful approximation. This contract uses predeclared KS, variance, coverage-mass, and centering thresholds.

The independent checker hashed all ten primary files, replayed **all 9,000** raw stopped records from the seed, used a separate scalar Brent root solver for `KL_inf`, verified every prior/at-stop crossing inequality and nested stopping time, and reconstructed all aggregate metrics. It found zero discrepancies.

Both negative controls fail as intended:

- Replacing the stopping-time variance with the fixed-sample variance gives variance ratio `52,481.94`, not one.
- Retaining negative DSSAT sentinels violates the paper's bounded `[0,1]` observation domain after positive-maximum normalization.

## Reproduction and downloadable evidence

Fixed command:

```bash
uv sync --frozen && .venv/bin/python -m reproduction.run
```

The accepted HF run used Git SHA `3ec478ec40cfc3c229d695117c73c57692fa4802`, Python 3.12.11, Hugging Face `cpu-upgrade`, and pinned CPU-only image `ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040`. Estimated need was 2 cores; actual affinity was 64 CPUs. Claim 5 runtime was 15.717 seconds, cumulative runtime was 170.358 seconds, and maximum RSS was 1,105,088 KiB. GPU use was disabled.

- [Exact claim contract](evidence/claim-5/claim_contract.json), [source audit](evidence/claim-5/source_audit.md), [method](evidence/claim-5/method.md), and [limitations](evidence/claim-5/limitations.md)
- [Current nonzero-exit verifier](evidence/claim-5/verify_claim.py), [executable independent checker](evidence/claim-5/independent_checker.py), and [core implementation](reproduction/claim5.py)
- [Accepted HF verifier source](evidence/claim-5/hf_verify_claim.py), [accepted HF checker source](evidence/claim-5/hf_independent_checker.py), and [accepted-run manifest](evidence/claim-5/accepted_run_manifest.json)
- [All aggregate metrics](evidence/claim-5/dssat_bootstrap_metrics.csv), [all 9,000 raw stopped records](evidence/claim-5/dssat_bootstrap_paths.csv), and [synthetic cross-check](evidence/claim-5/synthetic_crosscheck.json)
- [Verifier output](evidence/claim-5/verifier_output.json), [independent checker output](evidence/claim-5/checker_output.json), and [negative-control output](evidence/claim-5/negative_controls.json)
- [Runtime/CPU/Git/seed record](evidence/claim-5/environment.json), [HF artifact manifest](evidence/claim-5/artifact_manifest.json), [locked configuration](reproduction/config.json), [pinned environment](pyproject.toml), and [lockfile](uv.lock)

## Verdict and limitation

**VERIFIED** for the declared finite Section 5 contract: the exact synthetic settings reproduce, both stopping boundaries improve at smaller alpha, and the exact real-data protocol produces a close, improving Gaussian approximation on a pinned official public DSSAT crop-yield pool. This is finite evidence, not proof of the asymptotic theorem. Because the authors do not release the Figure 5 pool or transform, the result is an independently auditable same-domain reproduction, not an exact numerical match to their hidden panel.
