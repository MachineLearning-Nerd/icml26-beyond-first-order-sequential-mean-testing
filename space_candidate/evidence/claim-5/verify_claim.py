from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parents[1]
sys.path.insert(0, str(CANDIDATE))

from reproduction.claim5 import EXPECTED_SOURCE_HASHES, verify_result


GENERATED_CANDIDATES = [
    CANDIDATE.parent / ".openresearch" / "artifacts" / "claim_5" / "generated",
    CANDIDATE / ".generated" / "claim-5",
]


def close(left: float, right: float, tolerance: float = 2e-11) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    with (HERE / "dssat_bootstrap_metrics.csv").open(newline="", encoding="utf-8") as handle:
        metrics = list(csv.DictReader(handle))
    result = {
        "metrics": metrics,
        "source_manifest": json.loads((HERE / "dssat_source_manifest.json").read_text(encoding="utf-8")),
        "synthetic": json.loads((HERE / "synthetic_crosscheck.json").read_text(encoding="utf-8")),
        "controls": json.loads((HERE / "negative_controls.json").read_text(encoding="utf-8")),
    }
    scientific = verify_result(result)
    failures.extend(f"scientific gate: {failure}" for failure in scientific["failures"])

    groups: dict[float, list[int]] = defaultdict(list)
    by_path: dict[int, dict[float, int]] = defaultdict(dict)
    raw_rows = 0
    with (HERE / "dssat_bootstrap_paths.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            raw_rows += 1
            alpha = float(row["alpha"])
            path = int(row["path"])
            tau = int(row["tau"])
            counts = json.loads(row["counts_json"])
            if len(counts) != 44 or sum(counts) != tau:
                failures.append(f"raw count mismatch alpha={alpha} path={path}")
            if not (float(row["evidence_previous"]) < float(row["b"]) <= float(row["evidence_at_stop"]) + 5e-9):
                failures.append(f"first-hit inequality mismatch alpha={alpha} path={path}")
            groups[alpha].append(tau)
            by_path[path][alpha] = tau
    if raw_rows != 9000:
        failures.append(f"raw row count {raw_rows}, expected 9000")
    nested_failures = sum(
        not (values[0.01] <= values[0.001] <= values[0.0001])
        for values in by_path.values()
        if len(values) == 3
    )
    if len(by_path) != 3000 or nested_failures:
        failures.append(f"nested path audit failed: paths={len(by_path)}, violations={nested_failures}")

    theory = json.loads((HERE / "dssat_theory.json").read_text(encoding="utf-8"))
    for metric in metrics:
        alpha = float(metric["alpha"])
        tau = np.asarray(groups[alpha], dtype=float)
        b = math.log(1.0 / alpha)
        standardized = (
            math.sqrt(b) * (tau / b - float(theory["inverse_klinf"])) / math.sqrt(float(theory["sigma2_bd"]))
        )
        recomputed = {
            "standardized_mean": float(np.mean(standardized)),
            "variance_ratio": float(np.var(standardized, ddof=1)),
            "ks_distance": float(stats.kstest(standardized, "norm").statistic),
            "gaussian_95_coverage": float(np.mean(np.abs(standardized) <= 1.959963984540054)),
            "mean_tau": float(np.mean(tau)),
        }
        failures.extend(
            f"raw aggregate mismatch alpha={alpha}: {name}"
            for name, value in recomputed.items()
            if not close(value, float(metric[name]))
        )

    source_manifest = result["source_manifest"]
    source_dir = CANDIDATE / "reproduction" / "data" / "dssat_maize"
    observed_hashes = {path.name: sha256(path) for path in sorted(source_dir.glob("*.MZA"))}
    if observed_hashes != EXPECTED_SOURCE_HASHES or source_manifest["source_hashes"] != EXPECTED_SOURCE_HASHES:
        failures.append("pinned primary-source hashes do not match")
    if sha256(HERE / "dssat_public_maize_pool.csv") != source_manifest["pool_sha256"]:
        failures.append("canonical pool hash mismatch")
    accepted = json.loads((HERE / "accepted_run_manifest.json").read_text(encoding="utf-8"))
    if sha256(HERE / "dssat_bootstrap_paths.csv") != accepted["raw_text_sha256"]:
        failures.append("accepted raw-text hash mismatch")
    checker = json.loads((HERE / "checker_output.json").read_text(encoding="utf-8"))
    if not checker["passed"] or checker["raw_paths_checked"] != 9000:
        failures.append("accepted independent checker did not verify all raw paths")

    committed_raw = (HERE / "dssat_bootstrap_paths.csv").read_bytes()
    for generated in GENERATED_CANDIDATES:
        if generated.exists():
            if gzip.decompress((generated / "dssat_bootstrap_paths.csv.gz").read_bytes()) != committed_raw:
                failures.append(f"committed raw differs from regeneration at {generated}")
            for name in ("dssat_bootstrap_metrics.csv", "dssat_public_maize_pool.csv"):
                if (HERE / name).read_bytes() != (generated / name).read_bytes():
                    failures.append(f"committed {name} differs from regeneration at {generated}")

    logbook = json.loads((CANDIDATE / "logbook.json").read_text(encoding="utf-8"))
    children = logbook["root"]["children"]
    current_page = next((child for child in children if child["slug"] == "current-claim-5"), None)
    if current_page is None:
        failures.append("current Claim 5 page absent from navigation")
        current_page = {"file": "pages/current-claim-5/page.md"}
    elif children[0]["slug"] != "current-claim-5":
        failures.append("current Claim 5 page is not first in navigation")
    page = (CANDIDATE / current_page["file"]).read_text(encoding="utf-8")
    required_text = [
        "# Claim 5 — VERIFIED",
        "Exact Section 5 scope",
        "Official public DSSAT provenance",
        "all 9,000",
        "Current nonzero-exit verifier",
        "authors do not release",
        "finite evidence",
    ]
    failures.extend(f"canonical page missing: {text}" for text in required_text if text not in page)
    required_files = [
        "claim_contract.json",
        "source_audit.md",
        "method.md",
        "limitations.md",
        "dssat_bootstrap_metrics.csv",
        "dssat_bootstrap_paths.csv",
        "dssat_public_maize_pool.csv",
        "checker_output.json",
        "negative_controls.json",
        "environment.json",
        "independent_checker.py",
    ]
    failures.extend(f"candidate missing: {name}" for name in required_files if not (HERE / name).is_file())

    protected_root = CANDIDATE / "historical" / "judged-7f2c76f4"
    protected_manifest = CANDIDATE / "evidence" / "protected-judged-revision-manifest.sha256"
    protected_lines = protected_manifest.read_text(encoding="utf-8").splitlines()
    for line in protected_lines:
        expected_hash, relative = line.split("  ", 1)
        if not (CANDIDATE / relative).is_file():
            failures.append(f"judged file missing: {relative}")
            continue
        protected_copy = protected_root / relative
        source = protected_copy if protected_copy.is_file() else CANDIDATE / relative
        if sha256(source) != expected_hash:
            failures.append(f"protected historical hash mismatch: {relative}")

    verdict = {
        "claim": 5,
        "status": "VERIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures[:30],
        "raw_rows_checked": raw_rows,
        "nested_stopping_failures": nested_failures,
        "accepted_checker_rows": checker["raw_paths_checked"],
        "scientific_scope": scientific["verdict_scope"],
        "canonical_page": current_page["file"],
        "protected_files_checked": len(protected_lines),
    }
    print(json.dumps(verdict, indent=2))
    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
