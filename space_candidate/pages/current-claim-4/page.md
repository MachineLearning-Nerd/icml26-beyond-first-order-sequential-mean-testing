# Claim 4 — FALSIFIED as literally supplied

This is the current Claim 4 result. It supersedes the **Historical rejected baseline** verifier at judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`, whose below-nominal coverage came from finite significance levels and whose only calibration check was the vacuous ordering “95% > 50%.”

## Exact source-target audit

The supplied claim says Proposition 4.5 constructs an asymptotically valid “confidence interval for the stopping time” from one run. The proposition does define, from the same stopped path,

`σ̂ₙ² = n⁻¹ Σᵢ(ℓ(λₙ*,Xᵢ)−KL_inf(q̂ₙ,m₀))²`,

`v̂α = σ̂²_{τα}/KL_inf(q̂_{τα},m₀)³`, and

`Iα(γ) = [τα/log(1/α) ± z_{1−γ/2} √(v̂α/log(1/α))]`.

But its exact coverage event is

`lim_{α↓0} P(1/KL_inf(q,m₀) ∈ Iα(γ)) = 1−γ`.

The target is the deterministic normalized center `1/KL_inf(q,m₀)`, not the random stopping time. If `Iα` is instead interpreted as an interval for its own observed `τα/log(1/α)`, it has coverage one identically because that value is the interval center. This is 1.0 at both the nominal 95% and 50% levels—not `1−γ`. Multiplying through by `log(1/alpha)` gives an interval for the deterministic first-order center `log(1/alpha)/KL_inf`; it is not a prediction interval for a future random stopping time.

Sources: arXiv 2606.04520, [Proposition 4.5](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Thmtheorem5), [plug-in variance](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Ex39), [interval](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Ex41), [coverage event](https://ar5iv.labs.arxiv.org/html/2606.04520#S4.Ex42), and [proof](https://ar5iv.labs.arxiv.org/html/2606.04520#A1.SS4). The HTML was retrieved 2026-08-02 with an explicit User-Agent; SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.

## The actual proposition also passes

The direct contract fixes `q=Bernoulli(0.6)`, `m₀=0.2`, a bounded, nondegenerate law whose endpoint atoms satisfy Assumption 4.1's boundary clause. Ten thousand deterministic paths share the same random stream across four preselected `b=log(1/alpha)` values. Each interval uses only the observations on its own path through its own stopping time. The 10,000 paths are independent replicates only for evaluating coverage, not for constructing an individual interval.

| b | Mean τ/b | Relative center error | Mean v̂/σ²bd | Median v̂/σ²bd | 95% coverage | 50% coverage |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 147.365 | 2.75756 | 0.05314 | 1.00950 | 0.98490 | 0.9406 | 0.4618 |
| 589.462 | 2.65746 | 0.01491 | 1.00108 | 0.99347 | 0.9483 | 0.4845 |
| 2,357.847 | 2.63113 | 0.00485 | 1.00144 | 0.99967 | 0.9469 | 0.4932 |
| 10,000 | 2.62191 | 0.00133 | **1.00043** | **1.00016** | **0.9513** | **0.5010** |

At `b=10000`, the 95% coverage Wilson interval is `[0.94691, 0.95535]` and contains 0.95; the 50% Wilson interval is `[0.49120, 0.51080]` and contains 0.50. The target is `1/KL_inf=2.618428`. Median absolute relative plug-in error decreases from 0.15875 to 0.02079, and its 90th percentile decreases from 0.39996 to 0.05069. Both coverage errors improve across the declared endpoints.

The independent checker replayed all **40,000** raw stopped records from seed `260604241`, verified every first-hit inequality, recomputed every dual optimizer, variance estimate, interval endpoint, and coverage indicator, compared regenerated output, checked part hashes, and found zero nested-stopping violations.

All three controls fail for their intended reasons:

- Applying the asymptotic gate at finite `b=147.365` fails 95% coverage, 50% coverage, and centering.
- Using `KL_inf²` rather than the proposition's `KL_inf³` gives only 0.7770 coverage at the nominal 95% level.
- Treating the interval as covering its own stopping time gives tautological coverage one at both levels, falsifying the literal wording.

## Reproduction and downloadable evidence

Fixed command:

```bash
uv sync --frozen && .venv/bin/python -m reproduction.run
```

The accepted HF run used Git SHA `33cd700fa4dbe3bc0188dc090e36b08a2e01c6de`, Python 3.12.11, seed `260604241`, Hugging Face `cpu-upgrade`, and the pinned CPU-only image `ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040`. Estimated need was 2 cores; observed affinity was 64 CPUs. Claim 4 runtime was 43.852 seconds, cumulative fixed-command runtime was 145.455 seconds, and maximum RSS was 1,101,868 KiB. No GPU was allowed.

- [Claim and falsification contract](evidence/claim-4/claim_contract.json)
- [Source and assumption audit](evidence/claim-4/source_audit.md)
- [Method](evidence/claim-4/method.md) and [limitations](evidence/claim-4/limitations.md)
- [Current nonzero-exit verifier](evidence/claim-4/verify_claim.py) and [independent checker](evidence/claim-4/independent_checker.py)
- [HF verifier source](evidence/claim-4/hf_verify_claim.py), [HF checker source](evidence/claim-4/hf_independent_checker.py), and [core implementation](reproduction/claim4.py)
- [Locked configuration](reproduction/config.json), [pinned environment](pyproject.toml), and [complete lockfile](uv.lock)
- [All aggregate metrics](evidence/claim-4/single_run_ci_metrics.csv), [theory](evidence/claim-4/theory.json), and [raw-parts hash manifest](evidence/claim-4/raw_parts_manifest.json)
- Raw stopped records [1](evidence/claim-4/single-run-ci-paths-part-00.csv), [2](evidence/claim-4/single-run-ci-paths-part-01.csv), [3](evidence/claim-4/single-run-ci-paths-part-02.csv), [4](evidence/claim-4/single-run-ci-paths-part-03.csv)
- [HF verifier output](evidence/claim-4/verifier_output.json), [independent checker output](evidence/claim-4/checker_output.json), and [negative-control output](evidence/claim-4/negative_controls.json)
- [Runtime/CPU/Git/seed record](evidence/claim-4/environment.json), [HF artifact manifest](evidence/claim-4/hf_artifact_manifest.json), and [protected judged-revision manifest](evidence/protected-judged-revision-manifest.sha256)

## Verdict and limitation

**FALSIFIED** as literally supplied: Proposition 4.5 does not provide nominal coverage for a random stopping time. The actual displayed `1/KL_inf` proposition is strongly supported in the exact same-path construction at a nondegenerate, assumption-satisfying Bernoulli law. The numerical arm is finite evidence, not a theorem-wide proof over every law in `Q^bd`.
