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
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    crossing_failures = 0
    with gzip.open(generated / "stopping_paths.csv.gz", "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups[(row["boundary"], row["alpha_label"])].append(float(row["z_standardized"]))
            if float(row["evidence_at_stop"]) + 1e-12 < float(row["threshold_at_stop"]):
                crossing_failures += 1
            if float(row["evidence_previous"]) >= float(row["threshold_previous"]) - 1e-12:
                crossing_failures += 1
    with (generated / "stopping_clt_metrics.csv").open(newline="", encoding="utf-8") as handle:
        metrics = {(row["boundary"], row["alpha_label"]): row for row in csv.DictReader(handle)}

    mismatches: list[str] = []
    recomputed = {}
    for key, values in groups.items():
        checks = {
            "mean": statistics.fmean(values),
            "variance": statistics.variance(values),
            "coverage": sum(abs(value) <= 1.959963984540054 for value in values) / len(values),
            "ks": ks_distance(values),
        }
        expected = metrics[key]
        expected_names = {
            "mean": "standardized_mean",
            "variance": "variance_ratio",
            "coverage": "gaussian_95_coverage",
            "ks": "ks_distance",
        }
        for name, value in checks.items():
            if not math.isclose(value, float(expected[expected_names[name]]), rel_tol=0.0, abs_tol=2e-12):
                mismatches.append(f"{key}: {name}")
        recomputed[str(key)] = checks

    p, m0 = 0.6, 0.2
    klinf = p * math.log(p / m0) + (1.0 - p) * math.log((1.0 - p) / (1.0 - m0))
    log_odds = math.log((p * (1.0 - m0)) / (m0 * (1.0 - p)))
    sigma2 = p * (1.0 - p) * log_odds * log_odds
    theory = json.loads((generated / "theory.json").read_text(encoding="utf-8"))
    theory_checks = {
        "klinf": math.isclose(klinf, float(theory["klinf"]), rel_tol=0.0, abs_tol=2e-14),
        "sigma2": math.isclose(sigma2, float(theory["sigma2"]), rel_tol=0.0, abs_tol=2e-14),
        "sigma2_bd": math.isclose(sigma2 / klinf**3, float(theory["sigma2_bd"]), rel_tol=0.0, abs_tol=2e-12),
    }
    if not all(theory_checks.values()):
        mismatches.append("closed-form theory mismatch")
    if crossing_failures:
        mismatches.append(f"{crossing_failures} first-hit inequalities failed")
    if len(groups) != 16 or any(len(values) != 10000 for values in groups.values()):
        mismatches.append("raw path count mismatch")

    outcome = {
        "passed": not mismatches,
        "mismatches": mismatches,
        "crossing_failures": crossing_failures,
        "groups_checked": len(groups),
        "paths_checked": sum(len(values) for values in groups.values()),
        "theory_checks": theory_checks,
        "recomputed": recomputed,
    }
    (generated / "checker_output.json").write_text(json.dumps(outcome, indent=2), encoding="utf-8")
    print(json.dumps(outcome, indent=2))
    return 0 if outcome["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
