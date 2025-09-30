"""Line search routines for gradient descent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .objective import ArrayLike

Vector = np.ndarray
ObjectiveFn = Callable[[ArrayLike], float]
GradientFn = Callable[[ArrayLike], Vector]
LineSearch = Callable[[ObjectiveFn, GradientFn, Vector, Vector], "LineSearchResult"]


@dataclass(slots=True)
class LineSearchResult:
    step: float
    iterations: int
    success: bool


def simple_backtracking(
    f: ObjectiveFn,
    x: Vector,
    direction: Vector,
    *,
    t0: float = 1.0,
    beta: float = 0.5,
    max_iter: int = 50,
) -> LineSearchResult:
    """Back-tracking with monotonic decrease of ``f``."""
    fx = f(x)
    t = float(t0)
    iters = 0

    for iters in range(1, max_iter + 1):
        candidate = x + t * direction
        if f(candidate) < fx:
            return LineSearchResult(step=t, iterations=iters, success=True)
        t *= beta

    return LineSearchResult(step=t, iterations=iters, success=False)


def goldstein_backtracking(
    f: ObjectiveFn,
    grad_f: GradientFn,
    x: Vector,
    direction: Vector,
    *,
    t0: float = 1.0,
    beta: float = 0.5,
    c: float = 0.1,
    max_iter: int = 60,
) -> LineSearchResult:
    """Goldstein line search using expand-then-shrink strategy."""
    if not (0.0 < c < 0.5):
        raise ValueError("Goldstein parameter 'c' must lie in (0, 0.5).")

    fx = f(x)
    grad_x = grad_f(x)
    directional_derivative = float(np.dot(grad_x, direction))
    if directional_derivative >= 0.0:
        raise ValueError("Direction is not a descent direction under Goldstein rule.")

    t = float(t0)
    expand = 1.0 / beta
    if expand <= 1.0:
        raise ValueError("'beta' must be in (0,1) for Goldstein line search.")

    iterations = 0

    for _ in range(max_iter):
        iterations += 1
        trial = x + t * direction
        if f(trial) >= fx + (1.0 - c) * t * directional_derivative:
            break
        t *= expand
    else:
        return LineSearchResult(step=t, iterations=iterations, success=False)

    for _ in range(max_iter):
        iterations += 1
        trial = x + t * direction
        if f(trial) <= fx + c * t * directional_derivative:
            return LineSearchResult(step=t, iterations=iterations, success=True)
        t *= beta

    return LineSearchResult(step=t, iterations=iterations, success=False)


def simple_rule(*, t0: float = 1.0, beta: float = 0.5, max_iter: int = 50) -> LineSearch:
    """Factory producing a callable compatible with :func:`~lab_gd.gradient_descent`."""

    def _rule(f: ObjectiveFn, _grad: GradientFn, x: Vector, direction: Vector) -> LineSearchResult:
        return simple_backtracking(f, x, direction, t0=t0, beta=beta, max_iter=max_iter)

    return _rule


def goldstein_rule(
    *,
    t0: float = 1.0,
    beta: float = 0.5,
    c: float = 0.1,
    max_iter: int = 60,
) -> LineSearch:
    """Factory producing the Goldstein line search callable."""

    def _rule(f: ObjectiveFn, grad: GradientFn, x: Vector, direction: Vector) -> LineSearchResult:
        return goldstein_backtracking(
            f,
            grad,
            x,
            direction,
            t0=t0,
            beta=beta,
            c=c,
            max_iter=max_iter,
        )

    return _rule


__all__ = [
    "LineSearch",
    "LineSearchResult",
    "simple_backtracking",
    "goldstein_backtracking",
    "simple_rule",
    "goldstein_rule",
]
