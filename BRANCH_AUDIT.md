# Branch and attribution audit

Repository: MachineLearning-Nerd/icml26-beyond-first-order-sequential-mean-testing

Former repository: icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing

Paper: *Beyond First-order Asymptotics in Sequential Mean Testing*
Paper authors: Vikas Deep and Shubhada Agrawal
OpenReview: https://openreview.net/forum?id=HMyCBL2yMV
arXiv: https://arxiv.org/abs/2606.04520

## Final branch policy

main is the cumulative publication surface. The 16 descriptive branches are preserved as navigable audit and release checkpoints. Their former orx names are recorded for provenance only; no orx branch is part of the final GitHub ref set.

All mapped checkpoint tips were already reachable from main before the dossier was added. The cleanup therefore changes navigation and naming without discarding the evidence history or collapsing the branch topology.

| Final branch | Former branch | Role |
| --- | --- | --- |
| main | main | Cumulative publication surface and current final-gate state. |
| audit/claim-1-frozen-judged-baseline | orx/frozen-judged-baseline-claim-1 | Hardened fixed-sample Claim 1 baseline; Claim 1 verified under its finite contract. |
| audit/claim-2-stopping-time-clt | orx/claim-2-calibrated-stopping-time-clt | Calibrated stopping-time CLT sweep; Claim 2 verified under its finite contract. |
| audit/claim-3-decomposition-anscombe | orx/claim-3-decomposition-and-anscombe | Exact decomposition and full-prefix Anscombe audit; Claim 3 verified under its finite contract. |
| audit/claim-4-single-run-intervals | orx/claim-4-single-run-confidence-intervals | Literal target audit and interval coverage; Claim 4 falsified literally while the displayed deterministic-target formula is supported. |
| audit/claim-5-stopped-draw-evidence | orx/repair-claim-5-stopped-draw-evidence | Corrected stopped-draw evidence for Claim 5. |
| audit/claim-5-synthetic-dssat | orx/claim-5-synthetic-and-dssat-experiments | Synthetic and public DSSAT experiment implementation; Claim 5 verified under its declared contract. |
| release/claim-1-evidence | orx/evaluator-visible-claim-1-evidence | Evaluator-visible Claim 1 evidence, checker, and control. |
| release/claim-2-evidence | orx/evaluator-visible-claim-2-evidence | Evaluator-visible Claim 2 evidence, checker, and controls. |
| release/claim-3-evidence | orx/evaluator-visible-claim-3-evidence | Evaluator-visible Claim 3 evidence, checker, and controls. |
| release/claim-4-evidence | orx/evaluator-visible-claim-4-evidence | Evaluator-visible Claim 4 falsification and formula evidence. |
| release/claim-5-evidence | orx/evaluator-visible-claim-5-evidence | Evaluator-visible Claim 5 synthetic and DSSAT evidence. |
| release/publication-gates | orx/final-publication-gates | Publication allowlist, upload manifest, and blind traversal gates. |
| release/candidate-audit-report | orx/release-candidate-audit-and-report | Release figures and candidate report generation. |
| release/concise-evidence-stream | orx/repair-concise-release-evidence-stream | Cumulative regression, standalone candidate run, and concise release payload. |
| release/cumulative-navigation-repair | orx/repair-cumulative-current-page-navigation | Corrected cumulative current-page navigation. |
| release/final-gate-audits | orx/repair-final-release-gate-audits | Latest final publication-gate audit; same content tip as the cumulative surface before this dossier. |

## Attribution

All reachable commits in the final published history must use:

~~~text
MachineLearning-Nerd <37579156+MachineLearning-Nerd@users.noreply.github.com>
~~~

This is the collection owner’s Git attribution. It does not claim authorship of the paper, its proofs, or its experiments.

## Audit basis and invariants

- Final ref set: main plus 16 descriptive audit/release branches.
- No orx refs remain locally or on the GitHub remote.
- Every descriptive branch tip is reachable from main.
- Default branch is main.
- The repository name follows the collection convention: icml26-paper-topic.
- The pre-dossier main tip was 62b4b4842a5569eaa1ca1be82ffd2132702846cf.
- The pre-dossier history contained 28 reachable commits.
- A pre-dossier recovery bundle was created outside the repository; SHA-256 e9f53b5ec91e9138274c80e2319117a91e05d485587022fc0a5ef1c820b63cc5.
- verify_final.py checks the final remote branch set, commit identities, dossier hashes, release gate, and decisive claim outputs.

The branch names above are final names, not proposals. Former names are retained only in this provenance table and in historical commit messages where they are part of the original record.
