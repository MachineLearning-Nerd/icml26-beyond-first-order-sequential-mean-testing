from __future__ import annotations

import csv
import gzip
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from .claim1 import summarize
from .klinf import binary_kl, binary_reference


def large_b_gate(row: dict[str, Any]) -> tuple[bool, list[str]]:
    checks = {
        "variance_ci": float(row["variance_ratio_ci_low"]) <= 1.0 <= float(row["variance_ratio_ci_high"]),
        "ks_distance": float(row["ks_distance"]) <= 0.05,
        "standardized_mean": abs(float(row["standardized_mean"])) <= 0.12,
        "centering_relative_error": abs(float(row["centering_relative_error"])) <= 0.003,
        "skewness": abs(float(row["skewness"])) <= 0.12,
        "excess_kurtosis": abs(float(row["excess_kurtosis"])) <= 0.12,
        "coverage": 0.94 <= float(row["gaussian_95_coverage"]) <= 0.96,
    }
    return all(checks.values()), [name for name, passed in checks.items() if not passed]


def simulate_cell(
    *, p: float, m0: float, b: float, replicates: int, seed: int, max_n: int
) -> tuple[dict[str, dict[str, np.ndarray]], int]:
    rng = np.random.default_rng(seed)
    counts = np.zeros(replicates, dtype=np.int64)
    previous_evidence = np.zeros(replicates)
    names = ("growing", "constant")
    fields = ("tau", "successes", "evidence", "previous_evidence", "threshold", "previous_threshold")
    stopped = {name: {field: np.zeros(replicates) for field in fields} for name in names}
    stopped["growing"]["tau"] = np.zeros(replicates, dtype=np.int64)
    stopped["growing"]["successes"] = np.zeros(replicates, dtype=np.int64)
    stopped["constant"]["tau"] = np.zeros(replicates, dtype=np.int64)
    stopped["constant"]["successes"] = np.zeros(replicates, dtype=np.int64)

    for n in range(1, max_n + 1):
        counts += rng.binomial(1, p, size=replicates)
        empirical_k = binary_kl(counts / n, m0)
        evidence = n * empirical_k
        thresholds = {"growing": b + 1.0 + math.log(2.0 * (1.0 + n)), "constant": b}
        previous_thresholds = {"growing": b + 1.0 + math.log(2.0 * n), "constant": b}
        for name in names:
            new = (stopped[name]["tau"] == 0) & (evidence >= thresholds[name])
            if np.any(new):
                stopped[name]["tau"][new] = n
                stopped[name]["successes"][new] = counts[new]
                stopped[name]["evidence"][new] = evidence[new]
                stopped[name]["previous_evidence"][new] = previous_evidence[new]
                stopped[name]["threshold"][new] = thresholds[name]
                stopped[name]["previous_threshold"][new] = previous_thresholds[name]
        if all(np.all(stopped[name]["tau"] > 0) for name in names):
            return stopped, n
        previous_evidence = evidence
    unresolved = {name: int(np.sum(stopped[name]["tau"] == 0)) for name in names}
    raise RuntimeError(f"fixed max_n={max_n} reached; unresolved={unresolved}")


def run_claim(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    p = float(config["p"])
    m0 = float(config["m0"])
    replicates = int(config["replicates"])
    max_n = int(config["max_n"])
    reference = binary_reference(p, m0)
    center = 1.0 / reference["klinf"]
    sigma2_bd = reference["sigma2"] / reference["klinf"] ** 3
    rows: list[dict[str, Any]] = []
    raw_rows: list[tuple[Any, ...]] = []
    diagnostics: list[dict[str, Any]] = []

    for index, (b_value, label) in enumerate(zip(config["b_values"], config["alpha_labels"], strict=True)):
        b = float(b_value)
        stopped, final_n = simulate_cell(
            p=p,
            m0=m0,
            b=b,
            replicates=replicates,
            seed=int(config["seed"]) + index,
            max_n=max_n,
        )
        diagnostics.append({"b": b, "alpha_label": label, "seed": int(config["seed"]) + index, "final_n": final_n})
        for boundary in ("growing", "constant"):
            values = stopped[boundary]
            tau = values["tau"].astype(float)
            z = math.sqrt(b) * (tau / b - center)
            z_standardized = z / math.sqrt(sigma2_bd)
            summary = summarize(z_standardized)
            variance = float(summary["variance_ratio"])
            degrees = replicates - 1
            summary.update(
                {
                    "boundary": boundary,
                    "b": b,
                    "alpha_label": label,
                    "mean_tau": float(np.mean(tau)),
                    "mean_tau_over_b": float(np.mean(tau / b)),
                    "inverse_klinf": center,
                    "centering_relative_error": float((np.mean(tau / b) - center) / center),
                    "variance_ratio_ci_low": float(degrees * variance / stats.chi2.ppf(0.975, degrees)),
                    "variance_ratio_ci_high": float(degrees * variance / stats.chi2.ppf(0.025, degrees)),
                    "mean_overshoot": float(np.mean(values["evidence"] - values["threshold"])),
                    "q99_tau": float(np.quantile(tau, 0.99)),
                }
            )
            rows.append(summary)
            for path in range(replicates):
                raw_rows.append(
                    (
                        boundary,
                        label,
                        b,
                        int(config["seed"]) + index,
                        path,
                        int(values["tau"][path]),
                        int(values["successes"][path]),
                        float(values["evidence"][path]),
                        float(values["previous_evidence"][path]),
                        float(values["threshold"][path]),
                        float(values["previous_threshold"][path]),
                        float(z_standardized[path]),
                    )
                )

    with (output_dir / "stopping_clt_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (output_dir / "stopping_paths.csv.gz").open("wb") as raw_handle:
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", mtime=0) as gzip_handle:
            header = "boundary,alpha_label,b,seed,path,tau,successes,evidence_at_stop,evidence_previous,threshold_at_stop,threshold_previous,z_standardized\n"
            lines = [header]
            lines.extend(
                f"{boundary},{label},{b:.17g},{seed},{path},{tau},{successes},{evidence:.17g},{previous:.17g},{threshold:.17g},{previous_threshold:.17g},{z:.17g}\n"
                for boundary, label, b, seed, path, tau, successes, evidence, previous, threshold, previous_threshold, z in raw_rows
            )
            gzip_handle.write("".join(lines).encode("utf-8"))

    largest = next(row for row in rows if row["boundary"] == "growing" and row["b"] == 10000.0)
    finite = next(row for row in rows if row["boundary"] == "growing" and row["alpha_label"] == "1e-4")
    finite_passed, finite_failures = large_b_gate(finite)
    wrong_variance_ratio = float(largest["variance_ratio"]) * sigma2_bd / reference["sigma2"]
    controls = {
        "finite_b_large_scale_gate": {
            "expected": "FAIL",
            "observed": "PASS" if finite_passed else "FAIL",
            "failed_checks": finite_failures,
            "valid": not finite_passed,
        },
        "wrong_fixed_sample_variance": {
            "expected": "FAIL",
            "observed_variance_ratio": wrong_variance_ratio,
            "observed": "PASS" if 0.9 <= wrong_variance_ratio <= 1.1 else "FAIL",
            "valid": not (0.9 <= wrong_variance_ratio <= 1.1),
        },
    }
    (output_dir / "negative_controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    theory = {**reference, "inverse_klinf": center, "sigma2_bd": sigma2_bd}
    (output_dir / "theory.json").write_text(json.dumps(theory, indent=2), encoding="utf-8")
    (output_dir / "run_diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    return {"rows": rows, "theory": theory, "controls": controls, "diagnostics": diagnostics}


def verify_result(result: dict[str, Any]) -> dict[str, Any]:
    growing = sorted(
        (row for row in result["rows"] if row["boundary"] == "growing"),
        key=lambda row: float(row["b"]),
    )
    largest = growing[-1]
    passed, failed_checks = large_b_gate(largest)
    trends = {
        "ks_improves": float(growing[-1]["ks_distance"]) < float(growing[-2]["ks_distance"]) < float(growing[0]["ks_distance"]),
        "centering_improves": abs(float(growing[-1]["centering_relative_error"])) < abs(float(growing[-2]["centering_relative_error"])) < abs(float(growing[0]["centering_relative_error"])),
        "variance_improves": abs(float(growing[-1]["variance_ratio"]) - 1.0) < abs(float(growing[0]["variance_ratio"]) - 1.0),
    }
    failures = [f"largest-b gate failed: {failed_checks}"] if not passed else []
    failures.extend(name for name, ok in trends.items() if not ok)
    failures.extend(name for name, control in result["controls"].items() if not control["valid"])
    return {
        "status": "VERIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "largest_b": largest,
        "trends": trends,
        "controls": result["controls"],
    }
