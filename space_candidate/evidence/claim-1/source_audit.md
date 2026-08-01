# Claim 1 source audit

- Source: https://ar5iv.labs.arxiv.org/html/2606.04520
- Retrieved: 2026-08-01 with an explicit `OpenResearch-Reproduction/1.0` User-Agent.
- SHA-256: `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`
- Theorem anchor: `#S4.Thmtheorem2`; assumption anchor: `#S4.Thmtheorem1`.
- Section 5 paper settings: `m0=0.7`, `q=Beta(3,2)` and `q=Bernoulli(0.6)`, 5,000 independent replicates.

Assumption 4.1 is satisfied. Bernoulli has endpoint atoms, making the exceptional equality case vacuous. For Beta(3,2) with `m0=0.7`, the exceptional equality does not hold: `(1-m0)(a+b-1)/(b-1)=1.2`, not 1.
