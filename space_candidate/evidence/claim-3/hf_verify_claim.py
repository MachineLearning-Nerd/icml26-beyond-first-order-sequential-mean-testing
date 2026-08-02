from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from reproduction.claim3 import verify_result


def main() -> int:
    generated = Path(__file__).parent / "generated"
    config = json.loads((ROOT / "reproduction" / "config.json").read_text(encoding="utf-8"))["claim_3"]
    with (generated / "decomposition_metrics.csv").open(newline="", encoding="utf-8") as handle:
        decomposition = list(csv.DictReader(handle))
    with (generated / "anscombe_metrics.csv").open(newline="", encoding="utf-8") as handle:
        anscombe = list(csv.DictReader(handle))
    result = {
        "decomposition": decomposition,
        "anscombe": anscombe,
        "controls": json.loads((generated / "negative_controls.json").read_text(encoding="utf-8")),
    }
    verdict = verify_result(result, config)
    (generated / "verifier_output.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
