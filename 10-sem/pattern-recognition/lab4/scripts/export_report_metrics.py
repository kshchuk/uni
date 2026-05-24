#!/usr/bin/env python3
"""Виконує код з lab-4.ipynb: report_metrics_generated.tex і PNG для REPORT.tex."""
from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "lab-4.ipynb"
OUT_TEX = ROOT / "report_metrics_generated.tex"
FIG_DIR = ROOT / "figures"


def _cell_sources(nb: dict) -> list[str]:
    return ["".join(c.get("source", [])) for c in nb["cells"] if c.get("cell_type") == "code"]


def _find_cell(cells: list[str], predicate) -> str:
    for s in cells:
        if predicate(s):
            return s
    raise RuntimeError("required notebook code cell not found")


def notebook_namespace() -> dict:
    nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
    cells = _cell_sources(nb)
    imp = _find_cell(cells, lambda s: "import matplotlib" in s and "import numpy" in s)
    logic = _find_cell(cells, lambda s: "def run_experiment" in s and "CLASSES" in s)

    ns: dict = {}
    exec(imp, ns, ns)
    exec(logic, ns, ns)
    return ns


def _fmt_vec(v, prec=4) -> str:
    return "(" + ", ".join(f"{x:.{prec}f}" for x in v) + ")"


def _tex_escape(s: str) -> str:
    return s.replace("_", r"\_")


def build_tex(exp: dict, dim_labels: list) -> str:
    names = exp["names"]
    w = exp["weights"]
    total = exp["total_spread"]
    lines = [
        r"% --- AUTO-GENERATED from lab-4.ipynb via export_report_metrics.py ---",
        r"% Оновити: python3 lab4/scripts/export_report_metrics.py",
        "",
        r"\begin{table}[H]",
        r"\centering",
        r"\renewcommand{\arraystretch}{1.15}",
        r"\begin{tabular}{|l|c|c|}",
        r"\hline",
        r"\textbf{Клас} & \textbf{Підхід 1 (середина діапазону)} & \textbf{Підхід 2 (середнє)} \\",
        r"\hline",
    ]
    for n in names:
        r1 = exp["range"]["representatives"][n]
        r2 = exp["mean"]["representatives"][n]
        lines.append(f"{_tex_escape(n)} & {_fmt_vec(r1)} & {_fmt_vec(r2)} \\\\")
        lines.append(r"\hline")
    lines.extend(
        [
            r"\end{tabular}",
            r"\caption{Середні представники класів у $\mathbb{R}^4$}",
            r"\label{tab:lab4reps}",
            r"\end{table}",
            "",
            r"\begin{table}[H]",
            r"\centering",
            r"\renewcommand{\arraystretch}{1.15}",
            r"\begin{tabular}{|l|" + "r|" * len(names) + "r|r|}",
            r"\hline",
            r"\textbf{Вимір} & "
            + " & ".join(_tex_escape(n) for n in names)
            + r" & \textbf{$S_j$} & \textbf{$w_j$} \\",
            r"\hline",
        ]
    )
    for j, lab in enumerate(dim_labels):
        row = f"{lab} "
        for n in names:
            row += f"& {exp['spreads'][n][j]:.0f} "
        row += f"& {total[j]:.0f} & {w[j]:.6f} \\\\"
        lines.append(row)
        lines.append(r"\hline")
    lines.extend(
        [
            r"\end{tabular}",
            r"\caption{Розмахи класів $s_{k,j}$, сумарний розмах $S_j$ і ваги $w_j=1/S_j$}",
            r"\label{tab:lab4weights}",
            r"\end{table}",
            "",
        ]
    )

    for approach_key, approach_title in [("range", "Підхід 1"), ("mean", "Підхід 2")]:
        vote = exp[approach_key]["vote"]
        lines.extend(
            [
                r"\begin{table}[H]",
                r"\centering",
                r"\renewcommand{\arraystretch}{1.12}",
                r"\begin{tabular}{|c|" + "l|" * len(names) + "l|}",
                r"\hline",
                r"\textbf{Вимір} & "
                + " & ".join(f"\\textbf{{{_tex_escape(n)}}}" for n in names)
                + r" & \textbf{Переможець} \\",
                r"\hline",
            ]
        )
        for j, lab in enumerate(dim_labels):
            winners = vote.winners_per_dim[j]
            cells = ["$\\checkmark$" if n in winners else "---" for n in names]
            win_str = ", ".join(_tex_escape(w) for w in winners)
            lines.append(f"{lab} & " + " & ".join(cells) + f" & {win_str} \\\\")
            lines.append(r"\hline")
        vote_summary = ", ".join(f"{_tex_escape(n)}: {v}" for n, v in vote.votes_per_class.items())
        win_label = (
            f"нічия ({', '.join(_tex_escape(t) for t in vote.tied_classes)})"
            if vote.tie
            else _tex_escape(vote.winner or "")
        )
        lines.extend(
            [
                rf"\multicolumn{{{len(names)+2}}}{{|l|}}{{\textbf{{Голоси:}} {vote_summary}; \textbf{{рішення:}} {win_label}}} \\",
                r"\hline",
                r"\end{tabular}",
                rf"\caption{{Голосування по вимірах ({approach_title})}}",
                rf"\label{{tab:lab4vote{approach_key}}}",
                r"\end{table}",
                "",
            ]
        )

    lines.extend(
        [
            r"\begin{table}[H]",
            r"\centering",
            r"\renewcommand{\arraystretch}{1.15}",
            r"\begin{tabular}{|l|r|r|r|l|}",
            r"\hline",
            r"\textbf{Підхід} & \textbf{$D_{\text{Зел.}}$} & \textbf{$D_{\text{Син.}}$} & \textbf{$D_{\text{Черв.}}$} & \textbf{Клас} \\",
            r"\hline",
        ]
    )
    for approach_key, approach_title in [("range", "Підхід 1"), ("mean", "Підхід 2")]:
        wd = exp[approach_key]["weighted"]
        d = wd.distances
        lines.append(
            f"{approach_title} & {d['Зелена']:.4f} & {d['Синя']:.4f} & {d['Червона']:.4f} & {_tex_escape(wd.winner)} \\\\"
        )
        lines.append(r"\hline")
    lines.extend(
        [
            r"\end{tabular}",
            r"\caption{Зважена сума модулів $D_k$ для тестової точки $(6,6,26,5)$}",
            r"\label{tab:lab4weighted}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def export_figures(exp: dict, class_colors: dict) -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    classes = exp["classes"]
    test = exp["test"]
    names = exp["names"]
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    reps_r = exp["range"]["representatives"]

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, (i, j) in zip(axes.ravel(), pairs):
        for n in names:
            pts = classes[n]
            ax.scatter(
                pts[:, i], pts[:, j], c=class_colors[n], s=60, alpha=0.85,
                label=n, edgecolors="k", linewidths=0.4,
            )
            mu = reps_r[n]
            ax.scatter(mu[i], mu[j], c=class_colors[n], s=180, marker="X",
                       edgecolors="black", linewidths=1.0, zorder=5)
        ax.scatter(test[i], test[j], s=220, c="gold", marker="*",
                   edgecolors="black", linewidths=1.2, zorder=6, label="тест")
        ax.set_xlabel(f"$x_{i+1}$")
        ax.set_ylabel(f"$x_{j+1}$")
        ax.set_title(f"$x_{i+1}$ vs $x_{j+1}$")
        ax.grid(True, alpha=0.3)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc="upper center", ncol=4, fontsize=9)
    fig.suptitle("Навчальні точки, представники (підхід 1) і тестова точка", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(FIG_DIR / "lab4_pairplot.png", dpi=200, facecolor="white")
    plt.close(fig)

    for approach_key, title in [("range", "Підхід 1"), ("mean", "Підхід 2")]:
        vote = exp[approach_key]["vote"]
        fig, ax = plt.subplots(figsize=(7, 4))
        counts = [vote.votes_per_class[n] for n in names]
        ax.bar(names, counts, color=[class_colors[n] for n in names], edgecolor="black")
        ax.set_ylabel("Голосів")
        ax.set_title(f"Голосування по вимірах ({title})")
        ax.set_ylim(0, max(counts) + 1)
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"lab4_votes_{approach_key}.png", dpi=200, facecolor="white")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(2)
    width = 0.25
    for idx, n in enumerate(names):
        vals = [
            exp["range"]["weighted"].distances[n],
            exp["mean"]["weighted"].distances[n],
        ]
        ax.bar(x + idx * width, vals, width, label=n, color=class_colors[n], edgecolor="black")
    ax.set_xticks(x + width)
    ax.set_xticklabels(["Підхід 1", "Підхід 2"])
    ax.set_ylabel(r"$D_k$")
    ax.set_title("Зважена відстань до тестової точки")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "lab4_distances_weighted.png", dpi=200, facecolor="white")
    plt.close(fig)


def main() -> None:
    ns = notebook_namespace()
    exp = ns["run_experiment"]()
    tex = build_tex(exp, ns["DIM_LABELS"])
    OUT_TEX.write_text(tex, encoding="utf-8")
    print("Wrote", OUT_TEX)
    export_figures(exp, ns["CLASS_COLORS"])
    print("Wrote figures to", FIG_DIR)


if __name__ == "__main__":
    main()
