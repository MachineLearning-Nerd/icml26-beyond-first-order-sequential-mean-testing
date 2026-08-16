# Claim-to-evidence ledger

This ledger separates what the repository actually computes from what the paper proves. “Verified under a finite contract” means that the locked finite experiment, independent checker, and negative control passed. It does not replace a proof of the paper’s universal asymptotic statement.

| Claim | Paper target | Repository status | How the result is produced | Decisive evidence |
| --- | --- | --- | --- | --- |
| 1 | Theorem 4.2, fixed-sample KL_inf CLT | VERIFIED, finite contract | The implementation computes the population dual reference and empirical optimizer, generates fixed-sample replicates, then independently recomputes variance, KS distance, coverage, and centering. | space_candidate/evidence/claim-1/checker_output.json; the deliberately discrete n=50 control fails. |
| 2 | Theorem 4.4, stopping-time CLT as alpha decreases | VERIFIED, finite contract | Exact Bernoulli KL_inf is evaluated at every time, first-hit paths are generated under the growing boundary, and an independent checker tests crossing inequalities, variance, KS distance, coverage, and centering across the preregistered grid. | space_candidate/evidence/claim-2/checker_output.json; finite-large-b and wrong-fixed-sample controls fail. |
| 3 | Equations (5)-(6) and Lemma A.8 | VERIFIED, finite contract | The pathwise T1+T2 decomposition is evaluated, the optimizer remainder is scaled, every integer prefix in the declared Anscombe windows is checked, and seed replay is independently verified. | space_candidate/evidence/claim-3/checker_output.json; wrong-dual and over-wide-window controls fail. |
| 4 | Proposition 4.5, single-run confidence interval | FALSIFIED literally; formula supported | Nested stopped paths produce the plug-in interval. The checker compares deterministic-target coverage with the literal random-stopping-time target and preserves the source equations. | space_candidate/evidence/claim-4/checker_output.json; literal self-target coverage is 1.0, while deterministic-target coverage is 0.9513/0.5010. |
| 5 | Section 5 synthetic and crop-yield agreement | VERIFIED, declared contract | Synthetic checks are followed by bootstrap stopped paths from a pinned public DSSAT maize HWAM pool; source hashes, first-hit inequalities, scalar-solver replay, and aggregate metrics are independently checked. | space_candidate/evidence/claim-5/checker_output.json; wrong-variance and negative-sentinel controls fail. |

## Evidence production chain

~~~text
paper source and theorem anchor
  -> claim contract and assumption audit
  -> reproduction/claimN.py with locked configuration and seeds
  -> raw paths or replicates plus environment record
  -> independent checker and deliberately failing control
  -> candidate verifier and current claim page
  -> release visibility matrix and technical report
~~~

The canonical entrypoint is README.md, followed by space_candidate/README.md, release-report, and the five current-claim-N pages. Each page exposes the implementation, raw data or manifest, checker, control, source audit, command, environment, and verdict.

## Scope boundary

The historical live evaluator score is 3/10. The 6-10 and 10/10 values in the release report are forecasts, not judge results. The finite checks support reproducibility and expose a literal target mismatch; they do not establish the paper’s universal quantifiers. Claim 5 also cannot match the authors’ hidden crop-yield panel because the exact author data and preprocessing were not released.
