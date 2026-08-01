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


def ks_distance(values: list[float]) -> float:
    ordered = sorted(values)
    total = len(ordered)
    normal = NormalDist()
    return max(
        max((index + 1) / total - normal.cdf(value), normal.cdf(value) - index / total)
        for index, value in enumerate(ordered)
    )


def raw_rows():
    for path in sorted(HERE.glob("stopping_paths-part-*.csv")):
        with path.open(newline="", encoding="utf-8") as handle:
            yield from csv.DictReader(handle)


def compare_regenerated(failures: list[str]) -> None:
    candidates = [
        CANDIDATE.parent / ".openresearch" / "artifacts" / "claim_2" / "generated",
        CANDIDATE / ".generated" / "claim-2",
    ]
    for generated in candidates:
        if not generated.exists():
            continue
        regenerated_metrics = (generated / "stopping_clt_metrics.csv").read_text(encoding="utf-8").splitlines()
        committed_metrics = (HERE / "stopping_clt_metrics.csv").read_text(encoding="utf-8").splitlines()
        if regenerated_metrics != committed_metrics:
            failures.append(f"committed metrics differ from regenerated metrics at {generated}")
        committed = (
            (row[key] for key in row)
            for row in raw_rows()
        )
        with gzip.open(generated / "stopping_paths.csv.gz", "rt", newline="", encoding="utf-8") as handle:
            regenerated = csv.DictReader(handle)
            for index, (left, right) in enumerate(zip(committed, regenerated, strict=True)):
                if tuple(right.values()) != tuple(left):
                    failures.append(f"committed raw path differs from regenerated row {index}")
                    break


def main() -> int:
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    crossing_failures = 0
    raw_count = 0
    for row in raw_rows():
        raw_count += 1
        groups[(row["boundary"], row["alpha_label"])].append(float(row["z_standardized"]))
        if float(row["evidence_at_stop"]) + 1e-12 < float(row["threshold_at_stop"]):
            crossing_failures += 1
        if float(row["evidence_previous"]) >= float(row["threshold_previous"]) - 1e-12:
            crossing_failures += 1

    with (HERE / "stopping_clt_metrics.csv").open(newline="", encoding="utf-8") as handle:
        metrics = {(row["boundary"], row["alpha_label"]): row for row in csv.DictReader(handle)}

    failures: list[str] = []
    for key, values in groups.items():
        expected = metrics[key]
        checks = {
            "standardized_mean": statistics.fmean(values),
            "variance_ratio": statistics.variance(values),
            "gaussian_95_coverage": sum(abs(value) <= 1.959963984540054 for value in values) / len(values),
            "ks_distance": ks_distance(values),
        }
        for name, value in checks.items():
            if not math.isclose(value, float(expected[name]), rel_tol=0.0, abs_tol=2e-12):
                failures.append(f"{key}: {name} raw-data mismatch")

    p, m0 = 0.6, 0.2
    klinf = p * math.log(p / m0) + (1.0 - p) * math.log((1.0 - p) / (1.0 - m0))
    log_odds = math.log((p * (1.0 - m0)) / (m0 * (1.0 - p)))
    sigma2 = p * (1.0 - p) * log_odds * log_odds
    theory = json.loads((HERE / "theory.json").read_text(encoding="utf-8"))
    theory_checks = {
        "klinf": math.isclose(klinf, float(theory["klinf"]), rel_tol=0.0, abs_tol=2e-14),
        "sigma2": math.isclose(sigma2, float(theory["sigma2"]), rel_tol=0.0, abs_tol=2e-14),
        "sigma2_bd": math.isclose(sigma2 / klinf**3, float(theory["sigma2_bd"]), rel_tol=0.0, abs_tol=2e-12),
    }
    if not all(theory_checks.values()):
        failures.append("closed-form theory mismatch")
    if crossing_failures:
        failures.append(f"{crossing_failures} first-hit inequalities failed")
    if len(groups) != 16 or raw_count != 160000 or any(len(values) != 10000 for values in groups.values()):
        failures.append("raw path count mismatch")
    raw_manifest = json.loads((HERE / "raw_parts_manifest.json").read_text(encoding="utf-8"))
    for part in raw_manifest["parts"]:
        observed = hashlib.sha256((HERE / part["path"]).read_bytes()).hexdigest()
        if observed != part["sha256"]:
            failures.append(f"raw part hash mismatch: {part['path']}")
    compare_regenerated(failures)

    result = {
        "passed": not failures,
        "failures": failures,
        "crossing_failures": crossing_failures,
        "groups_checked": len(groups),
        "paths_checked": raw_count,
        "theory_checks": theory_checks,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
