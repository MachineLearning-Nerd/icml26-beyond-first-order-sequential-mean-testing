from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".generated" / "release"


CLAIM_FILES = {
    1: ["claim_contract.json", "source_audit.md", "method.md", "limitations.md", "fixed_clt_replicates.csv", "independent_checker.py", "checker_output.json", "negative_control.json", "environment.json", "verify_claim.py"],
    2: ["claim_contract.json", "source_audit.md", "method.md", "limitations.md", "stopping_clt_metrics.csv", "raw_parts_manifest.json", "independent_checker.py", "checker_output.json", "negative_controls.json", "environment.json", "verify_claim.py"],
    3: ["claim_contract.json", "source_audit.md", "method.md", "limitations.md", "decomposition_metrics.csv", "anscombe_metrics.csv", "raw_parts_manifest.json", "independent_checker.py", "checker_output.json", "negative_controls.json", "environment.json", "verify_claim.py"],
    4: ["claim_contract.json", "source_audit.md", "method.md", "limitations.md", "single_run_ci_metrics.csv", "raw_parts_manifest.json", "independent_checker.py", "checker_output.json", "negative_controls.json", "environment.json", "verify_claim.py"],
    5: ["claim_contract.json", "source_audit.md", "method.md", "limitations.md", "dssat_bootstrap_metrics.csv", "dssat_bootstrap_paths.csv", "dssat_public_maize_pool.csv", "dssat_source_manifest.json", "independent_checker.py", "checker_output.json", "negative_controls.json", "environment.json", "verify_claim.py"],
}


FIGURE_HASHES = {
    "headline.svg": "ca7a8b30317e7b4025c448c36182b8ec19fa7228a961bc8c551be5aef3c8c9c9",
    "claim2-convergence.svg": "e337b69365c7ae64be046b0de6ceee10f917addb928aa918679c2977d422e937",
    "claim3-decomposition.svg": "5a5e23c0c602eec83ef26ab28fff06d7f00d17db47fcf0646047ca7e76e1e6a5",
    "claim4-coverage.svg": "de2ecd59f6913c6cadaefde82d85d5dc987fcbc6ef0a5a097e62f016f92af225",
    "claim5-dssat.svg": "9e18df84023e8b8d4466409b60d09382691e21c4b42764af3562226b7a90a693",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(checks: list[dict[str, object]], name: str, passed: bool, detail: object) -> None:
    checks.append({"name": name, "passed": passed, "detail": detail})


def main() -> int:
    checks: list[dict[str, object]] = []
    logbook = json.loads((ROOT / "logbook.json").read_text(encoding="utf-8"))
    children = logbook["root"]["children"]
    slugs = [child["slug"] for child in children]
    add(checks, "space_id", logbook.get("space_id") == "DineshAI/HMyCBL2yMV", logbook.get("space_id"))
    add(checks, "canonical_first", slugs[0] == "release-report", slugs)
    current = [f"current-claim-{claim}" for claim in (1, 2, 3, 4, 5)]
    historical_positions = [index for index, child in enumerate(children) if child["title"].startswith("Historical rejected baseline")]
    add(
        checks,
        "current_before_historical",
        all(slug in slugs for slug in current) and min(historical_positions) > max(slugs.index(slug) for slug in current),
        historical_positions,
    )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    release_page = (ROOT / "pages/release-report/page.md").read_text(encoding="utf-8")
    add(checks, "readme_entrypoint", "#/release-report" in readme, "README -> release-report")
    add(checks, "score_forecast_not_result", "forecast only; not a judge result" in release_page and "Previous live judged score: `3/10`" in release_page, "explicit forecast label")
    add(checks, "visibility_table", all(header in release_page for header in ["Canonical page", "Code visible", "Data inline", "Raw link", "Checker", "Control", "Exact claim tested", "Reviewer verdict"]), "all required columns")

    for claim, names in CLAIM_FILES.items():
        evidence = ROOT / "evidence" / f"claim-{claim}"
        page = ROOT / "pages" / f"current-claim-{claim}" / "page.md"
        page_text = page.read_text(encoding="utf-8") if page.exists() else ""
        files_exist = all((evidence / name).is_file() for name in names)
        tokens = ["Exact", "Fixed command", "independent checker", "control", "Verdict", "limitation"]
        visible = all(token.lower() in page_text.lower() for token in tokens)
        add(checks, f"claim_{claim}_files", files_exist, names)
        add(checks, f"claim_{claim}_page", visible, tokens)

    report = ROOT / "reports/sequential-mean-testing/report.md"
    report_text = report.read_text(encoding="utf-8") if report.exists() else ""
    for name, expected in FIGURE_HASHES.items():
        path = report.parent / "images" / name
        add(checks, f"figure_{name}", path.is_file() and sha256(path) == expected and f"images/{name}" in report_text, expected)
    add(checks, "notebook", (ROOT / "notebooks/sequential_mean_testing.py").is_file(), "tutorial notebook")

    manifest = ROOT / "evidence/protected-judged-revision-manifest.sha256"
    protected_ok = True
    protected_count = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        snapshot = ROOT / "historical/judged-7f2c76f4" / relative
        if not snapshot.exists():
            snapshot = ROOT / relative
        protected_ok = protected_ok and snapshot.is_file() and sha256(snapshot) == expected
        protected_count += 1
    add(checks, "protected_subset", protected_ok, {"files": protected_count, "mapping": "original path -> historical/judged-7f2c76f4/path"})

    allowlist = ROOT / "evidence/release/publication_allowlist.txt"
    upload_manifest = ROOT / "evidence/release/publication_manifest.sha256"
    allowlisted = allowlist.read_text(encoding="utf-8").splitlines() if allowlist.exists() else []
    manifest_rows = upload_manifest.read_text(encoding="utf-8").splitlines() if upload_manifest.exists() else []
    allowlist_ok = bool(allowlisted) and allowlisted == sorted(set(allowlisted)) and all((ROOT / path).is_file() for path in allowlisted)
    manifest_ok = bool(manifest_rows)
    for line in manifest_rows:
        expected, relative = line.split("  ", 1)
        manifest_ok = manifest_ok and relative in allowlisted and sha256(ROOT / relative) == expected
    add(checks, "text_upload_allowlist", allowlist_ok and all(not path.lower().endswith(".png") for path in allowlisted), len(allowlisted))
    add(checks, "upload_hashes", manifest_ok, len(manifest_rows))

    secret_matches = []
    secret_pattern = re.compile(r"(?:hf_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)")
    for relative in allowlisted:
        path = ROOT / relative
        try:
            match = secret_pattern.search(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            match = True
        if match:
            secret_matches.append(relative)
    add(checks, "secret_scan", not secret_matches, secret_matches)

    for name in ("red-team-round-1.md", "red-team-round-2.md", "visibility_matrix.md", "command_ledger.md"):
        add(checks, f"release_record_{name}", (ROOT / "evidence/release" / name).is_file(), name)

    passed = all(bool(check["passed"]) for check in checks)
    output = {"status": "VERIFIED" if passed else "BLOCKED", "checks": checks}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "release_gate.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print("RELEASE_GATE=" + json.dumps(output, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
