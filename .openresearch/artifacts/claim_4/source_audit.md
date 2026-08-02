# Claim 4 source audit

Retrieved `https://ar5iv.labs.arxiv.org/html/2606.04520` with an explicit browser User-Agent on 2026-08-02. SHA-256: `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.

Proposition 4.5 (`S4.Thmtheorem5`) fixes `q in Q^bd` and `m0 in (0,1)`. Equation `S4.Ex39` defines

`sigma_hat_n^2 = n^-1 sum_i (ell(lambda_n*, X_i) - KL_inf(q_hat_n,m0))^2`.

It then defines `v_hat_alpha = sigma_hat_tau^2 / KL_inf(q_hat_tau,m0)^3`. Under Assumption 4.1, equation `S4.Ex40` states almost-sure convergence to `sigma_bd^2(q,m0)`. For every `gamma in (0,1)`, equations `S4.Ex41`–`S4.Ex42` state that

`[tau_alpha/log(1/alpha) +/- z_(1-gamma/2) sqrt(v_hat_alpha/log(1/alpha))]`

has limiting coverage `1-gamma` for `1/KL_inf(q,m0)` as `alpha` decreases to zero.

The paragraph after the proposition says the variance estimate is computed along the same run that produces `tau_alpha`; independent replicates are not needed to construct one interval. Repeated paths in this reproduction estimate coverage only. Appendix `A1.SS4` proves variance consistency using equation (22), Lemma A.5, continuous mapping, and `tau_alpha -> infinity`; the `m0 < mean(q)` direction uses the reflected `KL_inf^-` formula.

The tested Bernoulli(0.6), `m0=0.2` instance has bounded support, unequal mean, and endpoint atoms, so the boundary regularity clause in Assumption 4.1 is satisfied. The significance scales were inherited from the independent Claim 2 calibration and fixed before observing Claim 4 coverage.
