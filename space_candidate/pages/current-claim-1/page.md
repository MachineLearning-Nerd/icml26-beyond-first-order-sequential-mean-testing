# Claim 1 — VERIFIED

This is the current verification and supersedes the **Historical rejected baseline** verifier at revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`.

## Exact claim contract

Theorem 4.2 states: for fixed `q ∈ Q_bd` and `m₀ ∈ (0,1)`, with i.i.d. `Xᵢ ~ q` and Assumption 4.1,

`√n (KL_inf(q̂ₙ,m₀) − KL_inf(q,m₀)) ⇒ Normal(0, Var_q[ell(λ*,X)])` as `n → ∞`.

Source: arXiv 2606.04520, [Theorem 4.2](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Thmtheorem2) and [Assumption 4.1](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Thmtheorem1). The HTML was retrieved 2026-08-01 with an explicit User-Agent; SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.

The finite contract uses the paper's Section 5 settings: `m₀=0.7`, `Beta(3,2)` and `Bernoulli(0.6)`, 5,000 independent replicates at each `n ∈ {50,200,1000,5000}`. At `n=5000`, each distribution must have variance ratio in `[0.9,1.1]`, KS distance at most `0.04`, a 95% Wilson interval for Gaussian 95% coverage containing `0.95`, absolute standardized mean at most `0.05`, and improved KS distance relative to `n=50`.

Assumption 4.1 is audited numerically and analytically. Bernoulli has endpoint atoms, so the exceptional equality case is vacuous. For `Beta(3,2)`, `(1−m₀)(a+b−1)/(b−1)=1.2 ≠ 1`. The population dual score residual is `7.63×10⁻¹⁷`.

## Direct evidence

| Distribution | n | Variance ratio | KS distance | Gaussian 95% coverage | Wilson interval | Standardized mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Beta(3,2) | 50 | 1.0280 | 0.0466 | 0.9474 | [0.9409, 0.9533] | 0.1527 |
| Beta(3,2) | 5,000 | 1.0093 | 0.0124 | 0.9530 | [0.9468, 0.9585] | 0.0187 |
| Bernoulli(0.6) | 50 | 1.1946 | 0.2303 | 0.9002 | [0.8916, 0.9082] | 0.3169 |
| Bernoulli(0.6) | 5,000 | 0.9957 | 0.0185 | 0.9522 | [0.9459, 0.9578] | 0.0165 |

All preregistered large-`n` checks pass. The independent raw-data checker recomputed mean, variance, coverage, and KS distance for all 40,000 replicates and exited `0`. The negative control deliberately applies the large-`n` gate to discrete Bernoulli at `n=50`; it fails variance, KS, coverage, and centering as intended.

## Reproduction and downloadable evidence

Fixed command:

```bash
uv sync --frozen && .venv/bin/python -m reproduction.run
```

The run used Git SHA `5b4e0230ec91d15f4193bab883630af9af879f5c`, Python 3.12.11, seeds `260604201` and `260604202`, Hugging Face `cpu-upgrade`, and the pinned CPU-only image `ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040`. Estimated need was 2 cores; observed affinity was 64 CPUs. Scientific runtime was 4.456 seconds, job duration 31 seconds, and maximum RSS was 1,105,044 KiB. No GPU was allowed.

- [Claim contract](evidence/claim-1/claim_contract.json)
- [Source and assumption audit](evidence/claim-1/source_audit.md)
- [Method](evidence/claim-1/method.md) and [limitations](evidence/claim-1/limitations.md)
- [Current nonzero-exit verifier](evidence/claim-1/verify_claim.py)
- [Core implementation](reproduction/klinf.py), [experiment implementation](reproduction/claim1.py), and [locked configuration](reproduction/config.json)
- [Pinned environment](pyproject.toml) and [complete lockfile](uv.lock)
- [All metrics](evidence/claim-1/fixed_clt_metrics.csv) and [all 40,000 raw standardized replicates](evidence/claim-1/fixed_clt_replicates.csv)
- [Verifier output](evidence/claim-1/verifier_output.json), [independent checker output](evidence/claim-1/checker_output.json), and [negative-control output](evidence/claim-1/negative_control.json)
- [Runtime/CPU/Git/seed record](evidence/claim-1/environment.json) and [artifact manifest](evidence/claim-1/artifact_manifest.json)
- [Protected judged-revision manifest](evidence/protected-judged-revision-manifest.sha256)
- [Exact historical text snapshot](historical/judged-7f2c76f4/pages/index.md)

## Verdict and limitation

**VERIFIED** at the stated continuous and discrete paper settings. This is direct, reproducible finite-sample corroboration of the theorem's predicted normalization, variance, coverage, and convergence trend. A finite Monte Carlo experiment is not a proof of the theorem's universal asymptotic quantifier; the paper's proof remains necessary for that universal statement.
