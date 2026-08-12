# Branch and attribution audit

Repository: `MachineLearning-Nerd/icml26-beyond-first-order-sequential-mean-testing`

Former repository name: `icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing`

## Branch policy

`main` remains the default cumulative publication surface. Every former `orx/*` branch is mapped to a descriptive `audit/*` or `release/*` branch at the same commit. All mapped commits are already reachable from `main`, so this cleanup changes names and navigation without dropping evidence.

| Clean branch | Former branch | Purpose |
| --- | --- | --- |
| `audit/claim-1-frozen-judged-baseline` | `orx/frozen-judged-baseline-claim-1` | Hardened fixed-sample Claim 1 baseline. |
| `audit/claim-2-stopping-time-clt` | `orx/claim-2-calibrated-stopping-time-clt` | Stopping-time CLT calibration sweep. |
| `audit/claim-3-decomposition-anscombe` | `orx/claim-3-decomposition-and-anscombe` | Decomposition and full-prefix Anscombe audit. |
| `audit/claim-4-single-run-intervals` | `orx/claim-4-single-run-confidence-intervals` | Literal target audit and single-run interval coverage. |
| `audit/claim-5-synthetic-dssat` | `orx/claim-5-synthetic-and-dssat-experiments` | Synthetic and DSSAT experiment implementation. |
| `release/claim-1-evidence` | `orx/evaluator-visible-claim-1-evidence` | Claim 1 evaluator-visible evidence. |
| `release/claim-2-evidence` | `orx/evaluator-visible-claim-2-evidence` | Claim 2 evaluator-visible evidence. |
| `release/claim-3-evidence` | `orx/evaluator-visible-claim-3-evidence` | Claim 3 evaluator-visible evidence. |
| `release/claim-4-evidence` | `orx/evaluator-visible-claim-4-evidence` | Claim 4 falsification/formula evidence. |
| `release/claim-5-evidence` | `orx/evaluator-visible-claim-5-evidence` | Claim 5 evaluator-visible evidence. |
| `release/publication-gates` | `orx/final-publication-gates` | Publication allowlist and blind traversal gates. |
| `release/candidate-audit-report` | `orx/release-candidate-audit-and-report` | Release figures and candidate report. |
| `audit/claim-5-stopped-draw-evidence` | `orx/repair-claim-5-stopped-draw-evidence` | Corrected stopped-draw evidence. |
| `release/concise-evidence-stream` | `orx/repair-concise-release-evidence-stream` | Cumulative release regression and concise payload. |
| `release/cumulative-navigation-repair` | `orx/repair-cumulative-current-page-navigation` | Current-page navigation repair. |
| `release/final-gate-audits` | `orx/repair-final-release-gate-audits` | Latest final gate audit, same tip as `main`. |

## Attribution policy

All reachable commits will be normalized to:

```text
MachineLearning-Nerd <37579156+MachineLearning-Nerd@users.noreply.github.com>
```

This identity describes the collection owner’s published commit attribution. It does not claim authorship of the paper or of the original research.

## Verification checklist

- [x] Default branch is `main`.
- [x] All former `orx/*` branches have a descriptive target name.
- [x] Every mapped branch tip is reachable from `main`.
- [ ] Repository name is descriptive and consistent with the collection.
- [ ] Reachable commit author and committer identities are normalized.
- [x] README explains the paper, five claims, evidence paths, branch map, citation, and thank-you note.
- [ ] All old branch names are removed from GitHub after clean branches are pushed.
