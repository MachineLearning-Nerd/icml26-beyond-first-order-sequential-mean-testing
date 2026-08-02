# EVAL

Verdict: **VERIFIED**

- Exact Section 5 synthetic cross-checks: {'claim_1': True, 'claim_2': True, 'constant_boundary_alpha_trend': True, 'growing_boundary_alpha_trend': True}.
- Official public DSSAT pool: 44 non-missing HWAM rows from eight of ten pinned Maize A-files.
- At alpha=1e-4: KS 0.0890, variance ratio 0.9396, Gaussian 95% coverage 0.9693, relative centering error -0.0436.
- Decreasing-alpha trends: {'ks_strictly_improves': True, 'centering_improves': True, 'variance_improves': True}.
- Negative controls: ['FAIL', 'FAIL'].
- Verifier/checker/candidate exits: 0/0/NA.
- HF cpu-upgrade runtime: 15.717s; actual affinity: 64 CPUs.
- Limitation: the paper does not identify its exact DSSAT pool or normalization; this run uses a fully disclosed official public same-domain pool.
