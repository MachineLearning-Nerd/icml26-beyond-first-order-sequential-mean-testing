from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parents[1]


def main() -> int:
    with (HERE / "single_run_ci_metrics.csv").open(newline="", encoding="utf-8") as handle:
        rows = sorted(csv.DictReader(handle), key=lambda row: float(row["b"]))
    largest = rows[-1]
    checks = {
        "coverage_95": float(largest["coverage_95_wilson_low"]) <= 0.95 <= float(largest["coverage_95_wilson_high"]),
        "coverage_50": float(largest["coverage_50_wilson_low"]) <= 0.50 <= float(largest["coverage_50_wilson_high"]),
        "vhat_mean": 0.97 <= float(largest["vhat_ratio_mean"]) <= 1.03,
        "vhat_median": 0.97 <= float(largest["vhat_ratio_median"]) <= 1.03,
        "center": abs(float(largest["center_relative_error"])) <= 0.003,
        "vhat_median_error_improves": float(rows[-1]["vhat_relative_error_median"])
        < float(rows[-2]["vhat_relative_error_median"])
        < float(rows[0]["vhat_relative_error_median"]),
        "vhat_q90_error_improves": float(rows[-1]["vhat_relative_error_q90"])
        < float(rows[-2]["vhat_relative_error_q90"])
        < float(rows[0]["vhat_relative_error_q90"]),
        "coverage_95_improves": abs(float(rows[-1]["coverage_95"]) - 0.95)
        < abs(float(rows[0]["coverage_95"]) - 0.95),
        "coverage_50_improves": abs(float(rows[-1]["coverage_50"]) - 0.50)
        < abs(float(rows[0]["coverage_50"]) - 0.50),
        "literal_self_coverage_95": float(largest["literal_self_coverage_95"]) == 1.0,
        "literal_self_coverage_50": float(largest["literal_self_coverage_50"]) == 1.0,
    }
    failures = [name for name, passed in checks.items() if not passed]
    controls = json.loads((HERE / "negative_controls.json").read_text(encoding="utf-8"))
    failures.extend(name for name, control in controls.items() if control["observed"] != "FAIL" or not control["valid"])
    checker = subprocess.run(
        [sys.executable, (HERE / "independent_checker.py").as_posix()],
        cwd=CANDIDATE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if checker.returncode != 0:
        failures.append("independent checker failed")

    logbook = json.loads((CANDIDATE / "logbook.json").read_text(encoding="utf-8"))
    children = logbook["root"]["children"]
    current_page = next((child for child in children if child["slug"] == "current-claim-4"), None)
    if current_page is None:
        failures.append("current Claim 4 page is absent from navigation")
        current_page = {"file": "pages/current-claim-4/page.md"}
    historical_index = min(index for index, child in enumerate(children) if child["slug"] == "overview")
    claim_index = next(
        (index for index, child in enumerate(children) if child["slug"] == "current-claim-4"), len(children)
    )
    if claim_index >= historical_index:
        failures.append("current Claim 4 page appears after historical pages")
    page = (CANDIDATE / current_page["file"]).read_text(encoding="utf-8")
    required_text = [
        "# Claim 4 — FALSIFIED as literally supplied",
        "Exact source-target audit",
        "0.9513",
        "0.5010",
        "1.00043",
        "40,000",
        "Current nonzero-exit verifier",
        "coverage one",
        "not a prediction interval",
    ]
    failures.extend(f"canonical page missing: {text}" for text in required_text if text not in page)
    required_files = [
        "claim_contract.json",
        "source_audit.md",
        "method.md",
        "limitations.md",
        "single_run_ci_metrics.csv",
        "checker_output.json",
        "negative_controls.json",
        "environment.json",
        "raw_parts_manifest.json",
    ]
    failures.extend(f"candidate missing: {name}" for name in required_files if not (HERE / name).is_file())
    if len(list(HERE.glob("single-run-ci-paths-part-*.csv"))) != 4:
        failures.append("raw Claim 4 CSV parts missing")

    protected_root = CANDIDATE / "historical" / "judged-7f2c76f4"
    manifest = CANDIDATE / "evidence" / "protected-judged-revision-manifest.sha256"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected_hash, relative = line.split("  ", 1)
        if not (CANDIDATE / relative).is_file():
            failures.append(f"judged file missing from candidate: {relative}")
            continue
        protected_copy = protected_root / relative
        source = protected_copy if protected_copy.is_file() else CANDIDATE / relative
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected_hash:
            failures.append(f"protected historical hash mismatch: {relative}")

    result = {
        "claim": 4,
        "status": "FALSIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "largest_b": largest,
        "checks": checks,
        "controls": {name: control["observed"] for name, control in controls.items()},
        "independent_checker_exit": checker.returncode,
        "independent_checker_output": checker.stdout,
        "canonical_page": current_page["file"],
    }
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
