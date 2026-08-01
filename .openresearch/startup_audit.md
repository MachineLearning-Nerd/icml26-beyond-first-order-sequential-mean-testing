# Startup audit

- Project: `b12a8272-8ed7-45c5-bdad-d94b24eae9c2`; empty experiment tree and no prior runs.
- Repository: detached `348dd7825a288ad27ba178464635e7014c3c9a04`; `main` and `origin/main` matched; clean start.
- Disk: 43 GiB available at startup.
- Scientific compute: Hugging Face `cpu-upgrade` only; GPU use prohibited.
- Environment: Python 3.12, `uv`, repository `.venv`, committed lock; fixed command `uv sync --frozen && .venv/bin/python -m reproduction.run`.
- Paper HTML: ar5iv URL, retrieved 2026-08-01 with explicit User-Agent, SHA-256 `cf1579a4827d3248d278fc782191e672b191676c10e338d0ecd3439b9884caa0`.
- Verdict dataset: `ICML-2026-agent-repro/verdicts@9fbce7a8...`, file SHA-256 `a5da812b70987b6c4f5469eb861b9fa687806d04cf9dd1759a0243cefd8afc4c`; exactly one object matched `space_id == DineshAI/HMyCBL2yMV`.
- Protected Space: exact revision `7f2c76f4ea76832d2f8f79e68b1efb3349b29d40`; 17-file SHA-256 manifest created before candidate work.
- Reference Space inspected at `4a98fe4c75020e5167091c944b6ce77b18464a24`.
