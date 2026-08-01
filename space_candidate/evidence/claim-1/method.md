# Claim 1 method

The population Beta reference is computed by independent quadrature and a bracketed root of the paper's dual score. Bernoulli uses its closed-form binary-KL oracle. Empirical Beta `KL_inf` values use a safeguarded vectorized Newton solve of the one-dimensional dual problem, accepting either a small score residual or a narrow root bracket and falling back to the bracket midpoint after 60 iterations. The checker reads only raw standardized replicates and recomputes moments, coverage, and KS distance with the Python standard library.

Seeds, sample sizes, thresholds, and compute estimates are committed in `reproduction/config.json`. All scientific computation runs through the fixed OpenResearch command on HF `cpu-upgrade` in the immutable image `ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040`.
