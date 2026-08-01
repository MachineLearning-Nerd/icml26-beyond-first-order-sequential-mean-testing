from __future__ import annotations

import csv
import gzip
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .claim1 import wilson_interval
from .klinf import binary_kl, binary_reference, ell


def decomposition(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[tuple[Any, ...]]]:
    p = float(config["p"])
    m0 = float(config["m0"])
    replicates = int(config["decomposition_replicates"])
    reference = binary_reference(p, m0)
    lambda_star = reference["lambda_star"]
    ell_star = ell(lambda_star, np.array([0.0, 1.0]), m0)
    rng = np.random.default_rng(int(config["decomposition_seed"]))
    rows = []
    raw = []

    for n in config["decomposition_sizes"]:
        n = int(n)
        successes = rng.binomial(n, p, size=replicates)
        p_hat = successes / n
        empirical_at_hat = binary_kl(p_hat, m0)
        empirical_at_star = (1.0 - p_hat) * ell_star[0] + p_hat * ell_star[1]
        full = math.sqrt(n) * (binary_kl(p_hat, m0) - reference["klinf"])
        t1 = math.sqrt(n) * (empirical_at_hat - empirical_at_star)
        t2 = math.sqrt(n) * (empirical_at_star - reference["klinf"])
        wrong_lambda = lambda_star + 0.5
        wrong = math.sqrt(n) * (
            (1.0 - p_hat) * ell(wrong_lambda, 0.0, m0)
            + p_hat * ell(wrong_lambda, 1.0, m0)
            - empirical_at_star
        )
        identity_error = full - t1 - t2
        row = {
            "n": n,
            "replicates": replicates,
            "t1_rms": float(np.sqrt(np.mean(t1 * t1))),
            "t2_rms": float(np.sqrt(np.mean(t2 * t2))),
            "t1_to_t2_rms_ratio": float(np.sqrt(np.mean(t1 * t1)) / np.sqrt(np.mean(t2 * t2))),
            "full_variance": float(np.var(full, ddof=1)),
            "t2_variance": float(np.var(t2, ddof=1)),
            "full_to_t2_variance_ratio": float(np.var(full, ddof=1) / np.var(t2, ddof=1)),
            "max_identity_error": float(np.max(np.abs(identity_error))),
            "wrong_lambda_rms": float(np.sqrt(np.mean(wrong * wrong))),
        }
        rows.append(row)
        raw.extend(
            (n, int(config["decomposition_seed"]), path, int(successes[path]), float(full[path]), float(t1[path]), float(t2[path]), float(identity_error[path]), float(wrong[path]))
            for path in range(replicates)
        )
    return rows, raw


def anscombe_cell(
    *, p: float, m0: float, n: int, deltas: list[float], replicates: int, seed: int
) -> dict[float, np.ndarray]:
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
    if center is None:
        raise RuntimeError("Anscombe center was not evaluated")
    return {
        delta: np.maximum(np.abs(minima[index] - center), np.abs(maxima[index] - center))
        for index, delta in enumerate(deltas)
    }


def anscombe(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[tuple[Any, ...]]]:
    p = float(config["p"])
    m0 = float(config["m0"])
    replicates = int(config["anscombe_replicates"])
    deltas = [float(value) for value in config["anscombe_deltas"]]
    epsilon = float(config["epsilon"])
    rows = []
    raw = []
    for index, center in enumerate(config["anscombe_centers"]):
        n = int(center)
        seed = int(config["anscombe_seed"]) + index
        oscillations = anscombe_cell(p=p, m0=m0, n=n, deltas=deltas, replicates=replicates, seed=seed)
        for delta in deltas:
            values = oscillations[delta]
            exceedances = int(np.sum(values > epsilon))
            low, high = wilson_interval(exceedances, replicates)
            rows.append(
                {
                    "n": n,
                    "delta": delta,
                    "epsilon": epsilon,
                    "replicates": replicates,
                    "exceedances": exceedances,
                    "exceedance_probability": exceedances / replicates,
                    "wilson_low": low,
                    "wilson_high": high,
                    "mean_oscillation": float(np.mean(values)),
                    "q95_oscillation": float(np.quantile(values, 0.95)),
                    "max_oscillation": float(np.max(values)),
                    "seed": seed,
                }
            )
            raw.extend((n, delta, seed, path, float(value), int(value > epsilon)) for path, value in enumerate(values))
    return rows, raw


def run_claim(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    decomposition_rows, decomposition_raw = decomposition(config)
    anscombe_rows, anscombe_raw = anscombe(config)
    with (output_dir / "decomposition_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decomposition_rows[0]))
        writer.writeheader()
        writer.writerows(decomposition_rows)
    with (output_dir / "anscombe_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(anscombe_rows[0]))
        writer.writeheader()
        writer.writerows(anscombe_rows)
    with (output_dir / "claim3_raw.csv.gz").open("wb") as raw_handle:
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", mtime=0) as gzip_handle:
            text = "record_type,n,delta,seed,path,successes,full,t1,t2,identity_error,wrong_lambda,oscillation,exceeds_epsilon\n"
            text += "".join(
                f"decomposition,{n},,{seed},{path},{successes},{full:.17g},{t1:.17g},{t2:.17g},{error:.17g},{wrong:.17g},,\n"
                for n, seed, path, successes, full, t1, t2, error, wrong in decomposition_raw
            )
            text += "".join(
                f"anscombe,{n},{delta:.17g},{seed},{path},,,,,,,{oscillation:.17g},{exceeds}\n"
                for n, delta, seed, path, oscillation, exceeds in anscombe_raw
            )
            gzip_handle.write(text.encode("utf-8"))
    controls = {
        "wrong_dual_parameter": {
            "expected": "FAIL",
            "observed": "PASS" if decomposition_rows[-1]["wrong_lambda_rms"] <= 0.01 else "FAIL",
            "wrong_lambda_rms": decomposition_rows[-1]["wrong_lambda_rms"],
            "valid": decomposition_rows[-1]["wrong_lambda_rms"] > 0.01,
        },
        "wide_anscombe_window": {
            "expected": "FAIL",
            "observed": "PASS" if next(row for row in anscombe_rows if row["n"] == 50000 and row["delta"] == 0.2)["wilson_high"] < float(config["eta"]) else "FAIL",
            "exceedance_probability": next(row for row in anscombe_rows if row["n"] == 50000 and row["delta"] == 0.2)["exceedance_probability"],
            "valid": next(row for row in anscombe_rows if row["n"] == 50000 and row["delta"] == 0.2)["wilson_high"] >= float(config["eta"]),
        },
    }
    (output_dir / "negative_controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    return {"decomposition": decomposition_rows, "anscombe": anscombe_rows, "controls": controls}


def verify_result(result: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    decomposition_rows = sorted(result["decomposition"], key=lambda row: int(row["n"]))
    largest = decomposition_rows[-1]
    anscombe_rows = result["anscombe"]
    narrow = [row for row in anscombe_rows if int(row["n"]) >= 10000 and float(row["delta"]) == 0.01]
    nested = all(
        next(row for row in anscombe_rows if int(row["n"]) == n and float(row["delta"]) == smaller)["exceedance_probability"]
        <= next(row for row in anscombe_rows if int(row["n"]) == n and float(row["delta"]) == larger)["exceedance_probability"]
        for n in config["anscombe_centers"]
        for smaller, larger in zip(reversed(config["anscombe_deltas"][1:]), reversed(config["anscombe_deltas"][:-1]), strict=True)
    )
    checks = {
        "identity": float(largest["max_identity_error"]) <= 2e-12,
        "dual_remainder": float(largest["t1_rms"]) <= 0.01,
        "dual_relative": float(largest["t1_to_t2_rms_ratio"]) <= 0.02,
        "linear_variance": 0.98 <= float(largest["full_to_t2_variance_ratio"]) <= 1.02,
        "dual_remainder_trend": all(float(left["t1_rms"]) > float(right["t1_rms"]) for left, right in zip(decomposition_rows, decomposition_rows[1:], strict=True)),
        "anscombe_narrow_window": all(float(row["wilson_high"]) < float(config["eta"]) for row in narrow),
        "anscombe_nested_windows": nested,
    }
    failures = [name for name, passed in checks.items() if not passed]
    failures.extend(name for name, control in result["controls"].items() if not control["valid"])
    return {
        "status": "VERIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "checks": checks,
        "largest_decomposition": largest,
        "narrow_anscombe": narrow,
        "controls": result["controls"],
    }
