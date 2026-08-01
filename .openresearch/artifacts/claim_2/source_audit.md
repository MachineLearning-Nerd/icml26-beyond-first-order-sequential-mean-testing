# Claim 2 source audit

- Source: https://ar5iv.labs.arxiv.org/html/2606.04520, retrieved 2026-08-01 with explicit User-Agent, SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.
- Exact theorem: `#S4.Thmtheorem4`; stopping rule and boundary: equation (3), paragraph `S3.SS3.p2`; paper experiment: `S5.SS0.SSS0.Px2`.
- Quantifiers: fixed `q ∈ Q_bd`, fixed `m0 ∈ (0,1)`, Assumption 4.1, and `alpha ↓ 0`.
- Exact stopping time: first `n` such that `n KL_inf(qhat_n,m0) ≥ 1 + log(2(1+n)/alpha)`.
- Paper setting: `q=Bernoulli(0.6)`, `m0=0.2`, 5,000 paths at `alpha=1e-4,1e-8`; this reproduction increases to 10,000 paths and a preregistered asymptotic grid.

Bernoulli(0.6) is supported on `[0,1]`, differs from `m0`, and has endpoint atoms, so the exceptional equality in Assumption 4.1 is vacuous.
