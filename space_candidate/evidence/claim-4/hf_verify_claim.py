from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from reproduction.claim4 import verify_result


def main() -> int:
    generated = Path(__file__).parent / "generated"
    with (generated / "single_run_ci_metrics.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = {
        "rows": rows,
        "theory": json.loads((generated / "theory.json").read_text(encoding="utf-8")),
        "controls": json.loads((generated / "negative_controls.json").read_text(encoding="utf-8")),
    }
    verdict = verify_result(result)
    (generated / "verifier_output.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
