from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parents[1]
GENERATED_CANDIDATES = [
    CANDIDATE.parent / ".openresearch" / "artifacts" / "claim_1" / "generated",
    CANDIDATE / ".generated" / "claim-1",
]


def ks_distance(values: list[float]) -> float:
    ordered = sorted(values)
    total = len(ordered)
    normal = NormalDist()
    return max(
        max((index + 1) / total - normal.cdf(value), normal.cdf(value) - index / total)
        for index, value in enumerate(ordered)
    )


def load_raw(path: Path) -> dict[tuple[str, int], list[float]]:
    groups: dict[tuple[str, int], list[float]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups[(row["distribution"], int(row["n"]))].append(float(row["z_standardized"]))
    return groups


def main() -> int:
    with (HERE / "fixed_clt_metrics.csv").open(newline="", encoding="utf-8") as handle:
        metrics = {(row["distribution"], int(row["n"])): row for row in csv.DictReader(handle)}
    groups = load_raw(HERE / "fixed_clt_replicates.csv")
    failures: list[str] = []

    for key, values in groups.items():
        row = metrics[key]
        coverage = sum(abs(value) <= 1.959963984540054 for value in values) / len(values)
        recomputed = {
            "standardized_mean": statistics.fmean(values),
            "variance_ratio": statistics.variance(values),
            "gaussian_95_coverage": coverage,
            "ks_distance": ks_distance(values),
        }
        for name, value in recomputed.items():
            if not math.isclose(value, float(row[name]), rel_tol=0.0, abs_tol=2e-12):
                failures.append(f"{key} raw-data mismatch: {name}")

    for distribution in ("Beta(3,2)", "Bernoulli(0.6)"):
        large = metrics[(distribution, 5000)]
        small = metrics[(distribution, 50)]
        checks = {
            "variance_ratio": 0.9 <= float(large["variance_ratio"]) <= 1.1,
            "ks_distance": float(large["ks_distance"]) <= 0.04,
            "coverage_interval": float(large["coverage_wilson_low"]) <= 0.95 <= float(large["coverage_wilson_high"]),
            "standardized_mean": abs(float(large["standardized_mean"])) <= 0.05,
            "ks_trend": float(large["ks_distance"]) < float(small["ks_distance"]),
        }
        failures.extend(f"{distribution} failed {name}" for name, passed in checks.items() if not passed)

    control = json.loads((HERE / "negative_control.json").read_text(encoding="utf-8"))
    if control["observed"] != "FAIL" or not control["valid"]:
        failures.append("negative control did not fail as intended")

    for generated in GENERATED_CANDIDATES:
        if generated.exists():
            committed_metrics = (HERE / "fixed_clt_metrics.csv").read_text(encoding="utf-8").splitlines()
            regenerated_metrics = (generated / "fixed_clt_metrics.csv").read_text(encoding="utf-8").splitlines()
            if committed_metrics != regenerated_metrics:
                failures.append(f"committed metrics differ from regenerated metrics at {generated}")
            regenerated_raw = gzip.decompress((generated / "fixed_clt_replicates.csv.gz").read_bytes())
            if (HERE / "fixed_clt_replicates.csv").read_bytes() != regenerated_raw:
                failures.append(f"committed raw replicates differ from regenerated replicates at {generated}")

    logbook = json.loads((CANDIDATE / "logbook.json").read_text(encoding="utf-8"))
    children = logbook["root"]["children"]
    current_page = next((child for child in children if child["slug"] == "current-claim-1"), None)
    if current_page is None:
        failures.append("current Claim 1 page is absent from navigation")
        current_page = {"file": "pages/current-claim-1/page.md"}
    historical_index = min(index for index, child in enumerate(children) if child["slug"] == "overview")
    claim_index = next((index for index, child in enumerate(children) if child["slug"] == "current-claim-1"), len(children))
    if claim_index >= historical_index:
        failures.append("current Claim 1 page appears after historical pages")
    page = (CANDIDATE / current_page["file"]).read_text(encoding="utf-8")
    required_text = [
        "# Claim 1 — VERIFIED",
        "Exact claim contract",
        "Assumption 4.1",
        "Direct evidence",
        "Current nonzero-exit verifier",
        "all 40,000 raw standardized replicates",
        "negative-control output",
        "finite Monte Carlo experiment is not a proof",
    ]
    failures.extend(f"canonical page missing: {text}" for text in required_text if text not in page)
    required_files = [
        "claim_contract.json",
        "source_audit.md",
        "method.md",
        "limitations.md",
        "fixed_clt_metrics.csv",
        "fixed_clt_replicates.csv",
        "checker_output.json",
        "negative_control.json",
        "environment.json",
    ]
    failures.extend(f"candidate missing: {name}" for name in required_files if not (HERE / name).is_file())
    for historical in ("overview", "claims", "evidence", "verification-run", "conclusion"):
        historical_page = CANDIDATE / "pages" / historical / "page.md"
        if "Historical rejected baseline" not in historical_page.read_text(encoding="utf-8"):
            failures.append(f"historical page not labeled: {historical}")

    protected_root = CANDIDATE / "historical" / "judged-7f2c76f4"
    manifest = CANDIDATE / "evidence" / "protected-judged-revision-manifest.sha256"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected_hash, relative = line.split("  ", 1)
        if not (CANDIDATE / relative).is_file():
            failures.append(f"judged file missing from candidate: {relative}")
            continue
        protected_copy = protected_root / relative
        source = protected_copy if protected_copy.is_file() else CANDIDATE / relative
        observed_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if observed_hash != expected_hash:
            failures.append(f"protected historical hash mismatch: {relative}")

    result = {
        "claim": 1,
        "status": "VERIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "raw_rows_checked": sum(len(values) for values in groups.values()),
        "negative_control": control["observed"],
        "canonical_page": current_page["file"],
        "protected_files_checked": len(manifest.read_text(encoding="utf-8").splitlines()),
    }
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
