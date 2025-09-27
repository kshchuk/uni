"""Plotly based visualisation utilities."""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..line_search.base import Objective
from ..utils.history import IterationHistory

__all__ = [
    "create_slice_surface",
    "create_isosurface",
    "create_isosurface_with_path",
    "create_metrics_figure",
]

AXIS_NAMES = ("x1", "x2", "x3")


def create_slice_surface(
    objective: Objective,
    grid: Sequence[float],
    fixed_axis: int = 2,
    fixed_value: float = 0.0,
) -> go.Figure:
    """Return a surface plot of the quadratic on a two-dimensional slice."""

    grid_arr = np.asarray(grid, dtype=float)
    if grid_arr.ndim != 1:
        raise ValueError("grid must be a 1D sequence")
    if not 0 <= fixed_axis < 3:
        raise ValueError("fixed_axis must be 0, 1 or 2")

    axes = [idx for idx in range(3) if idx != fixed_axis]
    mesh_a, mesh_b = np.meshgrid(grid_arr, grid_arr, indexing="xy")
    coords = [mesh_a, mesh_b]
    coords.insert(fixed_axis, np.full_like(mesh_a, fixed_value))
    values = objective.value(tuple(coords))  # type: ignore[arg-type]

    figure = go.Figure(
        data=[go.Surface(x=coords[axes[0]], y=coords[axes[1]], z=values, showscale=False)]
    )
    figure.update_layout(
        title=f"Surface slice fixing {AXIS_NAMES[fixed_axis]} = {fixed_value:.3f}",
        scene=dict(
            xaxis_title=AXIS_NAMES[axes[0]],
            yaxis_title=AXIS_NAMES[axes[1]],
            zaxis_title="f",
        ),
    )
    return figure


def create_isosurface(
    objective: Objective,
    grid_range: Tuple[float, float] = (-1.2, 1.2),
    resolution: int = 40,
    level: float | None = None,
) -> Tuple[go.Figure, float]:
    """Return a Plotly isosurface figure and the level used."""

    gmin, gmax = map(float, grid_range)
    lin = np.linspace(gmin, gmax, resolution)
    x1, x2, x3 = np.meshgrid(lin, lin, lin, indexing="xy")
    values = objective.value((x1, x2, x3))  # type: ignore[arg-type]
    if level is None:
        percentiles = np.percentile(values, (5, 95))
        level = float(np.mean(percentiles))

    figure = go.Figure(
        go.Isosurface(
            x=x1.ravel(),
            y=x2.ravel(),
            z=x3.ravel(),
            value=values.ravel(),
            isomin=level,
            isomax=level,
            surface_count=1,
            opacity=0.5,
            caps=dict(x_show=False, y_show=False, z_show=False),
        )
    )
    figure.update_layout(
        title=f"Isosurface f(x) = {level:.2f}",
        scene=dict(xaxis_title="x1", yaxis_title="x2", zaxis_title="x3"),
    )
    return figure, level


def create_isosurface_with_path(
    objective: Objective,
    history: IterationHistory,
    grid_range: Tuple[float, float] = (-1.2, 1.2),
    resolution: int = 40,
    level: float | None = None,
) -> Tuple[go.Figure, float]:
    """Return an isosurface figure with optimisation path overlayed."""

    figure, level = create_isosurface(objective, grid_range, resolution, level)
    points = np.stack(history.points) if history.points else np.empty((0, 3))
    if points.size:
        figure.add_trace(
            go.Scatter3d(
                x=points[:, 0],
                y=points[:, 1],
                z=points[:, 2],
                mode="lines+markers",
                name="trajectory",
                marker=dict(size=4),
                line=dict(width=4),
            )
        )
    return figure, level


def create_metrics_figure(
    history: IterationHistory,
    log_value: bool = True,
    log_gradient: bool = True,
) -> go.Figure:
    """Assemble a subplot visualising objective, step-size and gradient norms."""

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("f(x_k)", "step size", "||grad f(x_k)||"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}], [{"type": "scatter"}, None]],
    )

    if history.values:
        fig.add_trace(
            go.Scatter(y=history.values, mode="lines+markers", name="f"),
            row=1,
            col=1,
        )
        if log_value:
            fig.update_yaxes(type="log", row=1, col=1)

    if history.steps:
        fig.add_trace(
            go.Scatter(y=history.steps, mode="lines+markers", name="step"),
            row=1,
            col=2,
        )

    if history.grad_norms:
        fig.add_trace(
            go.Scatter(y=history.grad_norms, mode="lines+markers", name="||grad||"),
            row=2,
            col=1,
        )
        if log_gradient:
            fig.update_yaxes(type="log", row=2, col=1)

    fig.update_layout(height=700, width=900, title_text="Optimization metrics")
    fig.update_xaxes(title_text="iteration", row=1, col=1)
    fig.update_xaxes(title_text="iteration", row=1, col=2)
    fig.update_xaxes(title_text="iteration", row=2, col=1)
    fig.update_yaxes(title_text="f", row=1, col=1)
    fig.update_yaxes(title_text="step", row=1, col=2)
    fig.update_yaxes(title_text="||grad f||", row=2, col=1)
    return fig

