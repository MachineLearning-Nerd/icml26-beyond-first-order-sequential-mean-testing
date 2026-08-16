# Reproduction audit report

## Decision

PARTIAL_FINITE_CONTRACTS; CLAIM_4_LITERAL_TARGET_FALSIFIED; FORMULA_SUPPORTED

The repository supplies strong, independently checked finite evidence for Claims 1-3 and 5 under their declared contracts. Claim 4 is not accepted as literally worded: the interval centered on the observed normalized stopping time covers that same random quantity identically, while the displayed Proposition 4.5 formula targets the deterministic 1 / KL_inf(q,m0). The formula is supported for the tested Bernoulli instance.

## Claim outcomes

| Claim | Key result | Verdict |
| --- | --- | --- |
| 1 | At n=5000, Beta(3,2) variance ratio 1.0092839787, KS 0.0124165830, coverage 0.9530; Bernoulli(0.6) variance ratio 0.9956726648, KS 0.0184674774, coverage 0.9522. | Verified under finite contract. |
| 2 | At growing-boundary exp(-10000), variance ratio 0.9923198426, KS 0.0349276193, coverage 0.9477, standardized mean 0.0720391565; 160,000 paths and zero crossing failures. | Verified under finite contract. |
| 3 | 40,000 decomposition paths, 100,000 Anscombe paths, zero nested-window failures, exact seed replay, and full/T2 variance ratio 1.000127 in the accepted run. | Verified under finite contract. |
| 4 | Literal stopping-time self-coverage is 1.0; deterministic-target coverage is 0.9513 at nominal 95% and 0.5010 at nominal 50%. | Literal claim falsified; displayed deterministic-target formula supported. |
| 5 | 10 source files hashed, 44 public pool rows, 9,000 raw paths, 9,000 first-hit checks, and three aggregate metric rows; at alpha 1e-4, KS 0.0890, variance ratio 0.9396, Gaussian mass 0.9693. | Verified under declared public-data contract. |

## What is and is not established

Established:

- The repository’s finite protocols execute from pinned source/configuration records.
- Independent checkers reproduce the decisive metrics.
- Negative controls fail where they are designed to fail.
- The release surface distinguishes current evidence from the historical rejected baseline.

Not established:

- A new proof of any universal asymptotic theorem.
- An exact numerical reproduction of the authors’ undisclosed crop-yield data.
- A new live evaluator score. The previous score remains 3/10; projected scores are forecasts only.

## Review path

Start at README.md, then read CLAIM_EVIDENCE.md and SOURCE_AUDIT.md. For executable evidence, follow space_candidate/README.md to release-report, inspect the five current claim pages, and run PYTHONDONTWRITEBYTECODE=1 python3 verify_final.py.
