"""
Optimization algorithms for unconstrained problems.

This module provides gradient-based optimization methods with various
line search strategies.
"""

from typing import Callable, TypedDict
import numpy as np

from .line_search import back_tracking, split_step_cond, LineSearchCondition


class OptimizationHistory(TypedDict):
    """History of optimization process."""

    x: list[np.ndarray]  # Sequence of points
    f: list[float]  # Function values at each point
    t: list[float]  # Step sizes taken
    grad_norm: list[float]  # Gradient norms at each point


def norm2(v: np.ndarray) -> float:
    """
    Compute Euclidean (L2) norm of a vector.

    Args:
        v: Input vector.

    Returns:
        Euclidean norm ||v||_2.
    """
    return np.sqrt(np.sum(v**2))


def gd_back_tracking(
    f: Callable[[np.ndarray], float],
    grad_f: Callable[[np.ndarray], np.ndarray],
    x0: np.ndarray,
    cond: LineSearchCondition | None = None,
    max_iters: int = 2000,
    tol: float = 1e-4,
    t0: float = 1.0,
    beta: float = 0.5,
    c: float = 0.1,
) -> tuple[np.ndarray, OptimizationHistory]:
    """
    Gradient descent with backtracking line search.

    Iteratively moves in the negative gradient direction with step size
    determined by backtracking line search. Terminates when gradient norm
    falls below tolerance or maximum iterations reached.

    Args:
        f: Objective function to minimize.
        grad_f: Gradient of the objective function.
        x0: Initial point.
        cond: Line search condition (e.g., split_step_cond, goldstein_cond).
            If None, uses split_step_cond by default.
        max_iters: Maximum number of iterations.
        tol: Convergence tolerance on gradient norm (default 1e-4 to match lab notebook).
        t0: Initial step size for line search.
        beta: Step size reduction factor in (0, 1).
        c: Parameter for line search condition.

    Returns:
        Tuple containing:
            - x_min: Point where minimum was found.
            - history: Dictionary with optimization trajectory:
                - 'x': list of points visited
                - 'f': list of function values
                - 't': list of step sizes used
                - 'grad_norm': list of gradient norms

    Raises:
        AssertionError: If line search fails to find valid step or
            direction is not a descent direction.
    """
    if cond is None:
        cond = split_step_cond

    x = np.array(x0, dtype=float)
    history: OptimizationHistory = {
        "x": [x.copy()],
        "f": [f(x)],
        "t": [],
        "grad_norm": [],
    }

    for _ in range(max_iters):
        g = grad_f(x)
        gnorm = norm2(g)
        history["grad_norm"].append(gnorm)

        if gnorm < tol:
            break

        p = -g
        assert np.dot(g, p) < 0, "Not a descent direction!"

        # Find step size using line search
        t = back_tracking(f, grad_f, x, p, cond, t0=t0, beta=beta, c=c)
        assert t > 0, "Line search failed to find a valid step size!"

        x = x + t * p

        history["x"].append(x.copy())
        history["f"].append(f(x))
        history["t"].append(t)

    return x, history


__all__ = [
    "OptimizationHistory",
    "norm2",
    "gd_back_tracking",
]
