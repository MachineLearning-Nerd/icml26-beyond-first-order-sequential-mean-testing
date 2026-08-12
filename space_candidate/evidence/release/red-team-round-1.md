# Evaluator-blind red team — round 1

Candidate Git revision: `470cbd5513750b246ed4d787380068694f576567`. Fresh clone: `release/publication-gates`. The reviewer started at `README.md`, received no storage hints, and used only the candidate plus the release rubric.

## Findings

The canonical entrypoint immediately exposed `#/release-report`. From there the reviewer located the current verifier, contract, source audit, inline metrics, raw records, checker, control, limitations, environment, and current page for every claim. No claim evidence link traversed from a current page was missing.

Provisional reviewer scoring from this artifact alone:

- Claim 1: 2/2, direct finite evidence and preserved accepted result.
- Claim 2: 2/2, direct large-`b` stopping-time calibration and first-hit checks.
- Claim 3: 1–2/2, exact finite mechanism and Anscombe check; universal proof quantifiers remain outside finite evidence.
- Claim 4: 0–2/2, rigorous literal source-target falsification; residual risk is whether the evaluator scores the supplied wording or silently substitutes the proposition's deterministic target.
- Claim 5: 1–2/2, exact synthetic protocols and public DSSAT same-domain reproduction; undisclosed author data prevents exact Figure 5 equality.

Release blockers found: `evidence/release/red-team-round-2.md`, the publication allowlist, and its SHA-256 manifest did not yet exist; those absent release products were correctly treated as missing. The release verifier and command ledger were present but not linked directly from the canonical page. The notebook had not yet been validated by the pinned HF environment. These are presentation/release-gate gaps, not new scientific conclusions.

## Files opened

- `README.md`
- `pages/release-report/page.md`
- `reports/sequential-mean-testing/images/headline.svg`
- `reports/sequential-mean-testing/report.md`
- `notebooks/sequential_mean_testing.py`
- `pages/current-claim-1/page.md`
- `evidence/claim-1/claim_contract.json`
- `evidence/claim-1/source_audit.md`
- `evidence/claim-1/method.md`
- `evidence/claim-1/limitations.md`
- `evidence/claim-1/verify_claim.py`
- `reproduction/klinf.py`
- `reproduction/claim1.py`
- `reproduction/config.json`
- `pyproject.toml`
- `uv.lock`
- `evidence/claim-1/fixed_clt_metrics.csv`
- `evidence/claim-1/fixed_clt_replicates.csv`
- `evidence/claim-1/verifier_output.json`
- `evidence/claim-1/checker_output.json`
- `evidence/claim-1/negative_control.json`
- `evidence/claim-1/environment.json`
- `evidence/claim-1/artifact_manifest.json`
- `evidence/protected-judged-revision-manifest.sha256`
- `historical/judged-7f2c76f4/pages/index.md`
- `evidence/claim-1/independent_checker.py`
- `pages/current-claim-2/page.md`
- `evidence/claim-2/claim_contract.json`
- `evidence/claim-2/source_audit.md`
- `evidence/claim-2/method.md`
- `evidence/claim-2/limitations.md`
- `evidence/claim-2/verify_claim.py`
- `evidence/claim-2/independent_checker.py`
- `reproduction/claim2.py`
- `evidence/claim-2/stopping_clt_metrics.csv`
- `evidence/claim-2/raw_parts_manifest.json`
- `evidence/claim-2/stopping_paths-part-00.csv`
- `evidence/claim-2/stopping_paths-part-01.csv`
- `evidence/claim-2/stopping_paths-part-02.csv`
- `evidence/claim-2/stopping_paths-part-03.csv`
- `evidence/claim-2/stopping_paths-part-04.csv`
- `evidence/claim-2/stopping_paths-part-05.csv`
- `evidence/claim-2/stopping_paths-part-06.csv`
- `evidence/claim-2/stopping_paths-part-07.csv`
- `evidence/claim-2/verifier_output.json`
- `evidence/claim-2/checker_output.json`
- `evidence/claim-2/negative_controls.json`
- `evidence/claim-2/environment.json`
- `evidence/claim-2/run_diagnostics.json`
- `evidence/claim-2/hf_artifact_manifest.json`
- `pages/current-claim-3/page.md`
- `evidence/claim-3/claim_contract.json`
- `evidence/claim-3/source_audit.md`
- `evidence/claim-3/method.md`
- `evidence/claim-3/limitations.md`
- `evidence/claim-3/verify_claim.py`
- `evidence/claim-3/independent_checker.py`
- `evidence/claim-3/hf_verify_claim.py`
- `evidence/claim-3/hf_independent_checker.py`
- `reproduction/claim3.py`
- `evidence/claim-3/decomposition_metrics.csv`
- `evidence/claim-3/anscombe_metrics.csv`
- `evidence/claim-3/raw_parts_manifest.json`
- `evidence/claim-3/claim3-raw-part-00.csv`
- `evidence/claim-3/claim3-raw-part-01.csv`
- `evidence/claim-3/claim3-raw-part-02.csv`
- `evidence/claim-3/claim3-raw-part-03.csv`
- `evidence/claim-3/claim3-raw-part-04.csv`
- `evidence/claim-3/claim3-raw-part-05.csv`
- `evidence/claim-3/claim3-raw-part-06.csv`
- `evidence/claim-3/verifier_output.json`
- `evidence/claim-3/checker_output.json`
- `evidence/claim-3/negative_controls.json`
- `evidence/claim-3/environment.json`
- `evidence/claim-3/hf_artifact_manifest.json`
- `pages/current-claim-4/page.md`
- `evidence/claim-4/claim_contract.json`
- `evidence/claim-4/source_audit.md`
- `evidence/claim-4/method.md`
- `evidence/claim-4/limitations.md`
- `evidence/claim-4/verify_claim.py`
- `evidence/claim-4/independent_checker.py`
- `evidence/claim-4/hf_verify_claim.py`
- `evidence/claim-4/hf_independent_checker.py`
- `reproduction/claim4.py`
- `evidence/claim-4/single_run_ci_metrics.csv`
- `evidence/claim-4/theory.json`
- `evidence/claim-4/raw_parts_manifest.json`
- `evidence/claim-4/single-run-ci-paths-part-00.csv`
- `evidence/claim-4/single-run-ci-paths-part-01.csv`
- `evidence/claim-4/single-run-ci-paths-part-02.csv`
- `evidence/claim-4/single-run-ci-paths-part-03.csv`
- `evidence/claim-4/verifier_output.json`
- `evidence/claim-4/checker_output.json`
- `evidence/claim-4/negative_controls.json`
- `evidence/claim-4/environment.json`
- `evidence/claim-4/hf_artifact_manifest.json`
- `pages/current-claim-5/page.md`
- `evidence/claim-5/dssat_public_maize_pool.csv`
- `evidence/claim-5/dssat_source_manifest.json`
- `reproduction/data/dssat_maize/BRPI0202.MZA`
- `evidence/claim-5/dssat_theory.json`
- `evidence/claim-5/claim_contract.json`
- `evidence/claim-5/source_audit.md`
- `evidence/claim-5/method.md`
- `evidence/claim-5/limitations.md`
- `evidence/claim-5/verify_claim.py`
- `evidence/claim-5/independent_checker.py`
- `reproduction/claim5.py`
- `evidence/claim-5/hf_verify_claim.py`
- `evidence/claim-5/hf_independent_checker.py`
- `evidence/claim-5/accepted_run_manifest.json`
- `evidence/claim-5/dssat_bootstrap_metrics.csv`
- `evidence/claim-5/dssat_bootstrap_paths.csv`
- `evidence/claim-5/synthetic_crosscheck.json`
- `evidence/claim-5/verifier_output.json`
- `evidence/claim-5/checker_output.json`
- `evidence/claim-5/negative_controls.json`
- `evidence/claim-5/environment.json`
- `evidence/claim-5/artifact_manifest.json`
- `evidence/release/visibility_matrix.md`
