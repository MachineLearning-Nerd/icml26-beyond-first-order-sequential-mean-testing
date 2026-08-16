# Environment and reproducibility record

## Locked command

The cumulative scientific run and release regression use:

~~~bash
uv sync --frozen
.venv/bin/python -m reproduction.run
~~~

The dependency lock is uv.lock; the project definition is pyproject.toml; the experiment configuration is reproduction/config.json.

## Accepted compute record

- Provider: Hugging Face cpu-upgrade.
- Image: ghcr.io/astral-sh/uv:0.8.3-python3.12-bookworm-slim@sha256:74b8fe8ec5931f3930cfb6c87b46aeb1dbd497a609f6abf860fd0f4390f8b040.
- Hardware policy: approximately two useful CPU cores, 64 CPUs visible in affinity, no GPU.
- Accepted cumulative job: f62c024e-5774-4715-b713-151f3bcc9a68.
- Recorded job duration: 5m28s; the report records 300.206 seconds of cumulative plus standalone scientific runtime.

This dossier pass does not rerun the scientific experiments. It rechecks the existing independent checkers, release hashes, controls, branch topology, and publication gate with verify_final.py.

## Claim 5 data provenance

The exact author crop-yield pool is not identified in the paper. The reproduction uses the primary public DSSAT/dssat-csm-data repository at commit a4f95d3ef36f1358bdeb5db49d498d5db373ba7a, retaining nonnegative HWAM entries from eight of ten pinned maize files. This is a declared same-domain substitution, not an exact recovery of the authors’ hidden Figure 5 data.

## Safety and attribution

The public release allowlist excludes private keys, tokens, binary figures, and the upload manifest itself. The upload manifest hashes the allowlisted text and source artifacts. Published dossier commits use MachineLearning-Nerd <37579156+MachineLearning-Nerd@users.noreply.github.com>.
