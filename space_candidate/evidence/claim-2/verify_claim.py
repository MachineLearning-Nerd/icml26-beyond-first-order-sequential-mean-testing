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
    with (HERE / "stopping_clt_metrics.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    growing = sorted((row for row in rows if row["boundary"] == "growing"), key=lambda row: float(row["b"]))
    largest = growing[-1]
    checks = {
        "variance_ci": float(largest["variance_ratio_ci_low"]) <= 1.0 <= float(largest["variance_ratio_ci_high"]),
        "ks_distance": float(largest["ks_distance"]) <= 0.05,
        "standardized_mean": abs(float(largest["standardized_mean"])) <= 0.12,
        "centering_relative_error": abs(float(largest["centering_relative_error"])) <= 0.003,
        "skewness": abs(float(largest["skewness"])) <= 0.12,
        "excess_kurtosis": abs(float(largest["excess_kurtosis"])) <= 0.12,
        "coverage": 0.94 <= float(largest["gaussian_95_coverage"]) <= 0.96,
        "ks_trend": float(growing[-1]["ks_distance"]) < float(growing[-2]["ks_distance"]) < float(growing[0]["ks_distance"]),
        "centering_trend": abs(float(growing[-1]["centering_relative_error"])) < abs(float(growing[-2]["centering_relative_error"])) < abs(float(growing[0]["centering_relative_error"])),
        "variance_trend": abs(float(growing[-1]["variance_ratio"]) - 1.0) < abs(float(growing[0]["variance_ratio"]) - 1.0),
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
    first_page = logbook["root"]["children"][0]
    if first_page["slug"] != "current-claim-2":
        failures.append("current Claim 2 page is not first in navigation")
    page = (CANDIDATE / first_page["file"]).read_text(encoding="utf-8")
    required_text = [
        "# Claim 2 — VERIFIED at the paper setting",
        "Exact claim contract",
        "Assumption 4.1",
        "160,000",
        "Current nonzero-exit verifier",
        "Both controls fail",
        "does not prove the arbitrary-q theorem",
    ]
    failures.extend(f"canonical page missing: {text}" for text in required_text if text not in page)
    required_files = [
        "claim_contract.json",
        "source_audit.md",
        "method.md",
        "limitations.md",
        "stopping_clt_metrics.csv",
        "checker_output.json",
        "negative_controls.json",
        "environment.json",
    ]
    failures.extend(f"candidate missing: {name}" for name in required_files if not (HERE / name).is_file())
    if len(list(HERE.glob("stopping_paths-part-*.csv"))) != 8:
        failures.append("raw path CSV parts missing")

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
        "claim": 2,
        "status": "VERIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "largest_b": largest,
        "checks": checks,
        "controls": {name: control["observed"] for name, control in controls.items()},
        "independent_checker_exit": checker.returncode,
        "independent_checker_output": checker.stdout,
        "canonical_page": first_page["file"],
    }
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
