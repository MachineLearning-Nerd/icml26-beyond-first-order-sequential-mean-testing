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
    with (HERE / "decomposition_metrics.csv").open(newline="", encoding="utf-8") as handle:
        decomposition = sorted(csv.DictReader(handle), key=lambda row: int(row["n"]))
    with (HERE / "anscombe_metrics.csv").open(newline="", encoding="utf-8") as handle:
        anscombe = list(csv.DictReader(handle))
    largest = decomposition[-1]
    narrow = [row for row in anscombe if int(row["n"]) >= 10000 and float(row["delta"]) == 0.01]
    probabilities = {
        (int(row["n"]), float(row["delta"])): float(row["exceedance_probability"])
        for row in anscombe
    }
    checks = {
        "identity": float(largest["max_identity_error"]) <= 2e-12,
        "dual_remainder": float(largest["t1_rms"]) <= 0.01,
        "dual_relative": float(largest["t1_to_t2_rms_ratio"]) <= 0.02,
        "linear_variance": 0.98 <= float(largest["full_to_t2_variance_ratio"]) <= 1.02,
        "dual_remainder_trend": all(
            float(left["t1_rms"]) > float(right["t1_rms"])
            for left, right in zip(decomposition, decomposition[1:])
        ),
        "anscombe_narrow_window": all(float(row["wilson_high"]) < 0.1 for row in narrow),
        "anscombe_nested_windows": all(
            probabilities[(n, smaller)] <= probabilities[(n, larger)]
            for n in [500, 2000, 10000, 50000]
            for smaller, larger in zip([0.01, 0.02, 0.05, 0.1], [0.02, 0.05, 0.1, 0.2], strict=True)
        ),
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
    if first_page["slug"] != "current-claim-3":
        failures.append("current Claim 3 page is not first in navigation")
    page = (CANDIDATE / first_page["file"]).read_text(encoding="utf-8")
    required_text = [
        "# Claim 3 — VERIFIED for the declared finite contract",
        "Exact claim contract",
        "Lemma A.8",
        "140,000",
        "Current nonzero-exit verifier",
        "Both controls fail",
        "does not prove the universal quantifiers",
    ]
    failures.extend(f"canonical page missing: {text}" for text in required_text if text not in page)
    required_files = [
        "claim_contract.json",
        "source_audit.md",
        "method.md",
        "limitations.md",
        "decomposition_metrics.csv",
        "anscombe_metrics.csv",
        "checker_output.json",
        "negative_controls.json",
        "environment.json",
        "raw_parts_manifest.json",
    ]
    failures.extend(f"candidate missing: {name}" for name in required_files if not (HERE / name).is_file())
    if len(list(HERE.glob("claim3-raw-part-*.csv"))) != 7:
        failures.append("raw Claim 3 CSV parts missing")

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
        "claim": 3,
        "status": "VERIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "largest_decomposition": largest,
        "narrow_anscombe": narrow,
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
