from __future__ import annotations

import csv
import gzip
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from .claim1 import wilson_interval
from .klinf import binary_kl, binary_reference


def interval_gate(row: dict[str, Any]) -> tuple[bool, list[str]]:
    checks = {
        "coverage_95": float(row["coverage_95_wilson_low"]) <= 0.95 <= float(row["coverage_95_wilson_high"]),
        "coverage_50": float(row["coverage_50_wilson_low"]) <= 0.50 <= float(row["coverage_50_wilson_high"]),
        "vhat_mean": 0.97 <= float(row["vhat_ratio_mean"]) <= 1.03,
        "vhat_median": 0.97 <= float(row["vhat_ratio_median"]) <= 1.03,
        "center": abs(float(row["center_relative_error"])) <= 0.003,
    }
    return all(checks.values()), [name for name, passed in checks.items() if not passed]


def simulate_nested(
    *, p: float, m0: float, b_values: list[float], replicates: int, seed: int, max_n: int
) -> tuple[list[dict[str, np.ndarray]], int]:
    rng = np.random.default_rng(seed)
    counts = np.zeros(replicates, dtype=np.int64)
    previous_evidence = np.zeros(replicates)
    stopped = []
    for _ in b_values:
        stopped.append(
            {
                "tau": np.zeros(replicates, dtype=np.int64),
                "successes": np.zeros(replicates, dtype=np.int64),
                "evidence": np.zeros(replicates),
                "previous_evidence": np.zeros(replicates),
                "threshold": np.zeros(replicates),
                "previous_threshold": np.zeros(replicates),
            }
        )

    for n in range(1, max_n + 1):
        counts += rng.binomial(1, p, size=replicates)
        evidence = n * binary_kl(counts / n, m0)
        for index, b in enumerate(b_values):
            threshold = b + 1.0 + math.log(2.0 * (1.0 + n))
            new = (stopped[index]["tau"] == 0) & (evidence >= threshold)
            if np.any(new):
                stopped[index]["tau"][new] = n
                stopped[index]["successes"][new] = counts[new]
                stopped[index]["evidence"][new] = evidence[new]
                stopped[index]["previous_evidence"][new] = previous_evidence[new]
                stopped[index]["threshold"][new] = threshold
                stopped[index]["previous_threshold"][new] = b + 1.0 + math.log(2.0 * n)
        if all(np.all(cell["tau"] > 0) for cell in stopped):
            return stopped, n
        previous_evidence = evidence
    unresolved = [int(np.sum(cell["tau"] == 0)) for cell in stopped]
    raise RuntimeError(f"fixed max_n={max_n} reached; unresolved={unresolved}")


def plugin_values(successes: np.ndarray, tau: np.ndarray, m0: float) -> dict[str, np.ndarray]:
    p_hat = successes / tau
    k_hat = binary_kl(p_hat, m0)
    lambda_hat = (m0 - p_hat) / (m0 * (1.0 - m0))
    ell0 = np.log1p(lambda_hat * m0)
    ell1 = np.log1p(-lambda_hat * (1.0 - m0))
    sigma_hat2 = (1.0 - p_hat) * (ell0 - k_hat) ** 2 + p_hat * (ell1 - k_hat) ** 2
    v_hat = sigma_hat2 / k_hat**3
    return {
        "p_hat": p_hat,
        "k_hat": k_hat,
        "lambda_hat": lambda_hat,
        "sigma_hat2": sigma_hat2,
        "v_hat": v_hat,
        "wrong_v_hat": sigma_hat2 / k_hat**2,
    }


def run_claim(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    p = float(config["p"])
    m0 = float(config["m0"])
    b_values = [float(value) for value in config["b_values"]]
    labels = list(config["alpha_labels"])
    replicates = int(config["replicates"])
    seed = int(config["seed"])
    stopped, final_n = simulate_nested(
        p=p,
        m0=m0,
        b_values=b_values,
        replicates=replicates,
        seed=seed,
        max_n=int(config["max_n"]),
    )
    reference = binary_reference(p, m0)
    target = 1.0 / reference["klinf"]
    sigma2_bd = reference["sigma2"] / reference["klinf"] ** 3
    z95 = float(stats.norm.ppf(0.975))
    z50 = float(stats.norm.ppf(0.75))
    metrics: list[dict[str, Any]] = []
    raw_rows: list[tuple[Any, ...]] = []

    for index, (b, label, cell) in enumerate(zip(b_values, labels, stopped, strict=True)):
        tau = cell["tau"].astype(float)
        plugin = plugin_values(cell["successes"], tau, m0)
        center = tau / b
        se = np.sqrt(plugin["v_hat"] / b)
        lower95, upper95 = center - z95 * se, center + z95 * se
        lower50, upper50 = center - z50 * se, center + z50 * se
        cover95 = (lower95 <= target) & (target <= upper95)
        cover50 = (lower50 <= target) & (target <= upper50)
        wrong_se = np.sqrt(plugin["wrong_v_hat"] / b)
        wrong_cover95 = (center - z95 * wrong_se <= target) & (target <= center + z95 * wrong_se)
        low95, high95 = wilson_interval(int(np.sum(cover95)), replicates)
        low50, high50 = wilson_interval(int(np.sum(cover50)), replicates)
        relative_v_error = np.abs(plugin["v_hat"] / sigma2_bd - 1.0)
        metrics.append(
            {
                "alpha_label": label,
                "b": b,
                "replicates": replicates,
                "seed": seed,
                "mean_tau": float(np.mean(tau)),
                "mean_tau_over_b": float(np.mean(center)),
                "target_inverse_klinf": target,
                "center_relative_error": float((np.mean(center) - target) / target),
                "sigma2_bd": sigma2_bd,
                "sigma_hat2_ratio_mean": float(np.mean(plugin["sigma_hat2"]) / reference["sigma2"]),
                "vhat_ratio_mean": float(np.mean(plugin["v_hat"]) / sigma2_bd),
                "vhat_ratio_median": float(np.median(plugin["v_hat"]) / sigma2_bd),
                "vhat_relative_error_median": float(np.median(relative_v_error)),
                "vhat_relative_error_q90": float(np.quantile(relative_v_error, 0.90)),
                "coverage_95": float(np.mean(cover95)),
                "coverage_95_wilson_low": low95,
                "coverage_95_wilson_high": high95,
                "coverage_50": float(np.mean(cover50)),
                "coverage_50_wilson_low": low50,
                "coverage_50_wilson_high": high50,
                "mean_width_95": float(np.mean(upper95 - lower95)),
                "mean_width_50": float(np.mean(upper50 - lower50)),
                "wrong_power2_coverage_95": float(np.mean(wrong_cover95)),
                "literal_self_coverage_95": float(np.mean((lower95 <= center) & (center <= upper95))),
                "literal_self_coverage_50": float(np.mean((lower50 <= center) & (center <= upper50))),
                "min_p_hat": float(np.min(plugin["p_hat"])),
                "max_p_hat": float(np.max(plugin["p_hat"])),
            }
        )
        raw_rows.extend(
            (
                label,
                b,
                seed,
                path,
                int(cell["tau"][path]),
                int(cell["successes"][path]),
                float(cell["evidence"][path]),
                float(cell["previous_evidence"][path]),
                float(cell["threshold"][path]),
                float(cell["previous_threshold"][path]),
                float(plugin["p_hat"][path]),
                float(plugin["k_hat"][path]),
                float(plugin["lambda_hat"][path]),
                float(plugin["sigma_hat2"][path]),
                float(plugin["v_hat"][path]),
                target,
                float(center[path]),
                float(lower95[path]),
                float(upper95[path]),
                int(cover95[path]),
                float(lower50[path]),
                float(upper50[path]),
                int(cover50[path]),
            )
            for path in range(replicates)
        )

    with (output_dir / "single_run_ci_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)
    with (output_dir / "single_run_ci_paths.csv.gz").open("wb") as raw_handle:
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", mtime=0) as gzip_handle:
            header = (
                "alpha_label,b,seed,path,tau,successes,evidence_at_stop,evidence_previous,threshold_at_stop,"
                "threshold_previous,p_hat,k_hat,lambda_hat,sigma_hat2,v_hat,target,center,lower_95,upper_95,"
                "covers_95,lower_50,upper_50,covers_50\n"
            )
            lines = [header]
            lines.extend(
                f"{label},{b:.17g},{seed},{path},{tau},{successes},{evidence:.17g},{previous:.17g},"
                f"{threshold:.17g},{previous_threshold:.17g},{p_hat:.17g},{k_hat:.17g},{lambda_hat:.17g},"
                f"{sigma_hat2:.17g},{v_hat:.17g},{target_value:.17g},{center_value:.17g},{lower95:.17g},"
                f"{upper95:.17g},{cover95},{lower50:.17g},{upper50:.17g},{cover50}\n"
                for (
                    label,
                    b,
                    seed,
                    path,
                    tau,
                    successes,
                    evidence,
                    previous,
                    threshold,
                    previous_threshold,
                    p_hat,
                    k_hat,
                    lambda_hat,
                    sigma_hat2,
                    v_hat,
                    target_value,
                    center_value,
                    lower95,
                    upper95,
                    cover95,
                    lower50,
                    upper50,
                    cover50,
                ) in raw_rows
            )
            gzip_handle.write("".join(lines).encode("utf-8"))

    largest = metrics[-1]
    finite = metrics[0]
    finite_passed, finite_failures = interval_gate(finite)
    controls = {
        "finite_alpha_asymptotic_gate": {
            "expected": "FAIL",
            "observed": "PASS" if finite_passed else "FAIL",
            "failed_checks": finite_failures,
            "valid": not finite_passed,
        },
        "wrong_klinf_power": {
            "expected": "FAIL",
            "observed_coverage_95": largest["wrong_power2_coverage_95"],
            "observed": "PASS" if 0.94 <= float(largest["wrong_power2_coverage_95"]) <= 0.96 else "FAIL",
            "valid": not (0.94 <= float(largest["wrong_power2_coverage_95"]) <= 0.96),
        },
        "literal_stopping_time_target": {
            "expected": "FAIL",
            "reason": "An interval centered on the observed tau/b contains that same tau/b identically, so it cannot have nominal 1-gamma coverage for the random stopping time itself.",
            "observed_95": largest["literal_self_coverage_95"],
            "observed_50": largest["literal_self_coverage_50"],
            "observed": "FAIL",
            "valid": largest["literal_self_coverage_95"] == 1.0 and largest["literal_self_coverage_50"] == 1.0,
        },
    }
    theory = {**reference, "inverse_klinf": target, "sigma2_bd": sigma2_bd}
    diagnostics = {"final_n": final_n, "max_n": int(config["max_n"]), "nested_paths": True}
    (output_dir / "theory.json").write_text(json.dumps(theory, indent=2), encoding="utf-8")
    (output_dir / "run_diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    (output_dir / "negative_controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    return {"rows": metrics, "theory": theory, "controls": controls, "diagnostics": diagnostics}


def verify_result(result: dict[str, Any]) -> dict[str, Any]:
    rows = sorted(result["rows"], key=lambda row: float(row["b"]))
    largest = rows[-1]
    passed, failed_checks = interval_gate(largest)
    trends = {
        "vhat_median_error_improves": float(rows[-1]["vhat_relative_error_median"])
        < float(rows[-2]["vhat_relative_error_median"])
        < float(rows[0]["vhat_relative_error_median"]),
        "vhat_q90_error_improves": float(rows[-1]["vhat_relative_error_q90"])
        < float(rows[-2]["vhat_relative_error_q90"])
        < float(rows[0]["vhat_relative_error_q90"]),
        "coverage_95_improves": abs(float(rows[-1]["coverage_95"]) - 0.95)
        < abs(float(rows[0]["coverage_95"]) - 0.95),
        "coverage_50_improves": abs(float(rows[-1]["coverage_50"]) - 0.50)
        < abs(float(rows[0]["coverage_50"]) - 0.50),
    }
    failures = [f"largest-b gate failed: {failed_checks}"] if not passed else []
    failures.extend(name for name, ok in trends.items() if not ok)
    failures.extend(name for name, control in result["controls"].items() if not control["valid"])
    return {
        "status": "FALSIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "largest_b": largest,
        "trends": trends,
        "controls": result["controls"],
    }
