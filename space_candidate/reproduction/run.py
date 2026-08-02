from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

from .claim1 import run_claim as run_claim_1
from .claim2 import run_claim as run_claim_2
from .claim3 import run_claim as run_claim_3
from .claim4 import run_claim as run_claim_4
from .claim5 import run_claim as run_claim_5


ROOT = Path(__file__).resolve().parents[1]


def run_verifier(claim: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, (ROOT / "evidence" / f"claim-{claim}" / "verify_claim.py").as_posix()],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    start = time.monotonic()
    config = json.loads((ROOT / "reproduction" / "config.json").read_text(encoding="utf-8"))
    generated_1 = ROOT / ".generated" / "claim-1"
    generated_2 = ROOT / ".generated" / "claim-2"
    generated_3 = ROOT / ".generated" / "claim-3"
    generated_4 = ROOT / ".generated" / "claim-4"
    generated_5 = ROOT / ".generated" / "claim-5"
    run_claim_1(config["claim_1"], generated_1)
    run_claim_2(config["claim_2"], generated_2)
    run_claim_3(config["claim_3"], generated_3)
    run_claim_4(config["claim_4"], generated_4)
    run_claim_5(
        config["claim_5"],
        generated_5,
        ROOT / "evidence",
        ROOT / "reproduction" / "data" / "dssat_maize",
    )

    results = {}
    passed = True
    for claim in (1, 2, 3, 4, 5):
        verifier = run_verifier(claim)
        results[f"claim_{claim}"] = {
            "exit": verifier.returncode,
            "output": verifier.stdout,
        }
        passed = passed and verifier.returncode == 0

    notebook = subprocess.run(
        [sys.executable, "-m", "marimo", "check", "notebooks/sequential_mean_testing.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    release_gate = subprocess.run(
        [sys.executable, (ROOT / "evidence/release/verify_release.py").as_posix()],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    passed = passed and notebook.returncode == 0 and release_gate.returncode == 0

    summary = {
        "status": "VERIFIED" if passed else "BLOCKED",
        "fixed_command": "uv sync --frozen && .venv/bin/python -m reproduction.run",
        "backend": config["compute"]["backend"],
        "flavor": config["compute"]["flavor"],
        "gpu_allowed": config["compute"]["gpu_allowed"],
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "runtime_seconds": time.monotonic() - start,
        "claims": results,
        "marimo_check": {"exit": notebook.returncode, "output": notebook.stdout},
        "release_gate": {"exit": release_gate.returncode, "output": release_gate.stdout},
    }
    print("CANDIDATE_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
