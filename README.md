# Beyond First-order Asymptotics in Sequential Mean Testing

Independent claim-by-claim reproduction and audit for:

> Vikas Deep and Shubhada Agrawal, “Beyond First-order Asymptotics in Sequential Mean Testing.”

Paper: [arXiv:2606.04520](https://arxiv.org/abs/2606.04520) · [HTML paper](https://arxiv.org/html/2606.04520) · [Open in Molab](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-beyond-first-order-sequential-mean-testing/blob/main/notebooks/sequential_mean_testing.py)

This is an independent reproduction/audit repository, not an author-maintained implementation. The repository contains the executable experiments, raw outputs, independent checkers, negative controls, source audits, release logbook, and a preserved historical judged baseline.

## Current status

The evidence is strong but scoped. Claims 1–3 and 5 are **verified under explicit finite contracts**; Claim 4 is **falsified as literally supplied** because the proposition’s interval targets the deterministic `1 / KL_inf(q,m0)`, not the observed random stopping time. The underlying Proposition 4.5 formula is supported for the tested Bernoulli law. None of the finite experiments replaces the paper’s universal asymptotic proofs.

| Claim | Paper target | Repository verdict | Decisive evidence |
| --- | --- | --- | --- |
| 1 | Theorem 4.2: fixed-sample `KL_inf` CLT | **VERIFIED, finite contract** | At `n=5000`, Beta(3,2) variance ratio `1.0093`, KS `0.0124`, coverage `0.9530`; Bernoulli(0.6) `0.9957`, `0.0185`, `0.9522`. |
| 2 | Theorem 4.4: stopping-time CLT as `alpha -> 0` | **VERIFIED, finite contract** | At `b=log(1/alpha)=10000`, variance ratio `0.9923`, KS `0.0349`, Gaussian mass `0.9477`, centering error `0.102%`. |
| 3 | Equations (5)–(6) and Lemma A.8: decomposition plus Anscombe transfer | **VERIFIED, finite contract** | At `n=50000`, optimizer-remainder/linear RMS `0.00444`, full/T2 variance ratio `1.000127`; full-prefix window checks pass. |
| 4 | Proposition 4.5: single-run confidence interval | **FALSIFIED literally; formula supported** | Self-target coverage is exactly `1`; deterministic-target coverage is `0.9513`/`0.5010` at nominal `95%`/`50%` in the largest-`b` run. |
| 5 | Section 5: synthetic and crop-yield numerical agreement | **VERIFIED, declared contract** | At `alpha=1e-4` on a pinned public DSSAT maize pool: KS `0.0890`, variance ratio `0.9396`, Gaussian mass `0.9693`. |

The previous live evaluator score remains `3/10`; the `6–10` and `10/10` numbers in the reports are forecasts, not judge results.

## Audit dossier

The repository-level audit is captured in the following files:

- [REPORT.md](REPORT.md) gives the concise decision and claim outcomes.
- [CLAIM_EVIDENCE.md](CLAIM_EVIDENCE.md) maps every claim to its implementation, checker, control, and limitation.
- [SOURCE_AUDIT.md](SOURCE_AUDIT.md) records paper identity, source hash, theorem anchors, and the disclosed DSSAT substitution.
- [BRANCH_AUDIT.md](BRANCH_AUDIT.md) records the final branch names, former checkpoint names, repository rename, and attribution policy.
- [CITATION.cff](CITATION.cff) and [AUTHOR_THANK_YOU.md](AUTHOR_THANK_YOU.md) provide citation metadata and an explicit thank-you note.
- [reproduction_verdicts.json](reproduction_verdicts.json) and [AUTONOMOUS_STATE.json](AUTONOMOUS_STATE.json) provide machine-readable claim outcomes and publication state.
- [EVIDENCE_MANIFEST.json](EVIDENCE_MANIFEST.json) and [verify_final.py](verify_final.py) provide the content and state verification contract.

Run PYTHONDONTWRITEBYTECODE=1 python3 verify_final.py from the repository root for the lightweight final audit. It rechecks the existing evidence and release gate; it does not rerun the full scientific experiments.

## What the paper does

The paper studies nonparametric sequential testing of a bounded distribution’s mean. For observations in `[0,1]`, it considers an `alpha`-correct power-one test of `H0: mean = m0` versus `H1: mean != m0`, using the information quantity `KL_inf` and the first crossing of a growing boundary.

Its main progression is:

1. establish a CLT for the empirical `KL_inf` statistic around its population value;
2. transfer that fluctuation through the stopping rule to obtain a Gaussian limit for the stopped sample size, centered at `1 / KL_inf` and scaled by `sqrt(log(1/alpha))`;
3. use the resulting variance estimate to construct a same-run interval for the deterministic first-order stopping-time constant; and
4. validate the approximation on synthetic distributions and crop-yield data.

The analysis is technically nontrivial because the empirical `KL_inf` statistic is a one-dimensional optimization rather than a fixed i.i.d. random walk. The reproduction therefore checks the optimizer, the algebraic decomposition, first-hit inequalities, full-prefix Anscombe windows, interval target, raw paths, and independent replays separately.

## How each claim becomes evidence

```text
paper source and exact anchor
        -> claim contract + assumption audit
        -> reproduction/claimN.py under one locked command
        -> raw CSV/JSON + environment and seed record
        -> independent checker + negative control
        -> nonzero-exit verifier and current claim page
        -> release visibility matrix and technical report
```

Every current claim page in `space_candidate/pages/current-claim-N/` links its contract, source audit, method, limitations, implementation, raw data, independent checker, control, verifier, and environment record. `reports/sequential-mean-testing/report.md` provides the human-readable synthesis.

| Claim | Production path | Evidence paths |
| --- | --- | --- |
| 1 | Population dual reference and empirical optimizer → standardized fixed-sample replicates → moments/coverage/KS checker | `reproduction/claim1.py`, `reproduction/klinf.py`, `space_candidate/evidence/claim-1/` |
| 2 | Exact Bernoulli `KL_inf` at every integer time → first crossing under growing and constant boundaries → stopped-path distribution checker | `reproduction/claim2.py`, `space_candidate/evidence/claim-2/` |
| 3 | Exact `T1 + T2` decomposition → optimizer remainder scaling → every integer prefix in relative windows → Anscombe checker | `reproduction/claim3.py`, `space_candidate/evidence/claim-3/` |
| 4 | Nested stopped paths → plug-in variance and interval → deterministic-target coverage plus literal self-target control | `reproduction/claim4.py`, `space_candidate/evidence/claim-4/` |
| 5 | Synthetic fixed/stopping checks → pinned public DSSAT pool → bootstrap stopped paths → source/hash/first-hit checker | `reproduction/claim5.py`, `reproduction/data/dssat_maize/`, `space_candidate/evidence/claim-5/` |

## Reproduce the cumulative evidence

The same locked command was used for every formal experiment and release regression:

```bash
uv sync --frozen
.venv/bin/python -m reproduction.run
```

The accepted cumulative run used Hugging Face `cpu-upgrade`, the pinned CPU-only image recorded in `reproduction/config.json`, an estimate of two useful cores, 64 CPUs visible in affinity, no GPU, and a 5m28s job duration. The repository also includes a tutorial notebook:

```bash
.venv/bin/marimo edit notebooks/sequential_mean_testing.py
.venv/bin/marimo run notebooks/sequential_mean_testing.py
```

No full local test suite is required to inspect the published evidence. Reviewers should start at `space_candidate/README.md`, then follow `#/release-report` to the current claim pages and `evidence/release/visibility_matrix.md`.

## Branch map

`main` is the cumulative publication surface. The former `orx/*` branches are preserved as cleanly named checkpoints below; each points to a commit already reachable from `main`, so renaming the references does not discard evidence.

| Clean branch | Former branch | Purpose and outcome |
| --- | --- | --- |
| `main` | `main` | Cumulative release surface; latest final-gate audit and report. |
| `audit/claim-1-frozen-judged-baseline` | `orx/frozen-judged-baseline-claim-1` | Hardened Claim 1 verifier and fixed-sample baseline; Claim 1 verified. |
| `audit/claim-2-stopping-time-clt` | `orx/claim-2-calibrated-stopping-time-clt` | Calibrated `b` sweep and stopping-time CLT; Claim 2 verified. |
| `audit/claim-3-decomposition-anscombe` | `orx/claim-3-decomposition-and-anscombe` | Exact decomposition and full-prefix Anscombe audit; Claim 3 verified under its finite contract. |
| `audit/claim-4-single-run-intervals` | `orx/claim-4-single-run-confidence-intervals` | Source-target distinction and interval coverage; Claim 4 falsified literally, actual formula supported. |
| `audit/claim-5-synthetic-dssat` | `orx/claim-5-synthetic-and-dssat-experiments` | Synthetic and crop-yield experiment implementation; Claim 5 verified under its declared contract. |
| `release/claim-1-evidence` | `orx/evaluator-visible-claim-1-evidence` | Evaluator-visible Claim 1 raw evidence and checker. |
| `release/claim-2-evidence` | `orx/evaluator-visible-claim-2-evidence` | Evaluator-visible Claim 2 raw evidence and checker. |
| `release/claim-3-evidence` | `orx/evaluator-visible-claim-3-evidence` | Evaluator-visible Claim 3 raw evidence and checker. |
| `release/claim-4-evidence` | `orx/evaluator-visible-claim-4-evidence` | Evaluator-visible Claim 4 falsification and formula evidence. |
| `release/claim-5-evidence` | `orx/evaluator-visible-claim-5-evidence` | Evaluator-visible Claim 5 synthetic/DSSAT evidence. |
| `release/publication-gates` | `orx/final-publication-gates` | Blind traversal, publication allowlist, and upload manifest. |
| `release/candidate-audit-report` | `orx/release-candidate-audit-and-report` | Release figures and candidate report generation. |
| `audit/claim-5-stopped-draw-evidence` | `orx/repair-claim-5-stopped-draw-evidence` | Corrected Claim 5 stopped-draw evidence. |
| `release/concise-evidence-stream` | `orx/repair-concise-release-evidence-stream` | Cumulative regression, candidate standalone run, and concise release payload. |
| `release/cumulative-navigation-repair` | `orx/repair-cumulative-current-page-navigation` | Corrected Claim 4 current-page navigation. |
| `release/final-gate-audits` | `orx/repair-final-release-gate-audits` | Latest final publication-gate audit; same tip as the current `main`. |

## Source, data, and limitations

The paper source was audited from [arXiv 2606.04520](https://arxiv.org/html/2606.04520). The exact DSSAT author pool, normalization, code, and seed behind the paper’s crop-yield figure were not published in the available record. Claim 5 therefore uses a pinned public pool from [`DSSAT/dssat-csm-data`](https://github.com/DSSAT/dssat-csm-data) at commit [`a4f95d3ef36f1358bdeb5db49d498d5db373ba7a`](https://github.com/DSSAT/dssat-csm-data/tree/a4f95d3ef36f1358bdeb5db49d498d5db373ba7a), with all nonnegative `HWAM` entries retained and checksummed.

Finite Monte Carlo agreement does not prove the paper’s universal quantifiers. The constant-boundary comparator is diagnostic only and does not inherit the growing boundary’s time-uniform guarantee. Historical rejected-evaluator files remain under `historical/judged-7f2c76f4/` and are labeled as historical rather than current evidence.

## Citation

```bibtex
@article{deep2026beyond,
  title         = {Beyond First-order Asymptotics in Sequential Mean Testing},
  author        = {Deep, Vikas and Agrawal, Shubhada},
  journal       = {arXiv preprint arXiv:2606.04520},
  year          = {2026},
  doi           = {10.48550/arXiv.2606.04520}
}
```

Please cite the paper using the version and venue information preferred by the authors when available.

## Thank you

Thank you to Vikas Deep and Shubhada Agrawal for making this work available and for developing a careful second-order analysis of `KL_inf`-based sequential mean tests. This repository is an independent reproduction and audit intended to make each claim, contract, evidence path, limitation, and correction easy to inspect.
