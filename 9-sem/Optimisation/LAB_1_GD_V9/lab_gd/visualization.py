"""Plotting helpers built on Plotly."""
from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from .objective import objective
from .gradient_descent import OptimizationHistory

AxisName = str


def _grid(grid_range: tuple[float, float], points: int) -> np.ndarray:
    start, stop = grid_range
    return np.linspace(start, stop, points)


def surface_slice(
    *,
    slice_axis: AxisName = "x3",
    slice_value: float = 0.0,
    grid_range: tuple[float, float] = (-1.2, 1.2),
    points: int = 40,
) -> "plotly.graph_objects.Figure":
    """Return a surface plot of ``f`` while fixing one coordinate."""
    import plotly.graph_objects as go

    grid = _grid(grid_range, points)

    if slice_axis == "x1":
        x2, x3 = np.meshgrid(grid, grid)
        z = objective((np.full_like(x2, slice_value), x2, x3))
        fig = go.Figure(go.Surface(x=x2, y=x3, z=z, showscale=False))
        fig.update_layout(scene=dict(xaxis_title="x2", yaxis_title="x3"))
    elif slice_axis == "x2":
        x1, x3 = np.meshgrid(grid, grid)
        z = objective((x1, np.full_like(x1, slice_value), x3))
        fig = go.Figure(go.Surface(x=x1, y=x3, z=z, showscale=False))
        fig.update_layout(scene=dict(xaxis_title="x1", yaxis_title="x3"))
    else:
        x1, x2 = np.meshgrid(grid, grid)
        z = objective((x1, x2, np.full_like(x1, slice_value)))
        fig = go.Figure(go.Surface(x=x1, y=x2, z=z, showscale=False))
        fig.update_layout(scene=dict(xaxis_title="x1", yaxis_title="x2"))

    fig.update_layout(
        title=f"Surface of f with {slice_axis} = {slice_value:.3f}",
        scene=dict(zaxis_title="f"),
        margin=dict(l=0, r=0, b=0, t=40),
    )
    return fig


def isosurface(
    *,
    level: float,
    grid_range: tuple[float, float] = (-1.2, 1.2),
    points: int = 30,
    history: OptimizationHistory | None = None,
    show_minimum: bool = True,
) -> "plotly.graph_objects.Figure":
    """Return an isosurface of ``f`` with optional optimisation path."""
    import plotly.graph_objects as go

    grid = _grid(grid_range, points)
    x1, x2, x3 = np.meshgrid(grid, grid, grid, indexing="xy")
    values = objective((x1, x2, x3))

    fig = go.Figure(
        go.Isosurface(
            x=x1.ravel(),
            y=x2.ravel(),
            z=x3.ravel(),
            value=values.ravel(),
            isomin=level,
            isomax=level,
            surface_count=1,
            caps=dict(x_show=False, y_show=False, z_show=False),
            opacity=0.6,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="f"),
        )
    )

    if history is not None:
        path = np.array(history.points)
        fig.add_scatter3d(
            x=path[:, 0],
            y=path[:, 1],
            z=path[:, 2],
            mode="lines+markers",
            name="path",
            marker=dict(size=4),
        )

    if show_minimum:
        fig.add_scatter3d(
            x=[0.0],
            y=[0.0],
            z=[0.0],
            mode="markers+text",
            name="minimum",
            marker=dict(size=6, symbol="diamond"),
            text=["min f=5"],
            textposition="top center",
        )

    fig.update_layout(
        title=f"Isosurface f = {level:.2f}",
        scene=dict(xaxis_title="x1", yaxis_title="x2", zaxis_title="x3"),
        margin=dict(l=0, r=0, b=0, t=40),
    )
    return fig


__all__ = ["surface_slice", "isosurface"]
