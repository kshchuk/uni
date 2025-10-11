"""
Visualization utilities for optimization trajectories.

This module provides functions for visualizing optimization processes,
including 3D isosurfaces, convergence plots, and animated trajectories.
"""

from typing import Callable
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib import animation

from .optimizers import OptimizationHistory


def surface_for_slice(
    f: Callable[[np.ndarray], float],
    grid: np.ndarray,
    slice_var: str = "x3",
    slice_val: float = 0.0,
) -> go.Figure:
    """
    Create 3D surface plot for a 2D slice of the objective function.

    Fixes one variable at a constant value and plots the function over
    the other two variables.

    Args:
        f: Objective function taking 3D array.
        grid: 1D array of coordinates for the grid.
        slice_var: Variable to fix ('x1', 'x2', or 'x3').
        slice_val: Value at which to fix the slice variable.

    Returns:
        Plotly Figure object with 3D surface.
    """
    X1g, X2g = np.meshgrid(grid, grid, indexing="ij")

    if slice_var == "x3":
        X3g = np.full_like(X1g, slice_val)
        xlabel, ylabel = "x1", "x2"
        Xplot, Yplot = X1g, X2g
    elif slice_var == "x2":
        X3g = X2g
        X2g = np.full_like(X1g, slice_val)
        xlabel, ylabel = "x1", "x3"
        Xplot, Yplot = X1g, X3g
    else:  # slice_var == "x1"
        X3g = X2g
        X2g = X1g
        X1g = np.full_like(X2g, slice_val)
        xlabel, ylabel = "x2", "x3"
        Xplot, Yplot = X2g, X3g

    Fgrid = np.zeros_like(X1g)
    for i in range(X1g.shape[0]):
        for j in range(X1g.shape[1]):
            x = np.array([X1g[i, j], X2g[i, j], X3g[i, j]])
            Fgrid[i, j] = f(x)

    fig = go.Figure(
        data=[
            go.Surface(
                x=Xplot,
                y=Yplot,
                z=Fgrid,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="f(x)"),
            )
        ]
    )

    fig.update_layout(
        title=f"Surface: {slice_var} = {slice_val:.2f}",
        scene=dict(
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            zaxis_title="f(x)",
        ),
        width=700,
        height=600,
    )

    return fig


def show_isosurface_with_path(
    f: Callable[[np.ndarray], float],
    history: OptimizationHistory,
    grid_range: tuple[float, float] = (-1.2, 1.2),
    vol_n: int = 50,
    level: float | None = None,
    opacity: float = 0.5,
    show_colorbar: bool = True,
) -> go.Figure:
    """
    Display 3D isosurface of objective function with optimization path.

    Args:
        f: Objective function.
        history: Optimization history with trajectory points.
        grid_range: Tuple (min, max) for grid coordinates.
        vol_n: Number of grid points per dimension.
        level: Isosurface level. If None, uses mean of f values along path.
        opacity: Transparency of isosurface (0-1).
        show_colorbar: Whether to display color bar.

    Returns:
        Plotly Figure object with isosurface and path.
    """
    # Create volumetric grid
    grid = np.linspace(grid_range[0], grid_range[1], vol_n)
    X1v, X2v, X3v = np.meshgrid(grid, grid, grid, indexing="ij")

    Fvol = np.zeros((vol_n, vol_n, vol_n))
    for i in range(vol_n):
        for j in range(vol_n):
            for k in range(vol_n):
                x = np.array([X1v[i, j, k], X2v[i, j, k], X3v[i, j, k]])
                Fvol[i, j, k] = f(x)

    # Extract optimization path
    P = np.array(history["x"])

    # Determine isosurface level
    if level is None:
        f_vals = np.array(history["f"])
        level = float(np.mean(f_vals))

    # Create figure
    fig = go.Figure()

    # Add isosurface
    iso = go.Isosurface(
        x=X1v.ravel(),
        y=X2v.ravel(),
        z=X3v.ravel(),
        value=Fvol.ravel(),
        isomin=level,
        isomax=level,
        surface_count=1,
        opacity=opacity,
        caps=dict(x_show=False, y_show=False, z_show=False),
        colorscale="Viridis",
        showscale=show_colorbar,
        colorbar=dict(
            title="f", x=1.02, thickness=14, len=0.6, tickfont=dict(size=10)
        ),
    )

    # Add optimization path
    path = go.Scatter3d(
        x=P[:, 0],
        y=P[:, 1],
        z=P[:, 2],
        mode="lines+markers",
        name="Path",
        marker=dict(size=4, color="red"),
        line=dict(width=4, color="red"),
        hovertemplate=(
            "iter=%{customdata}<br>"
            "x1=%{x:.3f}, x2=%{y:.3f}, x3=%{z:.3f}"
            "<extra></extra>"
        ),
        customdata=np.arange(len(P)),
    )

    fig.add_traces([iso, path])

    fig.update_layout(
        title=f"Isosurface: F = {level:.2f}",
        height=650,
        margin=dict(l=0, r=80 if show_colorbar else 0, b=0, t=40),
        scene=dict(xaxis_title="x1", yaxis_title="x2", zaxis_title="x3"),
    )

    return fig


def plot_metrics(
    history: OptimizationHistory,
    title: str = "Optimization metrics",
    log_f: bool = True,
    log_grad: bool = True,
    x_range: tuple[int, int] | None = (0, 50),
) -> go.Figure:
    """
    Plot optimization metrics: function value, step size, and gradient norm.

    Creates a 2x2 subplot layout with:
        - Top left: f(x_k) over iterations
        - Top right: step size t_k over iterations
        - Bottom left: gradient norm over iterations

    Args:
        history: Optimization history.
        title: Figure title.
        log_f: Use log scale for function values.
        log_grad: Use log scale for gradient norm.
        x_range: Tuple (min, max) for x-axis range. If None, auto-range.

    Returns:
        Plotly Figure object with metrics plots.
    """
    fvals = np.array(history.get("f", []))
    tvals = np.array(history.get("t", []))
    gnorm = np.array(history.get("grad_norm", []))

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("f(x_k)", "step size t_k", "||grad f(x_k)||"),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, None],
        ],
    )

    if fvals.size:
        fig.add_trace(
            go.Scatter(y=fvals, mode="lines+markers", name="f"),
            row=1,
            col=1,
        )
        if log_f:
            fig.update_yaxes(type="log", row=1, col=1)

    if tvals.size:
        fig.add_trace(
            go.Scatter(y=tvals, mode="lines+markers", name="t"),
            row=1,
            col=2,
        )

    if gnorm.size:
        fig.add_trace(
            go.Scatter(y=gnorm, mode="lines+markers", name="||grad||"),
            row=2,
            col=1,
        )
        if log_grad:
            fig.update_yaxes(type="log", row=2, col=1)

    fig.update_layout(height=700, width=900, title_text=title)

    # Set x-axis labels and ranges
    for row, col in [(1, 1), (1, 2), (2, 1)]:
        fig.update_xaxes(title_text="iteration", row=row, col=col)
        if x_range is not None:
            fig.update_xaxes(range=list(x_range), row=row, col=col)

    # Set y-axis labels
    fig.update_yaxes(title_text="f", row=1, col=1)
    fig.update_yaxes(title_text="t", row=1, col=2)
    fig.update_yaxes(title_text="||grad f||", row=2, col=1)

    return fig


def save_video_xyz(
    history: OptimizationHistory,
    filename: str = "path_xyz.mp4",
    fps: int = 8,
    figsize: tuple[int, int] = (7, 6),
) -> None:
    """
    Save 3D optimization trajectory as MP4 video.

    Creates an animated visualization of the optimization path in 3D space,
    with the current point highlighted.

    Args:
        history: Optimization history with trajectory.
        filename: Output video filename.
        fps: Frames per second for video.
        figsize: Figure size (width, height) in inches.

    Note:
        Requires ffmpeg to be installed for video encoding.
    """
    P = np.array(history["x"])
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_zlabel("x3")

    pad = 0.15
    ax.set_xlim(P[:, 0].min() - pad, P[:, 0].max() + pad)
    ax.set_ylim(P[:, 1].min() - pad, P[:, 1].max() + pad)
    ax.set_zlim(P[:, 2].min() - pad, P[:, 2].max() + pad)

    (line,) = ax.plot([], [], [], lw=2, c="tab:blue")
    (point,) = ax.plot([], [], [], "o", c="tab:red")

    def init():
        line.set_data([], [])
        line.set_3d_properties([])
        point.set_data([], [])
        point.set_3d_properties([])
        return line, point

    def update(i):
        line.set_data(P[: i + 1, 0], P[: i + 1, 1])
        line.set_3d_properties(P[: i + 1, 2])
        point.set_data(P[i, 0:1], P[i, 1:2])
        point.set_3d_properties(P[i, 2:3])
        return line, point

    ani = animation.FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=len(P),
        interval=int(1000 / fps),
        blit=True,
    )
    ani.save(filename, writer="ffmpeg", fps=fps)
    plt.close(fig)
    print(f"Saved 3D trajectory video to {filename}")


__all__ = [
    "surface_for_slice",
    "show_isosurface_with_path",
    "plot_metrics",
    "save_video_xyz",
]
