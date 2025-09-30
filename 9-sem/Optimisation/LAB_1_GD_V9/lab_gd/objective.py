"""Objective function and derivatives for Variant 9 optimisation task."""
from __future__ import annotations

import numpy as np

ArrayLike = np.ndarray | tuple[float, float, float] | list[float]


def _as_array(x: ArrayLike) -> np.ndarray:
    """Return ``x`` as a 1-D NumPy array of shape (3,)."""
    arr = np.asarray(x, dtype=float).reshape(3)
    return arr


def objective(x: ArrayLike) -> float:
    """Quadratic objective ``f(x1,x2,x3)`` from the assignment."""
    x1, x2, x3 = _as_array(x)
    return (
        200.0 * x1 ** 2
        + 5.0 * x2 ** 2
        + 144.0 * x3 ** 2
        - 24.0 * x1 * x2
        - 48.0 * x1 * x3
        + 24.0 * x2 * x3
        + 5.0
    )


def gradient(x: ArrayLike) -> np.ndarray:
    """Gradient of :func:`objective`."""
    x1, x2, x3 = _as_array(x)
    return np.array(
        [
            400.0 * x1 - 24.0 * x2 - 48.0 * x3,
            10.0 * x2 - 24.0 * x1 + 24.0 * x3,
            288.0 * x3 - 48.0 * x1 + 24.0 * x2,
        ]
    )


def hessian(_: ArrayLike | None = None) -> np.ndarray:
    """Hessian matrix of ``objective`` (constant for this quadratic)."""
    return np.array(
        [
            [400.0, -24.0, -48.0],
            [-24.0, 10.0, 24.0],
            [-48.0, 24.0, 288.0],
        ]
    )


__all__ = ["objective", "gradient", "hessian", "ArrayLike"]
