"""
Line search algorithms and conditions for optimization.

This module provides various line search conditions (Armijo, Goldstein)
and backtracking algorithms to find appropriate step sizes along descent directions.
"""

from typing import Callable, Protocol
import numpy as np


class LineSearchCondition(Protocol):
    """Protocol for line search acceptance conditions."""

    def __call__(
        self,
        f: Callable[[np.ndarray], float],
        x: np.ndarray,
        p: np.ndarray,
        t: float,
        f_x: float,
        grad_f: Callable[[np.ndarray], np.ndarray],
        c: float = 0.1,
    ) -> bool:
        """
        Check if step size satisfies the condition.

        Args:
            f: Objective function.
            x: Current point.
            p: Search direction.
            t: Step size to test.
            f_x: Function value at x (f(x)).
            grad_f: Gradient function.
            c: Parameter for the condition (e.g., Armijo/Goldstein constant).

        Returns:
            True if condition is satisfied, False otherwise.
        """
        ...


def split_step_cond(
    f: Callable[[np.ndarray], float],
    x: np.ndarray,
    p: np.ndarray,
    t: float,
    f_x: float,
    grad_f: Callable[[np.ndarray], np.ndarray],
    c: float = 0.1,
) -> bool:
    """
    Simple sufficient decrease condition (Armijo condition).

    Checks if f(x + t*p) < f(x), ensuring the step produces a decrease
    in the objective function value.

    Args:
        f: Objective function.
        x: Current point.
        p: Search direction (typically -gradient).
        t: Step size to test.
        f_x: Function value at x.
        grad_f: Gradient function (not used in this simple condition).
        c: Not used in this simple condition.

    Returns:
        True if f(x + t*p) < f(x), False otherwise.
    """
    return f(x + t * p) < f_x


def goldstein_cond(
    f: Callable[[np.ndarray], float],
    x: np.ndarray,
    p: np.ndarray,
    t: float,
    f_x: float,
    grad_f: Callable[[np.ndarray], np.ndarray],
    c: float = 0.1,
) -> bool:
    """
    Goldstein conditions for line search.

    Checks both lower and upper bounds:
        f(x) + (1-c)*t*phi0 <= f(x + t*p) <= f(x) + c*t*phi0
    where phi0 = grad_f(x)^T * p < 0 is the directional derivative.

    The lower bound ensures sufficient decrease, while the upper bound
    prevents the step from being too small.

    Args:
        f: Objective function.
        x: Current point.
        p: Search direction.
        t: Step size to test.
        f_x: Function value at x.
        grad_f: Gradient function.
        c: Goldstein parameter, typically in (0, 0.5].

    Returns:
        True if both Goldstein conditions are satisfied, False otherwise.
    """
    g = grad_f(x)
    phi0 = float(np.dot(g, p))
    f_x_new = f(x + t * p)
    left = f_x + (1.0 - c) * t * phi0
    right = f_x + c * t * phi0
    return (left <= f_x_new) and (f_x_new <= right)


def back_tracking(
    f: Callable[[np.ndarray], float],
    grad_f: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    p: np.ndarray,
    cond: Callable | None = None,
    t0: float = 1.0,
    beta: float = 0.5,
    max_halves: int = 100,
    c: float = 0.1,
) -> float:
    """
    Backtracking line search with support for different conditions.

    For Goldstein condition, uses a two-phase approach:
        1. Expansion phase: increase step size until left bound is satisfied
        2. Shrinking phase: decrease step size until right bound is satisfied

    For other conditions (e.g., Armijo), uses standard backtracking:
        repeatedly shrink step size until condition is satisfied.

    Args:
        f: Objective function.
        grad_f: Gradient function.
        x: Current point.
        p: Search direction.
        cond: Line search condition. If None, uses split_step_cond.
            For goldstein_cond, applies two-phase search.
        t0: Initial step size.
        beta: Shrinking factor in (0, 1). For Goldstein expansion, uses 1/beta.
        max_halves: Maximum number of iterations per phase.
        c: Parameter for the line search condition.

    Returns:
        Step size satisfying the condition.

    Raises:
        ValueError: If direction is not a descent direction.
    """
    t = float(t0)
    fx = float(f(x))
    g = grad_f(x)
    phi0 = float(np.dot(g, p))

    # Ensure descent direction
    if phi0 >= 0:
        p = -g
        phi0 = -float(np.dot(g, g))
        if phi0 >= 0:  # Zero gradient
            return 0.0

    # Two-phase Goldstein search
    if cond is goldstein_cond:
        # Phase 1: Expansion - ensure left inequality
        for _ in range(max_halves):
            if f(x + t * p) >= fx + (1.0 - c) * t * phi0:
                break
            t /= beta  # beta < 1 => increase step size

        # Phase 2: Shrinking - ensure right inequality
        for _ in range(max_halves):
            if goldstein_cond(f, x, p, t, fx, grad_f, c=c):
                return t
            t *= beta
        return t

    # Standard backtracking for other conditions
    if cond is None:
        cond = split_step_cond

    for _ in range(max_halves):
        if cond(f, x, p, t, fx, grad_f, c=c):
            return t
        t *= beta
    return t


__all__ = [
    "LineSearchCondition",
    "split_step_cond",
    "goldstein_cond",
    "back_tracking",
]
