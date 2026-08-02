# Command and compute ledger

The fixed research command on every node was exactly:

```bash
uv sync --frozen && .venv/bin/python -m reproduction.run
```

Every research launch used this orchestration form, with only the experiment id changing:

```bash
orx exp run <experiment-id> --flavor cpu-upgrade --image 'ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040' --timeout 1h
```

Evidence was read only with `orx exp wait`, `orx runs`, `orx exp status`, and `orx logs`. Repository inspection used `git status --short`, `git diff --check`, `git log`, `git branch`, and `git ls-remote`. Paper retrieval used an explicit browser User-Agent and produced SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`. Candidate and judged Space revisions were downloaded into fresh directories before comparison. No local scientific command and no GPU command was executed.

The complete experiment tree and individual run ids, durations, commits, outcomes, and repair notes remain in the OpenResearch experiment descriptions. Reader-facing lineage and exact fixed commands are reproduced in the GitHub README and technical report.
