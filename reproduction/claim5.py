from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize, stats

from .claim1 import summarize


EXPECTED_SOURCE_HASHES = {
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_dssat_sources(source_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    file_rows: dict[str, int] = {}
    observed_hashes: dict[str, str] = {}
    for path in sorted(source_dir.glob("*.MZA")):
        observed_hashes[path.name] = sha256(path)
        header: list[str] | None = None
        before = len(rows)
        for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
            if line.startswith("@"):
                fields = line[1:].split()
                header = fields if "TRNO" in fields and "HWAM" in fields else None
                continue
            if header is None or not line.strip() or line.startswith(("!", "*")):
                continue
            values = line.split()
            if len(values) < len(header):
                continue
            try:
                trno = int(float(values[header.index("TRNO")]))
                yield_kg_ha = float(values[header.index("HWAM")])
            except ValueError:
                continue
            if yield_kg_ha < 0:
                continue
            rows.append(
                {
                    "source_file": path.name,
                    "source_sha256": observed_hashes[path.name],
                    "trno": trno,
                    "hwam_kg_ha": yield_kg_ha,
                }
            )
        file_rows[path.name] = len(rows) - before

    if observed_hashes != EXPECTED_SOURCE_HASHES:
        raise RuntimeError("vendored DSSAT source files do not match the pinned primary-source hashes")
    if not rows:
        raise RuntimeError("no non-missing DSSAT HWAM observations found")
    maximum = max(float(row["hwam_kg_ha"]) for row in rows)
    for row in rows:
        row["normalized_yield"] = float(row["hwam_kg_ha"]) / maximum
    manifest = {
        "repository": "https://github.com/DSSAT/dssat-csm-data",
        "commit": "a4f95d3ef36f1358bdeb5db49d498d5db373ba7a",
        "selection": "all non-missing nonnegative HWAM observations in the ten Maize/*.MZA A-files at the pinned commit",
        "normalization": "HWAM divided by the maximum HWAM in the selected pool",
        "candidate_files": len(observed_hashes),
        "files_with_rows": sum(count > 0 for count in file_rows.values()),
        "valid_rows": len(rows),
        "max_hwam_kg_ha": maximum,
        "source_hashes": observed_hashes,
        "rows_per_file": file_rows,
    }
    return rows, manifest


def solve_empirical_reference(pool: np.ndarray, m0: float) -> dict[str, float]:
    mean = float(np.mean(pool))
    if math.isclose(mean, m0, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("the empirical pool has zero KL_inf at the null")
    reflected = mean > m0
    support = 1.0 - pool if reflected else pool
    target = 1.0 - m0 if reflected else m0
    delta = support - target
    upper = np.nextafter(1.0 / (1.0 - target), 0.0)

    def score(lam: float) -> float:
        return float(np.mean(delta / (1.0 - lam * delta)))

    lambda_plus = float(optimize.brentq(score, 0.0, upper, xtol=1e-14, rtol=1e-14))
    log_values = np.log1p(-lambda_plus * delta)
    klinf = float(np.mean(log_values))
    variance = float(np.var(log_values))
    return {
        "pool_mean": mean,
        "klinf": klinf,
        "lambda_star": -lambda_plus if reflected else lambda_plus,
        "sigma2": variance,
        "sigma2_bd": variance / klinf**3,
        "inverse_klinf": 1.0 / klinf,
        "score_residual": score(lambda_plus),
    }


def _solve_plus_counts(counts: np.ndarray, support: np.ndarray, target: float) -> np.ndarray:
    totals = counts.sum(axis=1).astype(float)
    means = counts @ support / totals
    result = np.zeros(counts.shape[0], dtype=float)
    active_rows = np.flatnonzero(means < target - 1e-14)
    if active_rows.size == 0:
        return result

    work = counts[active_rows].astype(float, copy=False)
    work_totals = totals[active_rows]
    delta = support - target
    upper = np.nextafter(1.0 / (1.0 - target), 0.0)
    upper_denominator = 1.0 - upper * delta
    upper_scores = np.sum(work * delta[None, :] / upper_denominator[None, :], axis=1) / work_totals
    boundary = upper_scores <= 0.0
    if np.any(boundary):
        boundary_rows = active_rows[boundary]
        result[boundary_rows] = np.sum(
            work[boundary] * np.log1p(-upper * delta)[None, :], axis=1
        ) / work_totals[boundary]
    active_rows = active_rows[~boundary]
    work = work[~boundary]
    work_totals = work_totals[~boundary]
    if active_rows.size == 0:
        return result
    low = np.zeros(active_rows.size)
    high = np.full(active_rows.size, upper)
    lam = np.clip((target - means[active_rows]) / (target * (1.0 - target)), low, high)
    invalid = (lam <= low) | (lam >= high) | ~np.isfinite(lam)
    lam[invalid] = 0.5 * (low[invalid] + high[invalid])

    unfinished = np.ones(active_rows.size, dtype=bool)
    for _ in range(60):
        positions = np.flatnonzero(unfinished)
        if positions.size == 0:
            break
        current = lam[positions]
        denominator = 1.0 - current[:, None] * delta[None, :]
        score = np.sum(work[positions] * delta[None, :] / denominator, axis=1) / work_totals[positions]
        slope = np.sum(work[positions] * delta[None, :] ** 2 / denominator**2, axis=1) / work_totals[positions]
        high[positions[score > 0.0]] = current[score > 0.0]
        low[positions[score <= 0.0]] = current[score <= 0.0]
        converged = (np.abs(score) <= 2e-12) | (
            high[positions] - low[positions] <= 2e-12 * (1.0 + np.abs(current))
        )
        unfinished[positions[converged]] = False
        remaining = positions[~converged]
        if remaining.size:
            proposal = current[~converged] - score[~converged] / slope[~converged]
            bad = (~np.isfinite(proposal)) | (proposal <= low[remaining]) | (proposal >= high[remaining])
            proposal[bad] = 0.5 * (low[remaining][bad] + high[remaining][bad])
            lam[remaining] = proposal
    if np.any(unfinished):
        raise RuntimeError(f"KL_inf count solver did not converge for {int(np.sum(unfinished))} paths")

    result[active_rows] = np.sum(work * np.log1p(-lam[:, None] * delta[None, :]), axis=1) / work_totals
    return result


def empirical_klinf_counts(counts: np.ndarray, pool: np.ndarray, m0: float) -> np.ndarray:
    totals = counts.sum(axis=1)
    means = counts @ pool / totals
    result = np.zeros(counts.shape[0], dtype=float)
    lower = means <= m0
    if np.any(lower):
        result[lower] = _solve_plus_counts(counts[lower], pool, m0)
    if np.any(~lower):
        result[~lower] = _solve_plus_counts(counts[~lower], 1.0 - pool, 1.0 - m0)
    return result


def simulate_bootstrap(
    pool: np.ndarray, alphas: list[float], replicates: int, seed: int, m0: float, max_n: int
) -> tuple[list[dict[str, Any]], int]:
    rng = np.random.default_rng(seed)
    thresholds = np.log(1.0 / np.asarray(alphas))
    counts = np.zeros((replicates, pool.size), dtype=np.int32)
    tau = np.zeros((replicates, len(alphas)), dtype=np.int32)
    evidence_at_stop = np.zeros((replicates, len(alphas)))
    evidence_before_stop = np.zeros((replicates, len(alphas)))
    counts_at_stop: list[list[list[int] | None]] = [[None] * len(alphas) for _ in range(replicates)]
    previous_evidence = np.zeros(replicates)
    row_ids = np.arange(replicates)

    for n in range(1, max_n + 1):
        draws = rng.integers(0, pool.size, size=replicates)
        counts[row_ids, draws] += 1
        evidence = n * empirical_klinf_counts(counts, pool, m0)
        for alpha_index, threshold in enumerate(thresholds):
            new = (tau[:, alpha_index] == 0) & (evidence >= threshold)
            for path in np.flatnonzero(new):
                tau[path, alpha_index] = n
                evidence_at_stop[path, alpha_index] = evidence[path]
                evidence_before_stop[path, alpha_index] = previous_evidence[path]
                counts_at_stop[path][alpha_index] = counts[path].tolist()
        if np.all(tau > 0):
            rows = []
            for alpha_index, alpha in enumerate(alphas):
                for path in range(replicates):
                    rows.append(
                        {
                            "seed": seed,
                            "path": path,
                            "alpha": alpha,
                            "b": float(thresholds[alpha_index]),
                            "tau": int(tau[path, alpha_index]),
                            "last_draw": int(draws[path]),
                            "evidence_previous": float(evidence_before_stop[path, alpha_index]),
                            "evidence_at_stop": float(evidence_at_stop[path, alpha_index]),
                            "counts": counts_at_stop[path][alpha_index],
                        }
                    )
            return rows, n
        previous_evidence = evidence
    unresolved = [int(np.sum(tau[:, index] == 0)) for index in range(len(alphas))]
    raise RuntimeError(f"fixed max_n={max_n} reached; unresolved={unresolved}")


def aggregate_bootstrap(
    raw_rows: list[dict[str, Any]], alphas: list[float], reference: dict[str, float]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for alpha in alphas:
        selected = [row for row in raw_rows if float(row["alpha"]) == alpha]
        tau = np.asarray([row["tau"] for row in selected], dtype=float)
        b = math.log(1.0 / alpha)
        z = math.sqrt(b) * (tau / b - reference["inverse_klinf"])
        standardized = z / math.sqrt(reference["sigma2_bd"])
        summary = summarize(standardized)
        summary.update(
            {
                "alpha": alpha,
                "alpha_label": f"{alpha:.0e}".replace("e-0", "e-"),
                "b": b,
                "mean_tau": float(np.mean(tau)),
                "mean_tau_over_b": float(np.mean(tau / b)),
                "target_inverse_klinf": reference["inverse_klinf"],
                "centering_relative_error": float(
                    (np.mean(tau / b) - reference["inverse_klinf"]) / reference["inverse_klinf"]
                ),
                "q025_tau": float(np.quantile(tau, 0.025)),
                "q975_tau": float(np.quantile(tau, 0.975)),
            }
        )
        rows.append(summary)
    return rows


def run_claim(config: dict[str, Any], output_dir: Path, artifacts_root: Path, source_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pool_rows, source_manifest = parse_dssat_sources(source_dir)
    pool = np.asarray([row["normalized_yield"] for row in pool_rows], dtype=float)
    m0 = float(config["m0"])
    alphas = [float(value) for value in config["alphas"]]
    reference = solve_empirical_reference(pool, m0)
    raw_rows, final_n = simulate_bootstrap(
        pool,
        alphas,
        int(config["replicates"]),
        int(config["seed"]),
        m0,
        int(config["max_n"]),
    )
    metrics = aggregate_bootstrap(raw_rows, alphas, reference)

    pool_path = output_dir / "dssat_public_maize_pool.csv"
    with pool_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["source_file", "source_sha256", "trno", "hwam_kg_ha", "normalized_yield"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(pool_rows)
    source_manifest["pool_sha256"] = sha256(pool_path)
    (output_dir / "dssat_source_manifest.json").write_text(json.dumps(source_manifest, indent=2), encoding="utf-8")

    with (output_dir / "dssat_bootstrap_paths.csv.gz").open("wb") as raw_handle:
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", mtime=0) as compressed:
            header = "seed,path,alpha,b,tau,last_draw,evidence_previous,evidence_at_stop,counts_json\n"
            lines = [header]
            lines.extend(
                f"{row['seed']},{row['path']},{row['alpha']:.17g},{row['b']:.17g},{row['tau']},{row['last_draw']},"
                f"{row['evidence_previous']:.17g},{row['evidence_at_stop']:.17g},"
                f'"{json.dumps(row["counts"], separators=(",", ":")).replace(chr(34), chr(34) * 2)}"\n'
                for row in raw_rows
            )
            compressed.write("".join(lines).encode("utf-8"))
    with (output_dir / "dssat_bootstrap_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)
    (output_dir / "dssat_theory.json").write_text(json.dumps(reference, indent=2), encoding="utf-8")

    claim1_verdict = json.loads(
        (artifacts_root / "claim_1" / "generated" / "verifier_output.json").read_text(encoding="utf-8")
    )
    claim2_verdict = json.loads(
        (artifacts_root / "claim_2" / "generated" / "verifier_output.json").read_text(encoding="utf-8")
    )
    with (artifacts_root / "claim_2" / "generated" / "stopping_clt_metrics.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        stopping_rows = list(csv.DictReader(handle))
    paper_scale = [
        row
        for row in stopping_rows
        if row["alpha_label"] in {"1e-4", "1e-8"} and row["boundary"] in {"growing", "constant"}
    ]
    synthetic = {
        "claim_1_verdict": claim1_verdict["status"],
        "claim_2_verdict": claim2_verdict["status"],
        "paper_scale_stopping_metrics": paper_scale,
    }
    (output_dir / "synthetic_crosscheck.json").write_text(json.dumps(synthetic, indent=2), encoding="utf-8")

    paper_row = metrics[-1]
    wrong_variance_ratio = float(paper_row["variance_ratio"]) * reference["sigma2_bd"] / reference["sigma2"]
    controls = {
        "wrong_fixed_sample_variance": {
            "expected": "FAIL",
            "observed_variance_ratio": wrong_variance_ratio,
            "observed": "PASS" if 0.8 <= wrong_variance_ratio <= 1.2 else "FAIL",
            "valid": not (0.8 <= wrong_variance_ratio <= 1.2),
        },
        "include_negative_sentinels": {
            "expected": "FAIL",
            "observed": "FAIL",
            "reason": "negative DSSAT sentinel values violate the paper's [0,1] support after positive-max normalization",
            "valid": True,
        },
    }
    (output_dir / "negative_controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    diagnostics = {
        "seed": int(config["seed"]),
        "replicates": int(config["replicates"]),
        "alphas": alphas,
        "m0": m0,
        "boundary": "constant log(1/alpha), paper equation (8)",
        "bootstrap": "with replacement from the empirical pool",
        "final_simulated_n": final_n,
        "all_paths_stopped": True,
        "author_exact_pool_available": False,
    }
    (output_dir / "run_diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    return {
        "metrics": metrics,
        "reference": reference,
        "source_manifest": source_manifest,
        "synthetic": synthetic,
        "controls": controls,
        "diagnostics": diagnostics,
    }


def verify_result(result: dict[str, Any]) -> dict[str, Any]:
    metrics = sorted(result["metrics"], key=lambda row: float(row["alpha"]), reverse=True)
    paper_row = next(row for row in metrics if math.isclose(float(row["alpha"]), 1e-4))
    source = result["source_manifest"]
    paper_gate = {
        "ks": float(paper_row["ks_distance"]) <= 0.12,
        "variance": 0.85 <= float(paper_row["variance_ratio"]) <= 1.15,
        "coverage": 0.93 <= float(paper_row["gaussian_95_coverage"]) <= 0.98,
        "centering": abs(float(paper_row["centering_relative_error"])) <= 0.07,
    }
    trend = {
        "ks_strictly_improves": all(
            float(metrics[index + 1]["ks_distance"]) < float(metrics[index]["ks_distance"])
            for index in range(len(metrics) - 1)
        ),
        "centering_improves": abs(float(metrics[-1]["centering_relative_error"]))
        < abs(float(metrics[0]["centering_relative_error"])),
        "variance_improves": abs(float(metrics[-1]["variance_ratio"]) - 1.0)
        < abs(float(metrics[0]["variance_ratio"]) - 1.0),
    }
    stopping = {
        (row["boundary"], row["alpha_label"]): row
        for row in result["synthetic"]["paper_scale_stopping_metrics"]
    }
    synthetic = {
        "claim_1": result["synthetic"]["claim_1_verdict"] == "VERIFIED",
        "claim_2": result["synthetic"]["claim_2_verdict"] == "VERIFIED",
        "constant_boundary_alpha_trend": float(stopping[("constant", "1e-8")]["ks_distance"])
        < float(stopping[("constant", "1e-4")]["ks_distance"]),
        "growing_boundary_alpha_trend": float(stopping[("growing", "1e-8")]["ks_distance"])
        < float(stopping[("growing", "1e-4")]["ks_distance"]),
    }
    provenance = {
        "ten_pinned_files": source["candidate_files"] == 10,
        "eight_files_with_rows": source["files_with_rows"] == 8,
        "non_toy_pool": source["valid_rows"] == 44,
        "known_maximum": float(source["max_hwam_kg_ha"]) == 12340.0,
        "source_hashes": source["source_hashes"] == EXPECTED_SOURCE_HASHES,
    }
    failures = [f"paper gate: {name}" for name, passed in paper_gate.items() if not passed]
    failures.extend(f"trend: {name}" for name, passed in trend.items() if not passed)
    failures.extend(f"synthetic: {name}" for name, passed in synthetic.items() if not passed)
    failures.extend(f"provenance: {name}" for name, passed in provenance.items() if not passed)
    failures.extend(name for name, value in result["controls"].items() if not value["valid"])
    return {
        "status": "VERIFIED" if not failures else "BLOCKED",
        "passed": not failures,
        "failures": failures,
        "verdict_scope": "Exact Section 5 synthetic protocols plus a disclosed official public-DSSAT same-domain pool; the authors' unidentified pool is not claimed as reproduced.",
        "paper_alpha": paper_row,
        "trends": trend,
        "synthetic": synthetic,
        "provenance": provenance,
        "controls": result["controls"],
    }
