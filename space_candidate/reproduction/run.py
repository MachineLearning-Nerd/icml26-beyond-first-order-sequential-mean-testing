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
    run_claim_1(config["claim_1"], generated_1)
    run_claim_2(config["claim_2"], generated_2)
    run_claim_3(config["claim_3"], generated_3)

    results = {}
    passed = True
    for claim in (1, 2, 3):
        verifier = run_verifier(claim)
        results[f"claim_{claim}"] = {
            "exit": verifier.returncode,
            "output": verifier.stdout,
        }
        passed = passed and verifier.returncode == 0

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
    }
    print("CANDIDATE_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
