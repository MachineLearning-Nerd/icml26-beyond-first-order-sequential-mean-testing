from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from .claim1 import run_claim as run_claim_1
from .claim2 import run_claim as run_claim_2
from .claim3 import run_claim as run_claim_3


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / ".openresearch" / "artifacts"
CLAIM_1 = ARTIFACTS / "claim_1"
CLAIM_2 = ARTIFACTS / "claim_2"
CLAIM_3 = ARTIFACTS / "claim_3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(claim_dir: Path) -> None:
    generated = claim_dir / "generated"
    entries = []
    for path in sorted(claim_dir.rglob("*")):
        if path.is_file() and path.name != "artifact_manifest.json":
            entries.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "sha256": sha256(path),
                    "bytes": path.stat().st_size,
                }
            )
    (generated / "artifact_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")


def make_bundle() -> Path:
    bundle = ARTIFACTS / "cumulative_evidence_bundle.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for claim_dir in (CLAIM_1, CLAIM_2, CLAIM_3):
            for path in sorted(claim_dir.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
    return bundle


def run_script(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, path.as_posix()],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def environment(config: dict, runtime: float, seeds: dict) -> dict:
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    return {
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "selected_backend": config["compute"]["backend"],
        "selected_flavor": config["compute"]["flavor"],
        "container_image": config["compute"]["image"],
        "estimated_cores": config["compute"]["estimated_cores"],
        "os_cpu_count": os.cpu_count(),
        "affinity_cpu_count": len(affinity) if affinity is not None else None,
        "affinity_cpus": affinity,
        "gpu_allowed": config["compute"]["gpu_allowed"],
        "runtime_seconds": runtime,
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "seeds": seeds,
        "fixed_command": "uv sync --frozen && .venv/bin/python -m reproduction.run",
    }


def main() -> int:
    total_start = time.monotonic()
    config = json.loads((ROOT / "reproduction" / "config.json").read_text(encoding="utf-8"))
    generated_1 = CLAIM_1 / "generated"
    generated_2 = CLAIM_2 / "generated"
    generated_3 = CLAIM_3 / "generated"
    generated_1.mkdir(parents=True, exist_ok=True)
    generated_2.mkdir(parents=True, exist_ok=True)
    generated_3.mkdir(parents=True, exist_ok=True)

    claim_1_start = time.monotonic()
    result_1 = run_claim_1(config["claim_1"], generated_1)
    verifier_1 = run_script(CLAIM_1 / "verify_claim.py")
    checker_1 = run_script(CLAIM_1 / "independent_checker.py")
    candidate_path_1 = ROOT / "space_candidate" / "evidence" / "claim-1" / "verify_claim.py"
    candidate_1 = run_script(candidate_path_1) if candidate_path_1.exists() else None
    claim_1_runtime = time.monotonic() - claim_1_start
    (generated_1 / "verifier_console.txt").write_text(verifier_1.stdout, encoding="utf-8")
    (generated_1 / "checker_console.txt").write_text(checker_1.stdout, encoding="utf-8")
    if candidate_1 is not None:
        (generated_1 / "candidate_verifier_console.txt").write_text(candidate_1.stdout, encoding="utf-8")
    env_1 = environment(
        config,
        claim_1_runtime,
        {"beta": config["claim_1"]["beta"]["seed"], "bernoulli": config["claim_1"]["bernoulli"]["seed"]},
    )
    (generated_1 / "environment.json").write_text(json.dumps(env_1, indent=2), encoding="utf-8")
    verifier_json_1 = json.loads((generated_1 / "verifier_output.json").read_text(encoding="utf-8"))
    large_rows_1 = [row for row in result_1["rows"] if row["n"] == 5000]
    eval_1 = "# EVAL\n\nVerdict: **{}**\n\n".format(verifier_json_1["status"])
    for row in large_rows_1:
        eval_1 += (
            f"- {row['distribution']} at n=5000: variance ratio {row['variance_ratio']:.4f}, "
            f"KS {row['ks_distance']:.4f}, coverage {row['gaussian_95_coverage']:.4f}, "
            f"standardized mean {row['standardized_mean']:.4f}.\n"
        )
    eval_1 += (
        f"- Negative control: {result_1['negative_control']['observed']} as expected.\n"
        f"- Verifier/checker/candidate exits: {verifier_1.returncode}/{checker_1.returncode}/"
        f"{candidate_1.returncode if candidate_1 is not None else 'NA'}.\n"
        f"- HF cpu-upgrade runtime: {claim_1_runtime:.3f}s; actual affinity: {env_1['affinity_cpu_count']} CPUs.\n"
    )
    (generated_1 / "EVAL.md").write_text(eval_1, encoding="utf-8")

    claim_2_start = time.monotonic()
    result_2 = run_claim_2(config["claim_2"], generated_2)
    verifier_2 = run_script(CLAIM_2 / "verify_claim.py")
    checker_2 = run_script(CLAIM_2 / "independent_checker.py")
    candidate_path_2 = ROOT / "space_candidate" / "evidence" / "claim-2" / "verify_claim.py"
    candidate_2 = run_script(candidate_path_2) if candidate_path_2.exists() else None
    claim_2_runtime = time.monotonic() - claim_2_start
    (generated_2 / "verifier_console.txt").write_text(verifier_2.stdout, encoding="utf-8")
    (generated_2 / "checker_console.txt").write_text(checker_2.stdout, encoding="utf-8")
    if candidate_2 is not None:
        (generated_2 / "candidate_verifier_console.txt").write_text(candidate_2.stdout, encoding="utf-8")
    env_2 = environment(
        config,
        claim_2_runtime,
        {label: config["claim_2"]["seed"] + index for index, label in enumerate(config["claim_2"]["alpha_labels"])},
    )
    env_2["b_values"] = config["claim_2"]["b_values"]
    env_2["fixed_safety_horizon"] = config["claim_2"]["max_n"]
    (generated_2 / "environment.json").write_text(json.dumps(env_2, indent=2), encoding="utf-8")
    verifier_json_2 = json.loads((generated_2 / "verifier_output.json").read_text(encoding="utf-8"))
    largest_2 = verifier_json_2["largest_b"]
    eval_2 = (
        f"# EVAL\n\nVerdict: **{verifier_json_2['status']}**\n\n"
        f"- Growing boundary at b=10000: variance ratio {float(largest_2['variance_ratio']):.4f}, "
        f"KS {float(largest_2['ks_distance']):.4f}, coverage {float(largest_2['gaussian_95_coverage']):.4f}, "
        f"standardized mean {float(largest_2['standardized_mean']):.4f}, relative centering error "
        f"{float(largest_2['centering_relative_error']):.5f}.\n"
        f"- Both negative controls: {[value['observed'] for value in result_2['controls'].values()]}.\n"
        f"- Verifier/checker/candidate exits: {verifier_2.returncode}/{checker_2.returncode}/"
        f"{candidate_2.returncode if candidate_2 is not None else 'NA'}.\n"
        f"- HF cpu-upgrade runtime: {claim_2_runtime:.3f}s; actual affinity: {env_2['affinity_cpu_count']} CPUs.\n"
    )
    (generated_2 / "EVAL.md").write_text(eval_2, encoding="utf-8")

    claim_3_start = time.monotonic()
    result_3 = run_claim_3(config["claim_3"], generated_3)
    verifier_3 = run_script(CLAIM_3 / "verify_claim.py")
    checker_3 = run_script(CLAIM_3 / "independent_checker.py")
    claim_3_runtime = time.monotonic() - claim_3_start
    (generated_3 / "verifier_console.txt").write_text(verifier_3.stdout, encoding="utf-8")
    (generated_3 / "checker_console.txt").write_text(checker_3.stdout, encoding="utf-8")
    env_3 = environment(
        config,
        claim_3_runtime,
        {
            "decomposition": config["claim_3"]["decomposition_seed"],
            "anscombe": [
                config["claim_3"]["anscombe_seed"] + index
                for index in range(len(config["claim_3"]["anscombe_centers"]))
            ],
        },
    )
    (generated_3 / "environment.json").write_text(json.dumps(env_3, indent=2), encoding="utf-8")
    verifier_json_3 = json.loads((generated_3 / "verifier_output.json").read_text(encoding="utf-8"))
    largest_3 = verifier_json_3["largest_decomposition"]
    narrow_3 = verifier_json_3["narrow_anscombe"]
    eval_3 = (
        f"# EVAL\n\nVerdict: **{verifier_json_3['status']}**\n\n"
        f"- At n=50000: T1 RMS {float(largest_3['t1_rms']):.6f}, T1/T2 RMS ratio "
        f"{float(largest_3['t1_to_t2_rms_ratio']):.6f}, full/T2 variance ratio "
        f"{float(largest_3['full_to_t2_variance_ratio']):.6f}, max identity error "
        f"{float(largest_3['max_identity_error']):.3e}.\n"
        f"- Anscombe delta=0.01 probabilities at n>=10000: "
        f"{[float(row['exceedance_probability']) for row in narrow_3]}; eta={config['claim_3']['eta']}.\n"
        f"- Negative controls: {[value['observed'] for value in result_3['controls'].values()]}.\n"
        f"- Verifier/checker exits: {verifier_3.returncode}/{checker_3.returncode}.\n"
        f"- HF cpu-upgrade runtime: {claim_3_runtime:.3f}s; actual affinity: {env_3['affinity_cpu_count']} CPUs.\n"
    )
    (generated_3 / "EVAL.md").write_text(eval_3, encoding="utf-8")
    write_manifest(CLAIM_1)
    write_manifest(CLAIM_2)
    write_manifest(CLAIM_3)

    candidate_exit_1 = candidate_1.returncode if candidate_1 is not None else None
    candidate_exit_2 = candidate_2.returncode if candidate_2 is not None else None
    passed_1 = verifier_1.returncode == 0 and checker_1.returncode == 0 and candidate_exit_1 in {None, 0}
    passed_2 = verifier_2.returncode == 0 and checker_2.returncode == 0 and candidate_exit_2 in {None, 0}
    passed_3 = verifier_3.returncode == 0 and checker_3.returncode == 0
    summary = {
        "claim_1": {
            "status": verifier_json_1["status"] if passed_1 else "BLOCKED",
            "verifier_exit": verifier_1.returncode,
            "checker_exit": checker_1.returncode,
            "candidate_verifier_exit": candidate_exit_1,
            "large_n_metrics": large_rows_1,
        },
        "claim_2": {
            "status": verifier_json_2["status"] if passed_2 else "BLOCKED",
            "verifier_exit": verifier_2.returncode,
            "checker_exit": checker_2.returncode,
            "candidate_verifier_exit": candidate_exit_2,
            "largest_b": largest_2,
            "trends": verifier_json_2["trends"],
            "controls": result_2["controls"],
            "runtime_seconds": claim_2_runtime,
        },
        "claim_3": {
            "status": verifier_json_3["status"] if passed_3 else "BLOCKED",
            "verifier_exit": verifier_3.returncode,
            "checker_exit": checker_3.returncode,
            "largest_decomposition": largest_3,
            "narrow_anscombe": narrow_3,
            "controls": result_3["controls"],
            "runtime_seconds": claim_3_runtime,
        },
        "actual_affinity_cpus": env_2["affinity_cpu_count"],
        "total_runtime_seconds": time.monotonic() - total_start,
    }
    print("EVAL_SUMMARY=" + json.dumps(summary, sort_keys=True))
    if not passed_1:
        print(verifier_1.stdout)
        print(checker_1.stdout)
        if candidate_1 is not None:
            print(candidate_1.stdout)
    if not passed_2:
        print(verifier_2.stdout)
        print(checker_2.stdout)
        if candidate_2 is not None:
            print(candidate_2.stdout)
    if not passed_3:
        print(verifier_3.stdout)
        print(checker_3.stdout)

    bundle = make_bundle()
    payload = base64.b64encode(bundle.read_bytes()).decode("ascii")
    print(f"ARTIFACT_BUNDLE_BEGIN sha256={sha256(bundle)} bytes={bundle.stat().st_size}")
    for start_index in range(0, len(payload), 76):
        print(payload[start_index : start_index + 76])
    print("ARTIFACT_BUNDLE_END")
    print("FINAL_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0 if passed_1 and passed_2 and passed_3 else 1


if __name__ == "__main__":
    sys.exit(main())
