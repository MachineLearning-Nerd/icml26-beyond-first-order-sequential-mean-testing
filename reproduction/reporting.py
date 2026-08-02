from __future__ import annotations

import csv
import html
from pathlib import Path


COLORS = ["#2563eb", "#dc2626", "#059669", "#7c3aed"]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape(str(value))


def save(path: Path, body: str, width: int = 1200, height: int = 650) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        '<rect width="100%" height="100%" fill="#f8fafc"/>'
        '<style>text{font-family:Inter,Arial,sans-serif;fill:#172033}.title{font-size:28px;font-weight:700}'
        '.sub{font-size:15px;fill:#526072}.label{font-size:14px}.value{font-size:24px;font-weight:700}'
        '.axis{stroke:#94a3b8;stroke-width:1}.grid{stroke:#dbe3ec;stroke-width:1}.target{stroke:#64748b;'
        'stroke-width:2;stroke-dasharray:8 6}.note{font-size:13px;fill:#526072}</style>'
        f"{body}</svg>",
        encoding="utf-8",
    )


def text(x: float, y: float, value: object, cls: str = "label", anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def polyline(points: list[tuple[float, float]], color: str) -> str:
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    circles = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>' for x, y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="4"/>{circles}'


def chart(
    path: Path,
    title: str,
    subtitle: str,
    x_labels: list[str],
    series: list[tuple[str, list[float], str]],
    y_min: float,
    y_max: float,
    target: float | None,
    y_label: str,
) -> None:
    left, top, right, bottom = 105.0, 120.0, 1140.0, 545.0
    plot_w, plot_h = right - left, bottom - top
    body = text(60, 48, title, "title") + text(60, 77, subtitle, "sub")
    for tick in range(6):
        value = y_min + (y_max - y_min) * tick / 5
        y = bottom - plot_h * tick / 5
        body += f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" class="grid"/>'
        body += text(left - 15, y + 5, f"{value:.3g}", "label", "end")
    body += f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>'
    body += f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>'
    if target is not None:
        y = bottom - plot_h * (target - y_min) / (y_max - y_min)
        body += f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" class="target"/>'
        body += text(right - 4, y - 8, f"target {target:g}", "note", "end")
    count = len(x_labels)
    xs = [left + plot_w * index / max(1, count - 1) for index in range(count)]
    for x, label in zip(xs, x_labels):
        body += text(x, bottom + 28, label, "label", "middle")
    for name, values, color in series:
        points = [(x, bottom - plot_h * (value - y_min) / (y_max - y_min)) for x, value in zip(xs, values)]
        body += polyline(points, color)
    legend_x = left
    for name, _, color in series:
        body += f'<rect x="{legend_x}" y="585" width="18" height="5" fill="{color}"/>'
        body += text(legend_x + 26, 592, name, "label")
        legend_x += 260
    body += text(28, (top + bottom) / 2, y_label, "note")
    save(path, body)


def headline(path: Path) -> None:
    cards = [
        ("Claim 1", "VERIFIED", "variance 1.009 / 0.996"),
        ("Claim 2", "VERIFIED", "KS 0.0349 at b=10,000"),
        ("Claim 3", "VERIFIED", "remainder ratio 0.00444"),
        ("Claim 4", "FALSIFIED*", "literal target: coverage = 1"),
        ("Claim 5", "VERIFIED", "DSSAT KS 0.0890 at 1e-4"),
    ]
    body = text(60, 48, "Five exact claim contracts, five executable outcomes", "title")
    body += text(60, 77, "Cumulative HF cpu-upgrade verification; *the proposition's actual deterministic target is supported", "sub")
    for index, (claim, status, metric) in enumerate(cards):
        x = 55 + index * 226
        color = "#7c3aed" if "FALSIFIED" in status else "#059669"
        body += f'<rect x="{x}" y="125" width="205" height="270" rx="16" fill="white" stroke="#dbe3ec"/>'
        body += text(x + 18, 166, claim, "value")
        body += f'<rect x="{x + 18}" y="194" width="169" height="36" rx="18" fill="{color}" opacity="0.12"/>'
        body += f'<text x="{x + 102.5}" y="218" text-anchor="middle" style="font-size:15px;font-weight:700;fill:{color}">{status}</text>'
        body += text(x + 18, 272, metric, "label")
        body += text(x + 18, 304, "verifier exit 0", "note")
        body += text(x + 18, 328, "checker exit 0", "note")
        body += text(x + 18, 352, "control fails", "note")
    body += text(60, 470, "Honest scope", "value")
    body += text(60, 505, "Claims 1–3 and 5 are finite, assumption-audited corroborations—not universal theorem proofs.", "sub")
    body += text(60, 535, "Claim 4 separates the supplied literal wording from Proposition 4.5's displayed coverage target.", "sub")
    save(path, body)


def generate_figures(candidate: Path, output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    headline_path = output / "headline.svg"
    headline(headline_path)
    created.append(headline_path)

    claim_2 = [row for row in rows(candidate / "evidence/claim-2/stopping_clt_metrics.csv") if row["boundary"] == "growing"]
    p = output / "claim2-convergence.svg"
    chart(
        p,
        "Stopping-time CLT converges beyond the paper's finite alpha",
        "Exact growing boundary; 10,000 paths per predeclared b",
        ["4.6", "9.2", "18", "37", "147", "589", "2358", "10000"],
        [
            ("KS distance", [float(row["ks_distance"]) for row in claim_2], COLORS[0]),
            ("|relative centering error|", [abs(float(row["centering_relative_error"])) for row in claim_2], COLORS[1]),
        ],
        0,
        1.1,
        0,
        "error",
    )
    created.append(p)

    claim_3 = rows(candidate / "evidence/claim-3/decomposition_metrics.csv")
    p = output / "claim3-decomposition.svg"
    chart(
        p,
        "The dual remainder vanishes while the linear variance is preserved",
        "Exact pathwise decomposition; 10,000 paths per n",
        [row["n"] for row in claim_3],
        [
            ("T1/T2 RMS", [float(row["t1_to_t2_rms_ratio"]) for row in claim_3], COLORS[0]),
            ("|variance ratio - 1|", [abs(float(row["full_to_t2_variance_ratio"]) - 1) for row in claim_3], COLORS[2]),
        ],
        0,
        0.075,
        0,
        "error",
    )
    created.append(p)

    claim_4 = rows(candidate / "evidence/claim-4/single_run_ci_metrics.csv")
    p = output / "claim4-coverage.svg"
    chart(
        p,
        "The actual Proposition 4.5 coverage calibrates at large b",
        "Each interval uses only its own stopped path; 10,000 paths assess coverage",
        ["147", "589", "2358", "10000"],
        [
            ("95% coverage", [float(row["coverage_95"]) for row in claim_4], COLORS[0]),
            ("2 × 50% coverage", [2 * float(row["coverage_50"]) for row in claim_4], COLORS[3]),
            ("v-hat / theory", [float(row["vhat_ratio_mean"]) for row in claim_4], COLORS[2]),
        ],
        0.90,
        1.05,
        1,
        "scaled agreement",
    )
    created.append(p)

    claim_5 = rows(candidate / "evidence/claim-5/dssat_bootstrap_metrics.csv")
    p = output / "claim5-dssat.svg"
    chart(
        p,
        "DSSAT stopping-time agreement improves as alpha decreases",
        "Pinned official public crop-yield pool; 3,000 bootstrap paths per alpha",
        [row["alpha_label"] for row in claim_5],
        [
            ("KS distance", [float(row["ks_distance"]) for row in claim_5], COLORS[0]),
            ("|variance ratio - 1|", [abs(float(row["variance_ratio"]) - 1) for row in claim_5], COLORS[1]),
            ("|centering error|", [abs(float(row["centering_relative_error"])) for row in claim_5], COLORS[2]),
        ],
        0,
        0.15,
        0,
        "error",
    )
    created.append(p)
    return created
