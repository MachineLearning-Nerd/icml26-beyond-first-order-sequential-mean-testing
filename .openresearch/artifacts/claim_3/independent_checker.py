from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def binary_kl(p: np.ndarray | float, m0: float) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        left = np.where(p == 0.0, 0.0, p * np.log(p / m0))
        right = np.where(p == 1.0, 0.0, (1.0 - p) * np.log((1.0 - p) / (1.0 - m0)))
    return left + right


def replay_anscombe(*, n: int, deltas: list[float], replicates: int, seed: int) -> dict[float, np.ndarray]:
    p, m0 = 0.6, 0.2
    rng = np.random.default_rng(seed)
    counts = np.zeros(replicates, dtype=np.int64)
    lower = np.array([math.ceil(n * (1.0 - delta)) for delta in deltas])
    upper = np.array([math.floor(n * (1.0 + delta)) for delta in deltas])
    minima = np.full((len(deltas), replicates), np.inf)
    maxima = np.full((len(deltas), replicates), -np.inf)
    reference = float(binary_kl(p, m0))
    center = None
    for k in range(1, int(np.max(upper)) + 1):
        counts += rng.binomial(1, p, size=replicates)
        y = math.sqrt(k) * (binary_kl(counts / k, m0) - reference)
        for index in range(len(deltas)):
            if lower[index] <= k <= upper[index]:
                minima[index] = np.minimum(minima[index], y)
                maxima[index] = np.maximum(maxima[index], y)
        if k == n:
            center = y.copy()
    return {
        delta: np.maximum(np.abs(minima[index] - center), np.abs(maxima[index] - center))
        for index, delta in enumerate(deltas)
    }


def main() -> int:
    generated = Path(__file__).parent / "generated"
    decomposition = []
    anscombe: dict[tuple[int, float], list[tuple[int, float, int]]] = defaultdict(list)
    with gzip.open(generated / "claim3_raw.csv.gz", "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["record_type"] == "decomposition":
                decomposition.append(row)
            else:
                anscombe[(int(row["n"]), float(row["delta"]))].append(
                    (int(row["path"]), float(row["oscillation"]), int(row["exceeds_epsilon"]))
                )

    failures = []
    p, m0 = 0.6, 0.2
    klinf = float(binary_kl(p, m0))
    lambda_star = (m0 - p) / (m0 * (1.0 - m0))
    ell0 = math.log1p(lambda_star * m0)
    ell1 = math.log1p(-lambda_star * (1.0 - m0))
    for row in decomposition:
        n = int(row["n"])
        p_hat = int(row["successes"]) / n
        empirical_hat = float(binary_kl(p_hat, m0))
        empirical_star = (1.0 - p_hat) * ell0 + p_hat * ell1
        expected = {
            "full": math.sqrt(n) * (float(binary_kl(p_hat, m0)) - klinf),
            "t1": math.sqrt(n) * (empirical_hat - empirical_star),
            "t2": math.sqrt(n) * (empirical_star - klinf),
        }
        for name, value in expected.items():
            if not math.isclose(value, float(row[name]), rel_tol=0.0, abs_tol=2e-12):
                failures.append(f"decomposition path mismatch: n={n} {name}")
                break

    deltas = [0.2, 0.1, 0.05, 0.02, 0.01]
    for index, n in enumerate([500, 2000, 10000, 50000]):
        replayed = replay_anscombe(n=n, deltas=deltas, replicates=5000, seed=260604231 + index)
        for delta in deltas:
            observed = sorted(anscombe[(n, delta)])
            if len(observed) != 5000:
                failures.append(f"Anscombe path count mismatch: n={n}, delta={delta}")
                continue
            for path, value, exceeds in observed:
                if not math.isclose(value, float(replayed[delta][path]), rel_tol=0.0, abs_tol=2e-12):
                    failures.append(f"Anscombe replay mismatch: n={n}, delta={delta}, path={path}")
                    break
                if exceeds != int(value > 0.35):
                    failures.append(f"Anscombe threshold mismatch: n={n}, delta={delta}, path={path}")
                    break

    nested_failures = 0
    for n in [500, 2000, 10000, 50000]:
        values = {delta: dict((path, value) for path, value, _ in anscombe[(n, delta)]) for delta in deltas}
        for path in range(5000):
            if any(values[smaller][path] > values[larger][path] + 2e-12 for smaller, larger in zip(deltas[1:], deltas[:-1], strict=True)):
                nested_failures += 1
    if nested_failures:
        failures.append(f"{nested_failures} paths violate nested-window monotonicity")
    result = {
        "passed": not failures,
        "failures": failures,
        "decomposition_paths_checked": len(decomposition),
        "anscombe_paths_checked": sum(len(values) for values in anscombe.values()),
        "anscombe_seed_replay": True,
        "nested_window_failures": nested_failures,
    }
    (generated / "checker_output.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
