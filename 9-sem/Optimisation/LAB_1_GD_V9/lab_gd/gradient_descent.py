"""Gradient descent solver with plugable line search."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .line_search import LineSearchResult
from .objective import ArrayLike, gradient as default_grad, objective as default_obj

Vector = np.ndarray
ObjectiveFn = Callable[[ArrayLike], float]
GradientFn = Callable[[ArrayLike], Vector]
LineSearch = Callable[[ObjectiveFn, GradientFn, Vector, Vector], LineSearchResult]


@dataclass(slots=True)
class OptimizationHistory:
    points: list[Vector]
    values: list[float]
    steps: list[float]
    grad_norms: list[float]
    line_iters: list[int]
    line_success: list[bool]


@dataclass(slots=True)
class OptimizationResult:
    minimiser: Vector
    value: float
    iterations: int
    history: OptimizationHistory


def gradient_descent(
    *,
    f: ObjectiveFn = default_obj,
    grad_f: GradientFn = default_grad,
    x0: ArrayLike,
    line_search: LineSearch,
    tol: float = 1e-6,
    max_iters: int = 100,
) -> OptimizationResult:
    """Run gradient descent with a supplied line search strategy."""
    x = np.asarray(x0, dtype=float).reshape(3)
    history = OptimizationHistory(
        points=[x.copy()],
        values=[f(x)],
        steps=[],
        grad_norms=[],
        line_iters=[],
        line_success=[],
    )

    for iteration in range(1, max_iters + 1):
        grad_x = grad_f(x)
        grad_norm = float(np.linalg.norm(grad_x))
        history.grad_norms.append(grad_norm)

        if grad_norm <= tol:
            break

        direction = -grad_x
        ls_result = line_search(f, grad_f, x, direction)
        step = ls_result.step

        if step <= 0.0 or not np.isfinite(step):
            raise RuntimeError("Line search returned non-positive step size.")

        x = x + step * direction

        history.points.append(x.copy())
        history.values.append(f(x))
        history.steps.append(step)
        history.line_iters.append(ls_result.iterations)
        history.line_success.append(ls_result.success)

        if not ls_result.success:
            break
    else:
        iteration = max_iters

    return OptimizationResult(
        minimiser=x,
        value=f(x),
        iterations=len(history.steps),
        history=history,
    )


__all__ = [
    "gradient_descent",
    "OptimizationResult",
    "OptimizationHistory",
]
