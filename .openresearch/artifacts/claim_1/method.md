# Claim 1 method

The population Beta reference is computed by independent quadrature and a bracketed root of the paper's dual score. Bernoulli uses its closed-form binary-KL oracle. Empirical Beta `KL_inf` values use a safeguarded vectorized Newton solve of the one-dimensional dual problem. The checker reads only raw standardized replicates and recomputes moments, coverage, and KS distance with the Python standard library.

Seeds, sample sizes, thresholds, and compute estimates are committed in `reproduction/config.json`. All scientific computation runs through the fixed OpenResearch command on HF `cpu-upgrade`.
