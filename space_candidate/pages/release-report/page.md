# Current release report — claim-by-claim verification

- Previous live judged score: `3/10`
- Conservative projected score range after this proposed change: **6–10/10**
- Best-supported possible new score: **10/10 (forecast only; not a judge result)**

![Five claim contracts and outcomes](reports/sequential-mean-testing/images/headline.svg)

The current verification is cumulative and supersedes the pages labeled **Historical rejected baseline**. Read the [illustrated technical report](reports/sequential-mean-testing/report.md) or [tutorial notebook](notebooks/sequential_mean_testing.py), then open each canonical claim page below for executable evidence.

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 2 | 2 | HIGH | VERIFIED | Exact paper Beta/Bernoulli settings, 40,000 raw replicates, calibrated variance/KS/coverage, checker and failing control; finite evidence is not a universal proof. |
| 2 | 0 | 2 | HIGH | VERIFIED | Exact growing stopping rule, independent `b` sweep to 10,000, 160,000 raw paths, first-hit replay, calibrated variance/KS/coverage; asymptotic evidence is finite. |
| 3 | 1 | 2 | MEDIUM | VERIFIED | Exact pathwise decomposition and every integer prefix in declared Anscombe windows, 140,000 raw records; the universal theorem quantifiers still rely on the paper's proof. |
| 4 | 0 | 2 | HIGH | FALSIFIED | Exact source equations show the supplied random-stopping-time wording is false: its own center has coverage one. The proposition's actual deterministic target is independently supported; evaluator may reject the supplied-claim/source distinction. |
| 5 | 0 | 2 | MEDIUM | VERIFIED | Exact synthetic protocols and decreasing-alpha trend plus a 3,000-path paper-protocol crop bootstrap on pinned official public DSSAT data; the authors' undisclosed Figure 5 pool prevents an exact panel match. |

Current total score: **3/10**. Conservative projected total: **6–10/10**. Best-supported possible total: **10/10, forecast only**. Claims 2–5 changed materially since the previous judge result. No claim is BLOCKED under its declared contract; Claim 3 remains finite rather than proof-complete, and Claim 5 has the disclosed author-data limitation.

## Evaluator-visible evidence matrix

Every link in this table is reachable from this canonical entrypoint. “Inline” means the page itself reports the decisive numbers rather than requiring a download.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Current Claim 1](#/current-claim-1) | [implementation](reproduction/claim1.py), [verifier](evidence/claim-1/verify_claim.py) | variance, KS, coverage, center | [40,000 rows](evidence/claim-1/fixed_clt_replicates.csv) | [source](evidence/claim-1/independent_checker.py), [output](evidence/claim-1/checker_output.json) | [output](evidence/claim-1/negative_control.json) | [contract](evidence/claim-1/claim_contract.json), [source audit](evidence/claim-1/source_audit.md) | VERIFIED |
| 2 | [Current Claim 2](#/current-claim-2) | [implementation](reproduction/claim2.py), [verifier](evidence/claim-2/verify_claim.py) | `b` sweep, variance interval, KS, coverage | [manifest and eight parts](evidence/claim-2/raw_parts_manifest.json) | [source](evidence/claim-2/independent_checker.py), [output](evidence/claim-2/checker_output.json) | [output](evidence/claim-2/negative_controls.json) | [contract](evidence/claim-2/claim_contract.json), [source audit](evidence/claim-2/source_audit.md) | VERIFIED |
| 3 | [Current Claim 3](#/current-claim-3) | [implementation](reproduction/claim3.py), [verifier](evidence/claim-3/verify_claim.py) | decomposition and Anscombe tables | [manifest and seven parts](evidence/claim-3/raw_parts_manifest.json) | [source](evidence/claim-3/independent_checker.py), [output](evidence/claim-3/checker_output.json) | [output](evidence/claim-3/negative_controls.json) | [contract](evidence/claim-3/claim_contract.json), [source audit](evidence/claim-3/source_audit.md) | VERIFIED |
| 4 | [Current Claim 4](#/current-claim-4) | [implementation](reproduction/claim4.py), [verifier](evidence/claim-4/verify_claim.py) | source target, plug-in error, 95%/50% coverage | [manifest and four parts](evidence/claim-4/raw_parts_manifest.json) | [source](evidence/claim-4/independent_checker.py), [output](evidence/claim-4/checker_output.json) | [three outputs](evidence/claim-4/negative_controls.json) | [contract](evidence/claim-4/claim_contract.json), [source audit](evidence/claim-4/source_audit.md) | FALSIFIED literally |
| 5 | [Current Claim 5](#/current-claim-5) | [implementation](reproduction/claim5.py), [verifier](evidence/claim-5/verify_claim.py) | synthetic trend and three DSSAT alpha rows | [9,000 paths](evidence/claim-5/dssat_bootstrap_paths.csv), [pool](evidence/claim-5/dssat_public_maize_pool.csv) | [source](evidence/claim-5/independent_checker.py), [output](evidence/claim-5/checker_output.json) | [output](evidence/claim-5/negative_controls.json) | [contract](evidence/claim-5/claim_contract.json), [source audit](evidence/claim-5/source_audit.md) | VERIFIED |

Every row also exposes method, limitations, fixed command, lockfile, seeds, Git SHA, CPU/runtime, and verifier console on its canonical page. Release evidence: [visibility details](evidence/release/visibility_matrix.md), [blind review round 1](evidence/release/red-team-round-1.md), [blind review round 2](evidence/release/red-team-round-2.md), [release verifier](evidence/release/verify_release.py), [command ledger](evidence/release/command_ledger.md), [text upload allowlist](evidence/release/publication_allowlist.txt), and [SHA-256 upload manifest](evidence/release/publication_manifest.sha256).

## Current regression and compute

The accepted cumulative HF run is `f62c024e-5774-4715-b713-151f3bcc9a68` at Git commit `c52042c`. It ran the unchanged command:

```bash
uv sync --frozen && .venv/bin/python -m reproduction.run
```

All five scientific verifiers, all five independent checkers, all controls, all five candidate verifiers, and the Space's own fixed command exited zero. The job used `cpu-upgrade`, a pinned CPU-only image, two estimated useful cores, 64 observed affinity CPUs, no GPU, 300.206 seconds of cumulative plus standalone scientific runtime, and 5m28s job duration. At the current official `cpu-upgrade` rate of `$0.0005/min`, that accepted job is approximately `$0.003` when rounded to six billed minutes; the invoice remains authoritative.

## Release action

After every final gate exits zero, the exact action is: upload only the SHA-256-manifested text allowlist to the existing `DineshAI/HMyCBL2yMV` Space using one Hugging Face API commit; download that exact revision and repeat hash/traversal checks; then mirror the exact published text paths to GitHub `main` and confirm the remote SHA. No second Space and no GPU will be used. Publication does not imply a score change; the paper will be marked awaiting judge.
