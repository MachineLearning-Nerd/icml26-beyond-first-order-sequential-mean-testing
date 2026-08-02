# Evaluator-visible traversal matrix

Canonical entrypoint: `README.md` → `#/release-report` → current claim pages. The audit uses only files reachable from that path.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `pages/current-claim-1/page.md` | yes | yes | yes | yes | yes | yes | VERIFIED |
| 2 | `pages/current-claim-2/page.md` | yes | yes | yes | yes | yes | yes | VERIFIED |
| 3 | `pages/current-claim-3/page.md` | yes | yes | yes | yes | yes | yes | VERIFIED |
| 4 | `pages/current-claim-4/page.md` | yes | yes | yes | yes | yes | yes | FALSIFIED literally |
| 5 | `pages/current-claim-5/page.md` | yes | yes | yes | yes | yes | yes | VERIFIED |

For each row the canonical page contains or links: exact source quantifiers and assumptions; source code; fixed command and `uv.lock`; inline decisive numbers; full raw CSV or a hash manifest linking every raw part; independent checker source and output; negative-control output; limitations; Git SHA; deterministic seeds; HF flavor, CPU allocation, runtime; and a verifier that exits nonzero when a gate fails.

Historical safety: all files from judged revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40` are preserved byte-for-byte under `historical/judged-7f2c76f4/`. Current verification precedes every navigation entry labeled **Historical rejected baseline**, and every current page names the superseded revision.
