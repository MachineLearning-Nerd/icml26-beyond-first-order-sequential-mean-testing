from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import optimize, stats


SOURCE_HASHES = {
    "BRPI0202.MZA": "7290aa7086bb99418352f7c8eb54bab0010e4b8bc7b99a87a20dcfe3dce5f444",
    "EBPL8501.MZA": "572585530ad42b0a8ea90715af4fbf7f05ab09db94a066e650f7671caaaebdd1",
    "FLSC8101.MZA": "1aa22571dee5318db5f9ae69b42fbaaa54fa430296310dc965effb077ed84728",
    "GAGR0201.MZA": "d33e562503709aaed5dbf495e293eb167064be6ef38094a13a490d72d1a4074c",
    "GHWA0401.MZA": "c788fa3fa4ef2cf9e21850a874f30d80c754165f5af66d5e906577a93668a1b6",
    "IBWA8301.MZA": "9c00471b872a49f278495a009a52022f21b85d3925c1edd105239c356b185f3d",
    "IUAF9901.MZA": "0efeae163cff0b094f817cd26cb261670c4d4ba6324c5cf5240b47824e830ded",
    "SIAZ9501.MZA": "664c831fda375b87baab2a770150e0903f762af842eb3e661f93580d2c2ba0d1",
    "SIAZ9601.MZA": "8ff454c2693e760f126da2412003d7d1b3246c15af935688bc0cc52c02769037",
    "UFGA8201.MZA": "a7133d0ca7db74136af183d5ed19d998902b11013273410cdd7cff95696279c3",
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def scalar_klinf(counts: np.ndarray, support: np.ndarray, m0: float) -> float:
    total = int(np.sum(counts))
    if total == 0:
        return 0.0
    mean = float(counts @ support / total)
    if math.isclose(mean, m0, rel_tol=0.0, abs_tol=1e-15):
        return 0.0
    transformed = 1.0 - support if mean > m0 else support
    target = 1.0 - m0 if mean > m0 else m0
    delta = transformed - target
    upper = np.nextafter(1.0 / (1.0 - target), 0.0)

    def equation(lam: float) -> float:
        return float(np.sum(counts * delta / (1.0 - lam * delta)) / total)

    root = upper if equation(upper) <= 0.0 else optimize.brentq(equation, 0.0, upper, xtol=1e-14, rtol=1e-14)
    return float(np.sum(counts * np.log1p(-root * delta)) / total)


def close(left: float, right: float, tolerance: float = 5e-9) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def main() -> int:
    claim_dir = Path(__file__).parent
    root = claim_dir.parents[1]
    generated = claim_dir
    failures: list[str] = []

    source_dir = root / "reproduction" / "data" / "dssat_maize"
    observed_hashes = {path.name: file_hash(path) for path in sorted(source_dir.glob("*.MZA"))}
    if observed_hashes != SOURCE_HASHES:
        failures.append("primary-source hash mismatch")

    with (generated / "dssat_public_maize_pool.csv").open(newline="", encoding="utf-8") as handle:
        pool_rows = list(csv.DictReader(handle))
    support = np.asarray([float(row["normalized_yield"]) for row in pool_rows])
    if len(pool_rows) != 44 or np.any((support < 0.0) | (support > 1.0)):
        failures.append("persisted pool does not contain 44 bounded observations")
    if not close(float(np.max([float(row["hwam_kg_ha"]) for row in pool_rows])), 12340.0):
        failures.append("unexpected HWAM normalization maximum")

    raw: dict[tuple[float, int], dict[str, object]] = {}
    events: dict[int, list[tuple[float, int]]] = {}
    with (generated / "dssat_bootstrap_paths.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            alpha = float(row["alpha"])
            path = int(row["path"])
            row["counts"] = json.loads(row.pop("counts_json"))
            raw[(alpha, path)] = row
            events.setdefault(int(row["tau"]), []).append((alpha, path))
    if len(raw) != 9000:
        failures.append(f"raw record count is {len(raw)}, expected 9000")

    replay_counts = np.zeros((3000, len(support)), dtype=np.int32)
    rng = np.random.default_rng(260604251)
    replayed = 0
    checked = 0
    for n in range(1, max(events, default=0) + 1):
        draws = rng.integers(0, len(support), size=3000)
        replay_counts[np.arange(3000), draws] += 1
        for alpha, path in events.get(n, []):
            stored = np.asarray(raw[(alpha, path)]["counts"], dtype=np.int32)
            if not np.array_equal(stored, replay_counts[path]):
                failures.append(f"seed replay mismatch alpha={alpha} path={path}")
                continue
            if int(raw[(alpha, path)]["last_draw"]) != int(draws[path]):
                failures.append(f"final draw mismatch alpha={alpha} path={path}")
                continue
            threshold = math.log(1.0 / alpha)
            evidence = n * scalar_klinf(stored, support, 0.5)
            prior = stored.copy()
            prior[int(draws[path])] -= 1
            previous = (n - 1) * scalar_klinf(prior, support, 0.5)
            if not close(evidence, float(raw[(alpha, path)]["evidence_at_stop"])) or evidence + 5e-9 < threshold:
                failures.append(f"at-stop evidence mismatch alpha={alpha} path={path}")
                continue
            if not close(previous, float(raw[(alpha, path)]["evidence_previous"])) or previous >= threshold + 5e-9:
                failures.append(f"previous evidence mismatch alpha={alpha} path={path}")
                continue
            replayed += 1
            checked += 1
    if replayed != 9000:
        failures.append(f"seed replay covered {replayed} records")

    for (alpha, path), row in raw.items():
        counts = np.asarray(row["counts"], dtype=np.int32)
        tau = int(row["tau"])
        if int(np.sum(counts)) != tau:
            failures.append(f"count total mismatch alpha={alpha} path={path}")
            continue

    with (generated / "dssat_bootstrap_metrics.csv").open(newline="", encoding="utf-8") as handle:
        metric_rows = list(csv.DictReader(handle))
    reference = json.loads((generated / "dssat_theory.json").read_text(encoding="utf-8"))
    for metric in metric_rows:
        alpha = float(metric["alpha"])
        tau = np.asarray([int(raw[(alpha, path)]["tau"]) for path in range(3000)], dtype=float)
        b = math.log(1.0 / alpha)
        z = math.sqrt(b) * (tau / b - float(reference["inverse_klinf"]))
        standardized = z / math.sqrt(float(reference["sigma2_bd"]))
        recomputed = {
            "standardized_mean": float(np.mean(standardized)),
            "variance_ratio": float(np.var(standardized, ddof=1)),
            "ks_distance": float(stats.kstest(standardized, "norm").statistic),
            "gaussian_95_coverage": float(np.mean(np.abs(standardized) <= 1.959963984540054)),
            "mean_tau": float(np.mean(tau)),
        }
        for name, value in recomputed.items():
            if not close(value, float(metric[name]), tolerance=2e-11):
                failures.append(f"aggregate mismatch alpha={alpha} metric={name}")

    nested_failures = sum(
        not (
            int(raw[(0.01, path)]["tau"])
            <= int(raw[(0.001, path)]["tau"])
            <= int(raw[(0.0001, path)]["tau"])
        )
        for path in range(3000)
    )
    if nested_failures:
        failures.append(f"{nested_failures} paths violate nested stopping times")

    result = {
        "passed": not failures,
        "failures": failures[:20],
        "source_files_hashed": len(observed_hashes),
        "pool_rows_checked": len(pool_rows),
        "raw_paths_checked": checked,
        "seed_replay_rows": replayed,
        "first_hit_inequalities_checked": checked,
        "aggregate_metrics_recomputed": len(metric_rows),
        "nested_stopping_failures": nested_failures,
        "independent_scalar_brent_solver": True,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
