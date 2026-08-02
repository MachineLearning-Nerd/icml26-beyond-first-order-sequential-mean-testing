# Claim 4 method

Simulate 10,000 deterministic, nested Bernoulli(0.6) paths. On each path, record the first crossing of the exact growing boundary at four independently preselected `b=log(1/alpha)` values. The same underlying path is retained across all four levels, which directly audits convergence along decreasing alpha.

At each path's stopping time, compute `p_hat`, the exact Bernoulli `KL_inf^-`, the empirical dual optimizer, equation (39)'s variance, and `v_hat` with the required cubic denominator. Construct 95% and 50% intervals solely from that stopped path. Independent paths are used only to estimate coverage, with Wilson uncertainty intervals.

The independent checker replays the seeded random paths, checks first-hit inequalities, recomputes every estimator and interval from stopped sufficient statistics, checks nested stopping times, and compares all 40,000 raw records. The verifier exits nonzero unless the predeclared largest-scale and trend gates pass. Controls deliberately apply an asymptotic gate at the first scale and replace the cubic denominator by a square.

Fixed command: `uv sync --frozen && .venv/bin/python -m reproduction.run`.
