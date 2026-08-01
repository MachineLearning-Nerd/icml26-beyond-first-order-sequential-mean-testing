from __future__ import annotations

import csv
import gzip
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist


def ks_distance(values: list[float]) -> float:
    ordered = sorted(values)
    total = len(ordered)
    normal = NormalDist()
    return max(
        max((index + 1) / total - normal.cdf(value), normal.cdf(value) - index / total)
        for index, value in enumerate(ordered)
    )


def main() -> int:
    generated = Path(__file__).parent / "generated"
    groups: dict[tuple[str, int], list[float]] = defaultdict(list)
    with gzip.open(generated / "fixed_clt_replicates.csv.gz", "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups[(row["distribution"], int(row["n"]))].append(float(row["z_standardized"]))
    with (generated / "fixed_clt_metrics.csv").open(newline="", encoding="utf-8") as handle:
        metrics = {(row["distribution"], int(row["n"])): row for row in csv.DictReader(handle)}

    mismatches: list[str] = []
    recomputed = {}
    for key, values in groups.items():
        mean = statistics.fmean(values)
        variance = statistics.variance(values)
        coverage = sum(abs(value) <= 1.959963984540054 for value in values) / len(values)
        ks = ks_distance(values)
        expected = metrics[key]
        checks = {
            "mean": math.isclose(mean, float(expected["standardized_mean"]), rel_tol=0.0, abs_tol=2e-12),
            "variance": math.isclose(variance, float(expected["variance_ratio"]), rel_tol=0.0, abs_tol=2e-12),
            "coverage": math.isclose(coverage, float(expected["gaussian_95_coverage"]), rel_tol=0.0, abs_tol=2e-12),
            "ks": math.isclose(ks, float(expected["ks_distance"]), rel_tol=0.0, abs_tol=2e-12),
        }
        if not all(checks.values()):
            mismatches.append(f"{key}: {[name for name, ok in checks.items() if not ok]}")
        recomputed[str(key)] = {"mean": mean, "variance": variance, "coverage": coverage, "ks": ks}
    outcome = {"passed": not mismatches, "mismatches": mismatches, "recomputed": recomputed}
    (generated / "checker_output.json").write_text(json.dumps(outcome, indent=2), encoding="utf-8")
    print(json.dumps(outcome, indent=2))
    return 0 if outcome["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
