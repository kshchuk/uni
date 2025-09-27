"""Matplotlib helpers for exporting optimisation paths."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

from ..utils.history import IterationHistory

__all__ = ["save_xyz_trajectory"]


def save_xyz_trajectory(
    history: IterationHistory,
    filename: str | Path,
    fps: int = 8,
) -> Path:
    """Save an animation of the optimisation trajectory."""

    if not history.points:
        raise ValueError("history must contain at least one point")

    path = Path(filename)
    points = np.stack(history.points)
    fig = plt.figure(figsize=(7, 6))
    axis = fig.add_subplot(111, projection="3d")
    axis.set_xlabel("x1")
    axis.set_ylabel("x2")
    axis.set_zlabel("x3")

    pad = 0.15
    axis.set_xlim(points[:, 0].min() - pad, points[:, 0].max() + pad)
    axis.set_ylim(points[:, 1].min() - pad, points[:, 1].max() + pad)
    axis.set_zlim(points[:, 2].min() - pad, points[:, 2].max() + pad)

    line, = axis.plot([], [], [], lw=2, c="tab:blue")
    marker, = axis.plot([], [], [], "o", c="tab:red")

    def init():  # pragma: no cover - animation callback
        line.set_data([], [])
        line.set_3d_properties([])
        marker.set_data([], [])
        marker.set_3d_properties([])
        return line, marker

    def update(frame: int):  # pragma: no cover - animation callback
        line.set_data(points[: frame + 1, 0], points[: frame + 1, 1])
        line.set_3d_properties(points[: frame + 1, 2])
        marker.set_data(points[frame, 0:1], points[frame, 1:2])
        marker.set_3d_properties(points[frame, 2:3])
        return line, marker

    anim = animation.FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=len(points),
        interval=int(1000 / fps),
        blit=True,
    )
    anim.save(str(path), writer="ffmpeg", fps=fps)
    plt.close(fig)
    return path

