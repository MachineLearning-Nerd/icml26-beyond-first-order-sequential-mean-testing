from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np


def binary_kl(p: np.ndarray | float, m0: float) -> np.ndarray:
    values = np.asarray(p, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        left = np.where(values == 0.0, 0.0, values * np.log(values / m0))
        right = np.where(values == 1.0, 0.0, (1.0 - values) * np.log((1.0 - values) / (1.0 - m0)))
    return left + right


def replay_stops(replicates: int) -> tuple[list[np.ndarray], list[np.ndarray], int]:
    p, m0, seed = 0.6, 0.2, 260604241
    b_values = [147.36544595161894, 589.4617838064758, 2357.8471352259027, 10000.0]
    rng = np.random.default_rng(seed)
    counts = np.zeros(replicates, dtype=np.int64)
    taus = [np.zeros(replicates, dtype=np.int64) for _ in b_values]
    successes = [np.zeros(replicates, dtype=np.int64) for _ in b_values]
    for n in range(1, 500001):
        counts += rng.binomial(1, p, size=replicates)
        evidence = n * binary_kl(counts / n, m0)
        for index, b in enumerate(b_values):
            new = (taus[index] == 0) & (evidence >= b + 1.0 + math.log(2.0 * (1.0 + n)))
            taus[index][new] = n
            successes[index][new] = counts[new]
        if all(np.all(values > 0) for values in taus):
            return taus, successes, n
    raise RuntimeError("independent replay hit the fixed safety horizon")


def close(left: float, right: float, tolerance: float = 3e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def main() -> int:
    generated = Path(__file__).parent / "generated"
    labels = ["1e-64", "1e-256", "1e-1024", "exp(-10000)"]
    b_values = [147.36544595161894, 589.4617838064758, 2357.8471352259027, 10000.0]
    raw: dict[tuple[str, int], dict[str, str]] = {}
    with gzip.open(generated / "single_run_ci_paths.csv.gz", "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            raw[(row["alpha_label"], int(row["path"]))] = row
    failures: list[str] = []
    if len(raw) != 40000:
        failures.append(f"raw record count is {len(raw)}, expected 40000")

    taus, successes, replay_final_n = replay_stops(10000)
    p, m0 = 0.6, 0.2
    true_k = float(binary_kl(p, m0))
    true_target = 1.0 / true_k
    z95, z50 = 1.959963984540054, 0.6744897501960817
    checked = 0
    nesting_failures = 0
    self_coverage_failures = 0
    for path in range(10000):
        if any(taus[index][path] > taus[index + 1][path] for index in range(3)):
            nesting_failures += 1
        for index, (label, b) in enumerate(zip(labels, b_values, strict=True)):
            row = raw.get((label, path))
            if row is None:
                failures.append(f"missing raw row {label}/{path}")
                continue
            tau = int(row["tau"])
            success = int(row["successes"])
            if tau != int(taus[index][path]) or success != int(successes[index][path]):
                failures.append(f"seed replay mismatch {label}/{path}")
                continue
            empirical = float(tau * binary_kl(success / tau, m0))
            threshold = b + 1.0 + math.log(2.0 * (1.0 + tau))
            if not close(empirical, float(row["evidence_at_stop"])) or not close(threshold, float(row["threshold_at_stop"])):
                failures.append(f"stopping evidence mismatch {label}/{path}")
                continue
            if empirical + 2e-12 < threshold or float(row["evidence_previous"]) >= float(row["threshold_previous"]) + 2e-12:
                failures.append(f"first-hit inequality mismatch {label}/{path}")
                continue

            p_hat = success / tau
            k_hat = float(binary_kl(p_hat, m0))
            lambda_hat = (m0 - p_hat) / (m0 * (1.0 - m0))
            ell0 = math.log1p(lambda_hat * m0)
            ell1 = math.log1p(-lambda_hat * (1.0 - m0))
            sigma_hat2 = (1.0 - p_hat) * (ell0 - k_hat) ** 2 + p_hat * (ell1 - k_hat) ** 2
            v_hat = sigma_hat2 / k_hat**3
            center = tau / b
            se = math.sqrt(v_hat / b)
            expected = {
                "p_hat": p_hat,
                "k_hat": k_hat,
                "lambda_hat": lambda_hat,
                "sigma_hat2": sigma_hat2,
                "v_hat": v_hat,
                "target": true_target,
                "center": center,
                "lower_95": center - z95 * se,
                "upper_95": center + z95 * se,
                "lower_50": center - z50 * se,
                "upper_50": center + z50 * se,
            }
            mismatch = next(
                (name for name, value in expected.items() if not close(value, float(row[name]))),
                None,
            )
            if mismatch is not None:
                failures.append(f"plug-in mismatch {label}/{path}/{mismatch}")
                continue
            expected_cover95 = int(expected["lower_95"] <= true_target <= expected["upper_95"])
            expected_cover50 = int(expected["lower_50"] <= true_target <= expected["upper_50"])
            if int(row["covers_95"]) != expected_cover95 or int(row["covers_50"]) != expected_cover50:
                failures.append(f"coverage mismatch {label}/{path}")
                continue
            if not (
                expected["lower_95"] <= center <= expected["upper_95"]
                and expected["lower_50"] <= center <= expected["upper_50"]
            ):
                self_coverage_failures += 1
            checked += 1

    if nesting_failures:
        failures.append(f"{nesting_failures} paths violate nested stopping times")
    if self_coverage_failures:
        failures.append(f"{self_coverage_failures} intervals fail to contain their own center")
    result = {
        "passed": not failures,
        "failures": failures[:20],
        "raw_paths_checked": checked,
        "expected_raw_paths": 40000,
        "seed_replay": True,
        "replay_final_n": replay_final_n,
        "nested_stopping_failures": nesting_failures,
        "first_hit_checked": True,
        "same_path_plugin_recomputed": True,
        "literal_stopping_time_self_coverage": 1.0 if not self_coverage_failures else None,
    }
    (generated / "checker_output.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
