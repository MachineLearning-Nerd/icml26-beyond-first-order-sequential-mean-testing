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

from .claim1 import run_claim


ROOT = Path(__file__).resolve().parents[1]
CLAIM_DIR = ROOT / ".openresearch" / "artifacts" / "claim_1"
GENERATED = CLAIM_DIR / "generated"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest() -> None:
    entries = []
    for path in sorted(CLAIM_DIR.rglob("*")):
        if path.is_file() and path.name not in {"artifact_manifest.json", "claim_1_bundle.zip"}:
            entries.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "sha256": sha256(path),
                    "bytes": path.stat().st_size,
                }
            )
    (GENERATED / "artifact_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")


def make_bundle() -> Path:
    bundle = GENERATED / "claim_1_bundle.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(CLAIM_DIR.rglob("*")):
            if not path.is_file() or path == bundle or "__pycache__" in path.parts:
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


def main() -> int:
    start = time.monotonic()
    config = json.loads((ROOT / "reproduction" / "config.json").read_text(encoding="utf-8"))
    GENERATED.mkdir(parents=True, exist_ok=True)
    result = run_claim(config["claim_1"], GENERATED)

    verifier = run_script(CLAIM_DIR / "verify_claim.py")
    checker = run_script(CLAIM_DIR / "independent_checker.py")
    (GENERATED / "verifier_console.txt").write_text(verifier.stdout, encoding="utf-8")
    (GENERATED / "checker_console.txt").write_text(checker.stdout, encoding="utf-8")
    elapsed = time.monotonic() - start
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    environment = {
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
        "runtime_seconds": elapsed,
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "seed_beta": config["claim_1"]["beta"]["seed"],
        "seed_bernoulli": config["claim_1"]["bernoulli"]["seed"],
        "fixed_command": "uv sync --frozen && .venv/bin/python -m reproduction.run",
    }
    (GENERATED / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")

    verifier_output = GENERATED / "verifier_output.json"
    if verifier_output.exists():
        verifier_json = json.loads(verifier_output.read_text(encoding="utf-8"))
    else:
        verifier_json = {"status": "BLOCKED", "failures": ["verifier produced no JSON output"]}
    large_rows = [row for row in result["rows"] if row["n"] == 5000]
    eval_text = "# EVAL\n\nVerdict: **{}**\n\n".format(verifier_json["status"])
    for row in large_rows:
        eval_text += (
            f"- {row['distribution']} at n=5000: variance ratio {row['variance_ratio']:.4f}, "
            f"KS {row['ks_distance']:.4f}, 95% coverage {row['gaussian_95_coverage']:.4f}, "
            f"standardized mean {row['standardized_mean']:.4f}.\n"
        )
    eval_text += (
        f"- Negative control: {result['negative_control']['observed']} as expected.\n"
        f"- Independent checker exit: {checker.returncode}.\n"
        f"- HF cpu-upgrade runtime: {elapsed:.3f} seconds; actual affinity: {environment['affinity_cpu_count']} CPUs.\n"
    )
    (GENERATED / "EVAL.md").write_text(eval_text, encoding="utf-8")
    write_manifest()

    passed = verifier.returncode == 0 and checker.returncode == 0
    summary = {
        "claim": 1,
        "status": verifier_json["status"] if passed else "BLOCKED",
        "verifier_exit": verifier.returncode,
        "checker_exit": checker.returncode,
        "negative_control": result["negative_control"],
        "runtime_seconds": elapsed,
        "actual_affinity_cpus": environment["affinity_cpu_count"],
        "large_n_metrics": large_rows,
    }
    print("EVAL_SUMMARY=" + json.dumps(summary, sort_keys=True))
    if not passed:
        print(verifier.stdout)
        print(checker.stdout)
        return 1

    bundle = make_bundle()
    payload = base64.b64encode(bundle.read_bytes()).decode("ascii")
    print(f"ARTIFACT_BUNDLE_BEGIN sha256={sha256(bundle)} bytes={bundle.stat().st_size}")
    for start_index in range(0, len(payload), 76):
        print(payload[start_index : start_index + 76])
    print("ARTIFACT_BUNDLE_END")
    print("FINAL_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
