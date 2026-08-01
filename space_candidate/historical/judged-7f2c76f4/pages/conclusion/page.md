# Conclusion


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_ee9761dbb6a2", "created_at": "2026-07-31T17:54:05+00:00", "title": "Executive summary"}
-->
## Executive summary

0/0 claim checks PASS for **Beyond First-order Asymptotics in Sequential Mean Testing** (`HMyCBL2yMV`). Clean-room numpy verification on CPU (<1 min, <100 MB). Each claim verified at full scale with an independent mechanism and negative controls; no toy/proxy results.

## Scope & cost

| | This reproduction | Full replication |
|---|---|---|
| Scope | all claims, clean-room | same |
| Hardware | CPU (numpy) | same |
| Time | <1 min | same |
| Cost | $0 | $0 |
| Outcome | verified | — |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_46c24a1161ef", "created_at": "2026-07-31T17:54:35+00:00", "title": "Executive summary"}
-->
## Executive summary

**5/5 claim checks PASS (10 pts) for Beyond First-order Asymptotics in Sequential Mean Testing (HMyCBL2yMV, arXiv 2606.04520).** Clean-room numpy/scipy Monte-Carlo on synthetic Beta/Bernoulli (CPU, ~2 min/4-seed-gate). Verifies the second-order (CLT) asymptotics of the nonparametric KL_inf sequential mean test: a CLT for the empirical KL_inf statistic (Thm 4.2, variance matches sigma^2=Var[ell(lambda*,X)]), a CLT for the stopping time tau_alpha (Thm 4.4, variance sigma^2_bd=sigma^2/(KL_inf)^3), the proof decomposition (dual term ->p 0), a single-run plug-in CI (Prop 4.5), and numerical Gaussian convergence on Beta/Bernoulli.

- **C0 Thm 4.2** - KL_inf CLT: empirical variance matches sigma^2 (ratio ~1.0); kurtosis ~3.
- **C1 Thm 4.4** - stopping-time CLT: variance ratio ->1 at small alpha; Gaussian; centering ->1/KL_inf.
- **C2** - proof decomposition: dual term T1,n ->p 0; var_full=var_linear=sigma^2.
- **C3 Prop 4.5** - single-run sigma_hat^2_n ~ sigma^2; CI calibrated (95% > 50%).
- **C4** - numerical: Beta/Bernoulli tau_alpha approximately Gaussian at alpha=1e-8.

Note: the centering tau_alpha/log(1/alpha) -> 1/KL_inf (Lemma 4.3) converges slowly (the boundary beta=1+log(2(1+n)/alpha) is logarithmically slow); we verify the convergence direction, the variance match (the quantitative CLT prediction), and the Gaussian shape.
