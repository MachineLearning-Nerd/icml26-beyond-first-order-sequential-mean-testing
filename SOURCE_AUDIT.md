# Paper and source audit

## Paper identity

- Title: *Beyond First-order Asymptotics in Sequential Mean Testing*
- Authors: Vikas Deep and Shubhada Agrawal
- ICML submission/OpenReview ID: HMyCBL2yMV
- arXiv: 2606.04520v1
- arXiv page: https://arxiv.org/abs/2606.04520
- OpenReview page: https://openreview.net/forum?id=HMyCBL2yMV
- HTML source used for the claim audits: https://ar5iv.labs.arxiv.org/html/2606.04520
- Audited HTML SHA-256: cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0
- Retrieval dates recorded in the claim-level audits: 2026-08-01 and 2026-08-02.

## Claim anchors

- Claim 1: Theorem 4.2 and Assumption 4.1.
- Claim 2: Theorem 4.4 and equation (3), including the first-crossing boundary.
- Claim 3: equations (5)-(6) and Lemma A.8.
- Claim 4: Proposition 4.5, equations (39)-(42), and the deterministic target 1 / KL_inf(q,m0).
- Claim 5: Section 5’s three experiments and the paper’s DSSAT description.

The detailed source anchors and assumptions are preserved in space_candidate/evidence/claim-1/ through claim-5/.

## Data audit

The paper does not identify the exact crop, observations, normalization, file revision, pool, or bootstrap seed behind its crop-yield figure. The repository therefore uses a pinned public substitute:

- Source repository: https://github.com/DSSAT/dssat-csm-data
- Commit: a4f95d3ef36f1358bdeb5db49d498d5db373ba7a
- Dataset slice: nonnegative HWAM entries from the pinned maize files.
- Limitation: this is not represented as the authors’ exact Figure 5 data.

## Repository audit

- Final repository: https://github.com/MachineLearning-Nerd/icml26-beyond-first-order-sequential-mean-testing
- Former repository: icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing
- Final branch and attribution evidence: BRANCH_AUDIT.md
- Content and publication verification: EVIDENCE_MANIFEST.json and verify_final.py
