from __future__ import annotations

import csv
import gzip
import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
from scipy import stats

from .klinf import beta_reference, binary_kl, binary_reference, empirical_klinf_batch


NORMAL = NormalDist()


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    rate = successes / total
    denominator = 1.0 + z * z / total
    center = (rate + z * z / (2.0 * total)) / denominator
    radius = z * math.sqrt(rate * (1.0 - rate) / total + z * z / (4.0 * total * total)) / denominator
    return center - radius, center + radius


def summarize(z: np.ndarray) -> dict[str, float]:
    successes = int(np.sum(np.abs(z) <= NORMAL.inv_cdf(0.975)))
    coverage_low, coverage_high = wilson_interval(successes, len(z))
    return {
        "replicates": int(len(z)),
        "standardized_mean": float(np.mean(z)),
        "variance_ratio": float(np.var(z, ddof=1)),
        "ks_distance": float(stats.kstest(z, "norm").statistic),
        "gaussian_95_coverage": successes / len(z),
        "coverage_wilson_low": coverage_low,
        "coverage_wilson_high": coverage_high,
        "skewness": float(stats.skew(z, bias=False)),
        "excess_kurtosis": float(stats.kurtosis(z, fisher=True, bias=False)),
    }


def large_n_gate(row: dict[str, Any]) -> tuple[bool, list[str]]:
    checks = {
        "variance_ratio": 0.9 <= float(row["variance_ratio"]) <= 1.1,
        "ks_distance": float(row["ks_distance"]) <= 0.04,
        "coverage_interval": float(row["coverage_wilson_low"]) <= 0.95 <= float(row["coverage_wilson_high"]),
        "standardized_mean": abs(float(row["standardized_mean"])) <= 0.05,
    }
    return all(checks.values()), [name for name, passed in checks.items() if not passed]


def run_claim(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    m0 = float(config["m0"])
    replicates = int(config["replicates"])
    sample_sizes = [int(value) for value in config["sample_sizes"]]
    beta_cfg = config["beta"]
    bern_cfg = config["bernoulli"]
    beta_ref = beta_reference(float(beta_cfg["a"]), float(beta_cfg["b"]), m0)
    bern_ref = binary_reference(float(bern_cfg["p"]), m0)

    rows: list[dict[str, Any]] = []
    raw_rows: list[tuple[str, int, int, float]] = []
    beta_rng = np.random.default_rng(int(beta_cfg["seed"]))
    bern_rng = np.random.default_rng(int(bern_cfg["seed"]))

    for n in sample_sizes:
        beta_samples = beta_rng.beta(float(beta_cfg["a"]), float(beta_cfg["b"]), size=(replicates, n))
        beta_values = empirical_klinf_batch(beta_samples, m0)
        beta_z = np.sqrt(n) * (beta_values - beta_ref["klinf"]) / math.sqrt(beta_ref["sigma2"])
        beta_row = {"distribution": "Beta(3,2)", "n": n, **summarize(beta_z)}
        rows.append(beta_row)
        raw_rows.extend(("Beta(3,2)", n, idx, float(value)) for idx, value in enumerate(beta_z))
        del beta_samples, beta_values

        successes = bern_rng.binomial(n, float(bern_cfg["p"]), size=replicates)
        bern_values = binary_kl(successes / n, m0)
        bern_z = np.sqrt(n) * (bern_values - bern_ref["klinf"]) / math.sqrt(bern_ref["sigma2"])
        bern_row = {"distribution": "Bernoulli(0.6)", "n": n, **summarize(bern_z)}
        rows.append(bern_row)
        raw_rows.extend(("Bernoulli(0.6)", n, idx, float(value)) for idx, value in enumerate(bern_z))

    metrics_path = output_dir / "fixed_clt_metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    raw_path = output_dir / "fixed_clt_replicates.csv.gz"
    with raw_path.open("wb") as raw_handle:
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", mtime=0) as gzip_handle:
            text = "distribution,n,replicate,z_standardized\n" + "".join(
                f'"{distribution}",{n},{idx},{value:.17g}\n' for distribution, n, idx, value in raw_rows
            )
            gzip_handle.write(text.encode("utf-8"))

    negative_row = next(row for row in rows if row["distribution"] == "Bernoulli(0.6)" and row["n"] == 50)
    negative_passed, negative_failures = large_n_gate(negative_row)
    control = {
        "control": "Apply the large-n Gaussian gate to the deliberately discrete Bernoulli n=50 cell",
        "expected": "FAIL",
        "observed": "PASS" if negative_passed else "FAIL",
        "failed_checks": negative_failures,
        "valid": not negative_passed,
    }
    (output_dir / "negative_control.json").write_text(json.dumps(control, indent=2), encoding="utf-8")
    theory = {"Beta(3,2)": beta_ref, "Bernoulli(0.6)": bern_ref}
    (output_dir / "theory.json").write_text(json.dumps(theory, indent=2), encoding="utf-8")
    return {"rows": rows, "theory": theory, "negative_control": control}


def verify_result(result: dict[str, Any]) -> dict[str, Any]:
    by_key = {(row["distribution"], int(row["n"])): row for row in result["rows"]}
    failures: list[str] = []
    details: dict[str, Any] = {}
    for distribution in ("Beta(3,2)", "Bernoulli(0.6)"):
        large = by_key[(distribution, 5000)]
        small = by_key[(distribution, 50)]
        passed, failed_checks = large_n_gate(large)
        trend = float(large["ks_distance"]) < float(small["ks_distance"])
        if not passed:
            failures.append(f"{distribution} n=5000 failed: {failed_checks}")
        if not trend:
            failures.append(f"{distribution} KS trend did not improve")
        details[distribution] = {"large_n_gate": passed, "failed_checks": failed_checks, "ks_trend": trend}
    if not result["negative_control"]["valid"]:
        failures.append("negative control unexpectedly passed")
    return {"status": "VERIFIED" if not failures else "BLOCKED", "passed": not failures, "failures": failures, "details": details}
