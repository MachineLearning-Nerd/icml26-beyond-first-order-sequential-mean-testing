# Claim 5 limitations and deviations

- The authors do not release the exact crop-yield pool, normalization, code, or seed. The real-data arm uses a fully disclosed official public DSSAT same-domain pool and cannot establish equality with Figure 5's hidden inputs.
- The public pool contains 44 observations from eight experiment files. Bootstrap resampling provides 3,000 paths but does not create 3,000 independent physical field trials.
- The additional alpha levels `1e-2` and `1e-3` test direction; the paper reports only `1e-4` for DSSAT.
- Finite simulation corroborates the displayed Gaussian approximation; it is not a proof of an asymptotic theorem over every bounded distribution.
- The fixed horizon 5,000 is not theorem-derived. The run exits nonzero if any path remains unresolved.
