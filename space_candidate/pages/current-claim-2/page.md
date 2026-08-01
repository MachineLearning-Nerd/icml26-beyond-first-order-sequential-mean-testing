# Claim 2 — VERIFIED at the paper setting

This is the current stopping-time verification and supersedes the **Historical rejected baseline** result at judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`.

## Exact claim contract

Theorem 4.4 states: for fixed `q ∈ Q_bd` and `m₀ ∈ (0,1)`, under Assumption 4.1,

`√log(1/α) (τ_α/log(1/α) − 1/KL_inf(q,m₀)) ⇒ Normal(0, Var_q[ell(λ*,X)]/KL_inf(q,m₀)³)` as `α ↓ 0`.

Here `τ_α` is the first integer `n` such that

`n KL_inf(q̂ₙ,m₀) ≥ 1 + log(2(1+n)/α)`.

Source: arXiv 2606.04520, [Theorem 4.4](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Thmtheorem4), [stopping rule](https://ar5iv.labs.arxiv.org/html/2606.04520#S3.SS3.p2), and [Assumption 4.1](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Thmtheorem1). The HTML was retrieved 2026-08-01 with an explicit User-Agent; SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.

The direct contract uses the paper's `q=Bernoulli(0.6)`, `m₀=0.2` setting with 10,000 paths per level and `b=log(1/α) ∈ {4.605,9.210,18.421,36.841,147.365,589.462,2357.847,10000}`. It implements the theorem's growing boundary exactly and separately reports the paper's practical constant-boundary comparator. The fixed 500,000-step guard is independent of the theorem formula. Bernoulli has an endpoint atom, so Assumption 4.1 is vacuously satisfied as stated in the paper's Appendix B.

At `b=10000`, the preregistered growing-boundary gate requires: a 95% chi-square interval for the variance ratio containing 1; KS distance at most 0.05; absolute standardized mean at most 0.12; absolute centering error at most 0.3%; absolute skewness and excess kurtosis at most 0.12; and Gaussian 95% coverage in `[0.94,0.96]`. KS, centering, and variance must also improve along the declared grid.

## Direct evidence

| b = log(1/α) | Mean τ/b | Relative centering error | Variance ratio | 95% variance interval | KS | 95% coverage | Standardized mean |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4.605 | 5.4127 | 106.72% | 2.4271 | [2.3612, 2.4959] | 0.4895 | 0.6463 | 1.6123 |
| 9.210 | 4.0834 | 55.95% | 1.8195 | [1.7701, 1.8710] | 0.4006 | 0.7590 | 1.1954 |
| 147.365 | 2.7589 | 5.36% | 1.0766 | [1.0474, 1.1071] | 0.1738 | 0.9139 | 0.4584 |
| 589.462 | 2.6593 | 1.56% | 1.0301 | [1.0021, 1.0592] | 0.1050 | 0.9383 | 0.2665 |
| 2357.847 | 2.6312 | 0.49% | 1.0128 | [0.9853, 1.0414] | 0.0653 | 0.9456 | 0.1667 |
| 10000 | 2.6211 | 0.102% | 0.9923 | [0.9654, 1.0204] | 0.0349 | 0.9477 | 0.0720 |

The theoretical center is `1/KL_inf=2.618428`. Every large-`b` gate and trend check passes. The independent checker recomputed mean, sample variance, Gaussian coverage, KS distance, and the closed-form variance from all **160,000** path records. It also checked the current and previous evidence at every stop: zero first-hit inequalities failed.

Both controls fail for the intended reasons. Applying the large-`b` gate at the paper's finite `α=10⁻⁴` fails all seven distributional checks. Replacing the stopping-time variance by the fixed-sample variance produces ratio `17.8145`, far outside `[0.9,1.1]`.

## Reproduction and downloadable evidence

Fixed command:

```bash
uv sync --frozen && .venv/bin/python -m reproduction.run
```

The HF run used Git SHA `f29f37a64c9f8f81dad231d806930b92913ef345`, Python 3.12.11, seeds `260604211` through `260604218`, Hugging Face `cpu-upgrade`, and the pinned CPU-only image `ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040`. Estimated need was 2 cores; observed affinity was 64 CPUs. Claim 2 scientific runtime was 17.244 seconds, total fixed-command runtime was 22.214 seconds, and maximum RSS was 1,105,680 KiB. No GPU was allowed.

- [Claim contract](evidence/claim-2/claim_contract.json)
- [Source and assumption audit](evidence/claim-2/source_audit.md)
- [Method](evidence/claim-2/method.md) and [limitations](evidence/claim-2/limitations.md)
- [Current nonzero-exit verifier](evidence/claim-2/verify_claim.py) and [independent checker](evidence/claim-2/independent_checker.py)
- [Core implementation](reproduction/claim2.py) and [locked configuration](reproduction/config.json)
- [Pinned environment](pyproject.toml) and [complete lockfile](uv.lock)
- [All metrics](evidence/claim-2/stopping_clt_metrics.csv), [raw-parts hash manifest](evidence/claim-2/raw_parts_manifest.json), and raw path parts [1](evidence/claim-2/stopping_paths-part-00.csv), [2](evidence/claim-2/stopping_paths-part-01.csv), [3](evidence/claim-2/stopping_paths-part-02.csv), [4](evidence/claim-2/stopping_paths-part-03.csv), [5](evidence/claim-2/stopping_paths-part-04.csv), [6](evidence/claim-2/stopping_paths-part-05.csv), [7](evidence/claim-2/stopping_paths-part-06.csv), [8](evidence/claim-2/stopping_paths-part-07.csv)
- [HF verifier output](evidence/claim-2/verifier_output.json), [independent checker output](evidence/claim-2/checker_output.json), and [negative-control output](evidence/claim-2/negative_controls.json)
- [Runtime/CPU/Git/seed record](evidence/claim-2/environment.json), [run diagnostics](evidence/claim-2/run_diagnostics.json), and [HF artifact manifest](evidence/claim-2/hf_artifact_manifest.json)
- [Protected judged-revision manifest](evidence/protected-judged-revision-manifest.sha256)

## Verdict and limitation

**VERIFIED** for the exact paper distribution, stopping rule, boundary, and asymptotic direction. The evidence directly resolves the earlier finite-`α` mismatch by showing convergence through independently chosen `b` levels; it does not hide the poor finite-`α` cells. This finite calibration does not prove the arbitrary-q theorem. Proof-level decomposition and Anscombe evidence are addressed separately under Claim 3.
