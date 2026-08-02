# Claim 3 — VERIFIED for the declared finite contract

This is the current decomposition and Anscombe verification. It supersedes the **Historical rejected baseline** numerical decomposition at judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`, which did not test Anscombe's condition or expose its core implementation.

## Exact claim contract

Section 4.1 equations (5)–(6) write

`√n(KL_inf(q̂ₙ,m₀)−KL_inf(q,m₀)) = T₁,ₙ + T₂,ₙ`,

where `T₁,ₙ` is the empirical dual-optimization remainder and `T₂,ₙ` is the centered i.i.d. empirical-mean term. The proof establishes `T₁,ₙ → 0` in probability and applies the ordinary CLT to `T₂,ₙ`.

Lemma A.8 states the quantified Anscombe condition for `Yₙ=√n(KL_inf(q̂ₙ,m₀)−KL_inf(q,m₀))`: for every `ε>0` and `η>0`, there exist `δ∈(0,1)` and `n₀` such that every `n≥n₀` satisfies

`P(max_{k∈N: |k−n|≤nδ} |Y_k−Yₙ| > ε) < η`.

Sources: arXiv 2606.04520, [equation (5)](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.E5), [equation (6)](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.E6), and [Lemma A.8](https://ar5iv.labs.arxiv.org/html/2606.04520#A1.Thmtheorem8). The HTML was retrieved 2026-08-01 with an explicit User-Agent; SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.

The direct finite contract fixes the paper setting `q=Bernoulli(0.6)`, `m₀=0.2`. Bernoulli belongs to the bounded model, its mean differs from `m₀`, and its endpoint atom makes Assumption 4.1's exceptional equality case vacuous. The decomposition uses 10,000 paths at `n∈{200,1000,5000,50000}`. The Anscombe audit uses 5,000 paths at `n∈{500,2000,10000,50000}`, every integer prefix in each relative window `δ∈{0.2,0.1,0.05,0.02,0.01}`, and the preregistered pair `ε=0.35`, `η=0.1`.

At `n=50000`, the gate requires exact-identity error at most `2×10⁻¹²`, `T₁` RMS at most `0.01`, `T₁/T₂` RMS at most `0.02`, full-to-linear variance ratio in `[0.98,1.02]`, and strictly decreasing `T₁` RMS. For `δ=0.01` and `n≥10000`, the 95% Wilson upper bound on the exceedance probability must be below `η`; probabilities must also respect pathwise nested windows.

## Direct evidence

| n | T₁ RMS | T₁/T₂ RMS | Full/T₂ variance | Maximum identity error |
| ---: | ---: | ---: | ---: | ---: |
| 200 | 0.061725 | 0.070444 | 1.001735 | 4.44×10⁻¹⁶ |
| 1,000 | 0.027481 | 0.031270 | 1.000836 | 4.44×10⁻¹⁶ |
| 5,000 | 0.011925 | 0.013718 | 0.999874 | 4.44×10⁻¹⁶ |
| 50,000 | 0.003902 | 0.004439 | 1.000127 | 4.44×10⁻¹⁶ |

The exact identity holds pathwise, the dual remainder shrinks by a factor of 15.8 across the grid, and the full statistic's variance converges to the i.i.d. linear term's variance.

| Center n | P(exceed), δ=.20 | δ=.10 | δ=.05 | δ=.02 | δ=.01 | Wilson upper at δ=.01 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 500 | 0.9024 | 0.6038 | 0.2168 | 0.0064 | 0.0000 | 0.000768 |
| 2,000 | 0.9118 | 0.6136 | 0.2462 | 0.0152 | 0.0000 | 0.000768 |
| 10,000 | 0.9222 | 0.6366 | 0.2510 | 0.0164 | 0.0004 | 0.001457 |
| 50,000 | 0.9252 | 0.6420 | 0.2634 | 0.0162 | 0.0000 | 0.000768 |

Every integer prefix in each declared window was evaluated—there is no within-window subsampling. At `δ=0.01`, the `n≥10000` Wilson bounds are far below `η=0.1`. The independent checker replayed all deterministic streams, recomputed **40,000** decomposition paths and **100,000** Anscombe records, and found zero pathwise nesting violations: **140,000** raw records in total.

Both controls fail for the intended reasons. Replacing the empirical optimizer with `λ*+0.5` gives RMS `2.899763`, not a vanishing remainder. Applying the narrow-window `η` gate to `δ=0.2` fails with exceedance probability `0.9252`.

## Reproduction and downloadable evidence

Fixed command:

```bash
uv sync --frozen && .venv/bin/python -m reproduction.run
```

The HF run used Git SHA `7a84b5821c2d6b5dd72b6f59889d9477305d2b13`, Python 3.12.11, decomposition seed `260604221`, Anscombe seeds `260604231`–`260604234`, Hugging Face `cpu-upgrade`, and the pinned CPU-only image `ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040`. Estimated need was 2 cores; observed affinity was 64 CPUs. Claim 3 runtime was 29.320 seconds, cumulative fixed-command runtime was 52.173 seconds, and maximum RSS was 1,105,344 KiB. No GPU was allowed.

- [Claim contract](evidence/claim-3/claim_contract.json)
- [Source and assumption audit](evidence/claim-3/source_audit.md)
- [Method](evidence/claim-3/method.md) and [limitations](evidence/claim-3/limitations.md)
- [Current nonzero-exit verifier](evidence/claim-3/verify_claim.py) and [independent checker](evidence/claim-3/independent_checker.py)
- [HF verifier source](evidence/claim-3/hf_verify_claim.py), [HF checker source](evidence/claim-3/hf_independent_checker.py), and [core implementation](reproduction/claim3.py)
- [Locked configuration](reproduction/config.json), [pinned environment](pyproject.toml), and [complete lockfile](uv.lock)
- [Decomposition metrics](evidence/claim-3/decomposition_metrics.csv), [Anscombe metrics](evidence/claim-3/anscombe_metrics.csv), and [raw-parts hash manifest](evidence/claim-3/raw_parts_manifest.json)
- Raw records [1](evidence/claim-3/claim3-raw-part-00.csv), [2](evidence/claim-3/claim3-raw-part-01.csv), [3](evidence/claim-3/claim3-raw-part-02.csv), [4](evidence/claim-3/claim3-raw-part-03.csv), [5](evidence/claim-3/claim3-raw-part-04.csv), [6](evidence/claim-3/claim3-raw-part-05.csv), [7](evidence/claim-3/claim3-raw-part-06.csv)
- [HF verifier output](evidence/claim-3/verifier_output.json), [independent checker output](evidence/claim-3/checker_output.json), and [negative-control output](evidence/claim-3/negative_controls.json)
- [Runtime/CPU/Git/seed record](evidence/claim-3/environment.json), [HF artifact manifest](evidence/claim-3/hf_artifact_manifest.json), and [protected judged-revision manifest](evidence/protected-judged-revision-manifest.sha256)

## Verdict and limitation

**VERIFIED** for the exact pathwise decomposition and the declared full-prefix, assumption-satisfying finite Anscombe contract. This evidence directly answers the previous judge's missing-Anscombe and hidden-implementation criticisms. It does not prove the universal quantifiers over every admissible distribution, every positive `(ε,η)`, or all untested `n`; the paper's analytical proof is still required for that theorem-wide statement.
