# Claims

> **Historical rejected baseline** — preserved from judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`. Its conclusions are superseded by the current verification pages.


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_001cc6bd60bd", "created_at": "2026-07-31T17:51:28+00:00", "title": "Claims to reproduce"}
-->
## Claims to reproduce

1. Theorem 4.2 establishes a central limit theorem for the empirical KL_inf statistic, showing sqrt(n)(KL_inf(q_hat_n, m_o) - KL_inf(q, m_o)) converges in distribution to N(0, sigma^2(q, m_o)) (Theorem 4.2).
2. Theorem 4.4 extends this result to the stopping time tau_alpha, proving sqrt(log(1/alpha))(tau_alpha/log(1/alpha) - 1/KL_inf(q,m_o)) converges to a Gaussian limit N(0, sigma^2_bd(q,m_o)) as alpha to 0 (Theorem 4.4).
3. The proof decomposes the normalized KL_inf statistic into a term from the dual optimization (shown to vanish in probability) and a standard empirical-mean term that converges to Gaussian, combined with verification of Anscombe's condition to transfer the CLT to the stopping time (Section 4).
4. Proposition 4.5 constructs asymptotically valid confidence intervals for the stopping time using only a single simulation run, without requiring multiple independent replicates (Proposition 4.5).
5. Numerical experiments on synthetic Beta and Bernoulli distributions and on real crop-yield data show empirical stopping-time distributions converging to the theoretical Gaussian limit, with stronger agreement at smaller significance levels alpha (Section 5).
