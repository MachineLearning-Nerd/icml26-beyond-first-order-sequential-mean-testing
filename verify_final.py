from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANONICAL_IDENTITY = "MachineLearning-Nerd <37579156+MachineLearning-Nerd@users.noreply.github.com>"
REPOSITORY = "MachineLearning-Nerd/icml26-beyond-first-order-sequential-mean-testing"
EXPECTED_BRANCHES = {
    "main",
    "audit/claim-1-frozen-judged-baseline",
    "audit/claim-2-stopping-time-clt",
    "audit/claim-3-decomposition-anscombe",
    "audit/claim-4-single-run-intervals",
    "audit/claim-5-stopped-draw-evidence",
    "audit/claim-5-synthetic-dssat",
    "release/candidate-audit-report",
    "release/claim-1-evidence",
    "release/claim-2-evidence",
    "release/claim-3-evidence",
    "release/claim-4-evidence",
    "release/claim-5-evidence",
    "release/concise-evidence-stream",
    "release/cumulative-navigation-repair",
    "release/final-gate-audits",
    "release/publication-gates",
}


def run(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        list(args),
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return result.stdout.strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float, tolerance: float = 1e-9) -> bool:
    return math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)


def main() -> int:
    failures: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            failures.append(name)

    remote = run("git", "remote", "get-url", "origin").removesuffix(".git")
    check(remote == f"https://github.com/{REPOSITORY}", "canonical origin")
    check(run("git", "symbolic-ref", "--short", "HEAD") == "main", "checked-out main")
    check(run("git", "symbolic-ref", "refs/remotes/origin/HEAD") == "refs/remotes/origin/main", "origin HEAD")

    remote_branches = {
        line.removeprefix("origin/")
        for line in run("git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").splitlines()
        if line and line not in {"origin", "origin/HEAD"}
    }
    check(remote_branches == EXPECTED_BRANCHES, "exact remote branch set")
    refs = run("git", "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes/origin").splitlines()
    check(not any("orx/" in ref or "refs/original/" in ref for ref in refs), "old refs absent")

    commit_count = int(run("git", "rev-list", "--count", "--all"))
    check(commit_count >= 28, "reachable history preserved")
    identities = run("git", "log", "--all", "--format=%an <%ae>%n%cn <%ce>").splitlines()
    check(identities and all(identity == CANONICAL_IDENTITY for identity in identities), "canonical commit identities")
    messages = run("git", "log", "--all", "--format=%B")
    check(not re.search(r"^Co-authored-by:", messages, flags=re.MULTILINE | re.IGNORECASE), "no coauthor trailers")

    required = [
        "README.md",
        "STATUS.md",
        "branch-audit.md",
        "BRANCH_AUDIT.md",
        "AUTHOR_THANK_YOU.md",
        "CITATION.cff",
        "CLAIM_EVIDENCE.md",
        "ENVIRONMENT.md",
        "REPORT.md",
        "SOURCE_AUDIT.md",
        "claims.json",
        "reproduction_verdicts.json",
        "AUTONOMOUS_STATE.json",
        "EVIDENCE_MANIFEST.json",
        "verify_final.py",
        "space_candidate/evidence/release/publication_allowlist.txt",
        "space_candidate/evidence/release/publication_manifest.sha256",
        "space_candidate/evidence/protected-judged-revision-manifest.sha256",
        "space_candidate/evidence/release/verify_release.py",
        "space_candidate/evidence/release/visibility_matrix.md",
        "space_candidate/pages/release-report/page.md",
        "space_candidate/logbook.json",
        "reproduction/config.json",
        "pyproject.toml",
        "uv.lock",
    ]
    check(all((ROOT / path).is_file() for path in required), "dossier files present")

    manifest = json.loads((ROOT / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
    check(
        manifest.get("branch_contract")
        == {"default": "main", "total": 17, "descriptive": 16, "old_prefix_absent": "orx/"},
        "manifest branch contract",
    )
    check(
        manifest.get("aggregate_manifests", {}).get("space_candidate/evidence/release/publication_manifest.sha256")
        == sha256(ROOT / "space_candidate/evidence/release/publication_manifest.sha256"),
        "publication aggregate hash",
    )
    check(
        manifest.get("aggregate_manifests", {}).get("space_candidate/evidence/protected-judged-revision-manifest.sha256")
        == sha256(ROOT / "space_candidate/evidence/protected-judged-revision-manifest.sha256"),
        "protected aggregate hash",
    )
    for relative, expected in manifest.get("files", {}).items():
        path = ROOT / relative
        check(path.is_file() and sha256(path) == expected, f"manifest hash: {relative}")

    claims = json.loads((ROOT / "claims.json").read_text(encoding="utf-8"))
    statuses = {str(claim["id"]): claim["status"] for claim in claims["claims"]}
    check(
        statuses
        == {
            "1": "VERIFIED_FINITE_CONTRACT",
            "2": "VERIFIED_FINITE_CONTRACT",
            "3": "VERIFIED_FINITE_FULL_PREFIX_CONTRACT",
            "4": "FALSIFIED_LITERAL_FORMULA_SUPPORTED",
            "5": "VERIFIED_DECLARED_PUBLIC_DATA_CONTRACT",
        },
        "claim status ledger",
    )

    verdicts = json.loads((ROOT / "reproduction_verdicts.json").read_text(encoding="utf-8"))
    check(
        verdicts.get("repository") == REPOSITORY
        and verdicts.get("overall_verdict") == "PARTIAL_FINITE_CONTRACTS_CLAIM_4_LITERAL_FALSIFIED"
        and verdicts.get("publication_allowed") is False,
        "reproduction verdict header",
    )
    verdict_statuses = {str(claim["id"]): claim["status"] for claim in verdicts["claims"]}
    check(verdict_statuses == statuses, "reproduction verdict status ledger")

    state = json.loads((ROOT / "AUTONOMOUS_STATE.json").read_text(encoding="utf-8"))
    check(
        state.get("phase") == "published_and_verified"
        and state.get("overall_verdict") == "PARTIAL_FINITE_CONTRACTS_CLAIM_4_LITERAL_FALSIFIED"
        and state.get("publication_allowed") is False
        and state.get("live_verification", {}).get("default_branch") == "main",
        "autonomous state",
    )

    claim1 = json.loads((ROOT / "space_candidate/evidence/claim-1/checker_output.json").read_text())
    claim1_control = json.loads((ROOT / "space_candidate/evidence/claim-1/negative_control.json").read_text())
    beta = claim1["recomputed"]["('Beta(3,2)', 5000)"]
    bernoulli = claim1["recomputed"]["('Bernoulli(0.6)', 5000)"]
    check(
        claim1["passed"]
        and close(beta["variance"], 1.0092839787469237)
        and close(bernoulli["variance"], 0.9956726647955515),
        "Claim 1 decisive output",
    )
    check(claim1_control["valid"] and claim1_control["observed"] == "FAIL", "Claim 1 negative control")

    claim2 = json.loads((ROOT / "space_candidate/evidence/claim-2/checker_output.json").read_text())
    claim2_controls = json.loads((ROOT / "space_candidate/evidence/claim-2/negative_controls.json").read_text())
    growing = claim2["recomputed"]["('growing', 'exp(-10000)')"]
    check(
        claim2["passed"]
        and claim2["crossing_failures"] == 0
        and claim2["paths_checked"] == 160000
        and close(growing["variance"], 0.992319842585117),
        "Claim 2 decisive output",
    )
    check(all(control["valid"] and control["observed"] == "FAIL" for control in claim2_controls.values()), "Claim 2 negative controls")

    claim3 = json.loads((ROOT / "space_candidate/evidence/claim-3/checker_output.json").read_text())
    claim3_controls = json.loads((ROOT / "space_candidate/evidence/claim-3/negative_controls.json").read_text())
    check(
        claim3["passed"]
        and claim3["decomposition_paths_checked"] == 40000
        and claim3["anscombe_paths_checked"] == 100000
        and claim3["nested_window_failures"] == 0
        and claim3["anscombe_seed_replay"],
        "Claim 3 decisive output",
    )
    check(all(control["valid"] and control["observed"] == "FAIL" for control in claim3_controls.values()), "Claim 3 negative controls")

    claim4 = json.loads((ROOT / "space_candidate/evidence/claim-4/checker_output.json").read_text())
    claim4_controls = json.loads((ROOT / "space_candidate/evidence/claim-4/negative_controls.json").read_text())
    check(
        claim4["passed"]
        and claim4["raw_paths_checked"] == 40000
        and claim4["nested_stopping_failures"] == 0
        and close(claim4["literal_stopping_time_self_coverage"], 1.0),
        "Claim 4 decisive output",
    )
    check(all(control["valid"] and control["observed"] == "FAIL" for control in claim4_controls.values()), "Claim 4 negative controls")

    claim5 = json.loads((ROOT / "space_candidate/evidence/claim-5/checker_output.json").read_text())
    claim5_controls = json.loads((ROOT / "space_candidate/evidence/claim-5/negative_controls.json").read_text())
    check(
        claim5["passed"]
        and claim5["source_files_hashed"] == 10
        and claim5["pool_rows_checked"] == 44
        and claim5["raw_paths_checked"] == 9000
        and claim5["first_hit_inequalities_checked"] == 9000
        and claim5["independent_scalar_brent_solver"],
        "Claim 5 decisive output",
    )
    check(all(control["valid"] and control["observed"] == "FAIL" for control in claim5_controls.values()), "Claim 5 negative controls")

    release = subprocess.run(
        [sys.executable, "space_candidate/evidence/release/verify_release.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    check(release.returncode == 0, "existing release gate")

    if failures:
        print("FINAL_AUDIT=BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"FINAL_AUDIT=VERIFIED branches={len(EXPECTED_BRANCHES)} commits={commit_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
