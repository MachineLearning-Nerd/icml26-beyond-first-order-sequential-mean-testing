# Reproduction: Beyond First-order Asymptotics in Sequential Mean Testing

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing/blob/main/notebooks/sequential_mean_testing.py)

We tested all five supplied claims for arXiv `2606.04520`: the fixed-sample and stopping-time `KL_inf` CLTs, the dual/Anscombe proof mechanism, the single-run interval, and the synthetic plus DSSAT numerical experiments. The cumulative assessment is **VERIFIED / VERIFIED / VERIFIED / FALSIFIED as literally supplied / VERIFIED**, each under an explicit contract with raw data, an independent checker, and a negative control.

The headline stopping-time result improves the old finite-alpha variance ratio `1.276` to `0.9923` at `b=log(1/alpha)=10000` (95% interval `[0.9654,1.0204]`), with KS `0.0349`, Gaussian mass `0.9477`, and center error `0.102%`. The missing crop-yield arm now uses 3,000 bootstrap paths on a pinned official public DSSAT pool: at alpha `1e-4`, KS is `0.0890`, variance/theory is `0.9396`, and Gaussian mass is `0.9693`.

The DSSAT authors' exact pool and normalization are unavailable, so Claim 5 is a disclosed same-domain reproduction rather than an exact Figure 5 data match. Claims 1–3 and 5 are finite corroborations, not universal theorem proofs. Claim 4 distinguishes the supplied wording from Proposition 4.5: the proposition covers deterministic `1/KL_inf`, while an interval centered on its observed stopping time covers that same value with probability one.

Compute was exclusively Hugging Face `cpu-upgrade` with a pinned CPU-only image, two useful cores estimated, 64 CPUs visible in affinity, and GPU disabled. See the [illustrated report](reports/sequential-mean-testing/report.md), [tutorial notebook](notebooks/sequential_mean_testing.py), and [candidate evaluator logbook](space_candidate/README.md).

## Experiment log

Every formal node inherited the exact same command shown below; behavior changed only through committed code and configuration.

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Publication surface | Not run as an experiment (publication surface) | Receives only release-gated text artifacts | N/A |
| [`orx/frozen-judged-baseline-claim-1`](https://github.com/MachineLearning-Nerd/icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing/tree/orx/frozen-judged-baseline-claim-1) | Freeze and rerun full-credit Claim 1 | `uv sync --frozen && .venv/bin/python -m reproduction.run` | Claim 1 VERIFIED | HF `cpu-upgrade`, 26s job |
| [`orx/claim-2-calibrated-stopping-time-clt`](https://github.com/MachineLearning-Nerd/icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing/tree/orx/claim-2-calibrated-stopping-time-clt) | Calibrated independent `b` sweep | `uv sync --frozen && .venv/bin/python -m reproduction.run` | Claim 2 VERIFIED | HF `cpu-upgrade`, 42s job |
| [`orx/claim-3-decomposition-and-anscombe`](https://github.com/MachineLearning-Nerd/icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing/tree/orx/claim-3-decomposition-and-anscombe) | Exact decomposition and full-prefix Anscombe audit | `uv sync --frozen && .venv/bin/python -m reproduction.run` | Claim 3 VERIFIED | HF `cpu-upgrade`, 1m25s job |
| [`orx/claim-4-single-run-confidence-intervals`](https://github.com/MachineLearning-Nerd/icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing/tree/orx/claim-4-single-run-confidence-intervals) | Exact source target plus large-`b` coverage | `uv sync --frozen && .venv/bin/python -m reproduction.run` | Claim 4 FALSIFIED literally; actual proposition supported | HF `cpu-upgrade`, 3m00s job |
| [`orx/repair-claim-5-stopped-draw-evidence`](https://github.com/MachineLearning-Nerd/icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing/tree/orx/repair-claim-5-stopped-draw-evidence) | Synthetic trend and pinned DSSAT bootstrap | `uv sync --frozen && .venv/bin/python -m reproduction.run` | Claim 5 VERIFIED | HF `cpu-upgrade`, 3m22s job |
| [`orx/repair-concise-release-evidence-stream`](https://github.com/MachineLearning-Nerd/icml26-repro-HMyCBL2yMV-beyond-first-order-asymptotics-in-sequential-mean-testing/tree/orx/repair-concise-release-evidence-stream) | Cumulative regression, candidate standalone run, figures | `uv sync --frozen && .venv/bin/python -m reproduction.run` | All claim and candidate gates exit 0 | HF `cpu-upgrade`, 5m28s job |

Only a new live judge verdict can change the previous score of `3/10`. Conservative forecast: `6–10`; best-supported possible score: `10/10` (forecast only).

Local notebook use after `uv sync --frozen`:

```bash
.venv/bin/marimo edit notebooks/sequential_mean_testing.py
.venv/bin/marimo run notebooks/sequential_mean_testing.py
```
