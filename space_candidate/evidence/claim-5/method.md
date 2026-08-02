# Claim 5 method

The cumulative runner first regenerates the exact Section 5 synthetic evidence already accepted for Claims 1 and 2. Claim 5 checks those current verifier outputs and directly compares the two paper alpha levels under both boundary choices.

For the real-data arm, the HF job parses all ten pinned official maize A-files, extracts every nonnegative observed `HWAM` value, retains zero as a legitimate crop failure, and normalizes by the pool maximum. It then constructs the empirical dual optimum, plug-in `KL_inf`, and stopping-time variance.

Using one deterministic seed, it generates 3,000 nested with-replacement bootstrap paths and records the first crossing of the constant `log(1/alpha)` boundary at alpha `1e-2`, `1e-3`, and the paper's `1e-4`. The extra larger levels were fixed before the run and test the reported direction without selecting a favorable endpoint. Every stopped support-count vector, prior evidence, and at-stop evidence is persisted.

An independent checker hashes all source files, replays every bootstrap draw, checks every stopped count vector and first-hit inequality, recomputes each `KL_inf` with an independent scalar Brent solver, verifies nested stopping times, and reconstructs aggregate metrics from all 9,000 raw records. The verifier exits nonzero unless the prespecified scientific, trend, provenance, synthetic-regression, and negative-control gates pass.

Fixed command: `uv sync --frozen && .venv/bin/python -m reproduction.run`.
