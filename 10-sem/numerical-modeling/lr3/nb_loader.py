"""Завантаження функцій розв'язувача з navier_stokes_2d.ipynb (для _make_figures.py)."""
from __future__ import annotations

from pathlib import Path

import nbformat

_STOP_MARKDOWN = "## Запуск чисельного експерименту"


def _exec_cell(source: str, namespace: dict) -> None:
    """Виконати код комірки, пропускаючи IPython magic (%% / %)."""
    lines = []
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        lines.append(line)
    code = "\n".join(lines).strip()
    if code:
        exec(code, namespace)  # noqa: S102


def load_solver(root: Path | None = None) -> dict:
    """Виконати кодові комірки ноутбука до розділу запуску експерименту."""
    root = root or Path(__file__).parent
    nb = nbformat.read(root / "navier_stokes_2d.ipynb", as_version=4)
    namespace: dict = {"__name__": "__main__"}
    for cell in nb.cells:
        if cell.cell_type == "markdown" and _STOP_MARKDOWN in cell.source:
            break
        if cell.cell_type == "code":
            _exec_cell(cell.source, namespace)
    return namespace
