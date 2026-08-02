# Claim 4 limitations and deviations

- This is a direct verification at one nondegenerate law satisfying the paper's assumptions, not a proof uniformly over `Q^bd`.
- `alpha=exp(-10000)` cannot be represented as a floating-point number, so the exact log-scale `b=10000` is stored and used directly.
- Coverage is assessed with 10,000 paths; its Monte Carlo uncertainty is reported with Wilson intervals.
- The fixed safety horizon 500,000 is not theorem-derived. A run is invalid and exits nonzero if any path reaches it unresolved.
- The Bernoulli dual and `KL_inf^-` have closed forms, avoiding numerical optimization error. This is faithful for the tested law but does not exercise a generic continuous-law optimizer.
- The `FALSIFIED` verdict applies to the literal campaign wording “interval for the stopping time,” not to Proposition 4.5's displayed `1/KL_inf` coverage statement.
