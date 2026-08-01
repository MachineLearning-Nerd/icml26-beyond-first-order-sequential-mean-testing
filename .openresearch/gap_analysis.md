# Claim-by-claim gap analysis

Compared artifacts: protected `DineshAI/HMyCBL2yMV@7f2c76f4...` and public reference `MarxistLeninist/HMyCBL2yMV@4a98fe4...`. The reference is comparative context only; all checks below will be independently implemented and rerun.

| Claim | Protected DineshAI state | Sound reference pattern | Required independent upgrade |
| --- | --- | --- | --- |
| 1 | Full judge credit, but verifier imports absent `core.py`; no raw data/checker/control. | Dedicated page, exact dual solver, continuous/discrete settings, small-n disagreement. | Preserve the conclusion; rerun exact paper distributions with raw replicates, independent checker, strict gate, and failing small-n control. |
| 2 | Variance ratio 1.276 and 23% centering bias at the smallest alpha. | Separate growing and constant boundaries; sweep `b=log(1/alpha)` far beyond the paper's plotted alpha. | Use a precommitted non-circular b-grid, 10,000 paths, confidence intervals, exact crossing checks, and a finite-b control that must fail. |
| 3 | Only a numerical dual-term check; no implementation or Anscombe audit. | Exact decomposition identity, local-oscillation diagnostic, proof audit of the omitted boundary term. | Check algebraic proof obligations independently, exact decomposition from raw paths, local oscillations over n/delta, and a deliberately invalid control. |
| 4 | Below-nominal coverage caused by testing the wrong target; trivial `95%>50%` gate. | Distinguish the proposition's actual estimand `1/KL_inf` from a future random stopping time. | Verify actual-estimand coverage and variance consistency, then test the literal future-stopping-time interpretation; require the analytically predicted ~83.4% independent-path coverage rather than 95%. |
| 5 | Synthetic normality tests at one scale; crop-yield arm absent. | Pinned official DSSAT maize observations, disclosed normalization, paper-matched bootstrap, alpha trend. | Independently fetch the pinned primary dataset, preserve source hashes, rerun exact synthetic settings and a disclosed same-domain DSSAT protocol, and label the unreleased author pool limitation. |

The reference still lacks several gates required here: per-claim executable nonzero verifiers, negative controls, HF allocation/runtime evidence, a protected-old-file subset proof, and evaluator-blind traversal records. These will be added rather than inferred from its 10/10 score.
