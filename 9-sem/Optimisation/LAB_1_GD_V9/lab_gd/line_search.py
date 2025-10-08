"""Line-search conditions and backtracking routines.

The Goldstein inequalities are given by

.. math::
   f(x) + (1 - c)t\phi'(0) \le f(x + t p) \le f(x) + c t \phi'(0),

where :math:`p` is a descent direction, :math:`\phi(t) = f(x + t p)`
and :math:`\phi'(0) = \nabla f(x)^\top p`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import numpy as np

ObjectiveFn = Callable[[np.ndarray], float]
GradientFn = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class LineSearchResult:
    """Container describing the chosen step size."""

    step: float
    evaluations: int


ConditionFn = Callable[
    [ObjectiveFn, GradientFn, np.ndarray, np.ndarray, float, float, float],
    bool,
]


def simple_decrease_condition(
    func: ObjectiveFn,
    grad: GradientFn,
    x: np.ndarray,
    direction: np.ndarray,
    step: float,
    fx: float,
    phi0: float,
    **_: Dict[str, float],
) -> bool:
    """Armijo-free decrease condition :math:`f(x + t p) < f(x)`."""
    trial = func(x + step * direction)
    return trial < fx


def goldstein_condition(
    func: ObjectiveFn,
    grad: GradientFn,
    x: np.ndarray,
    direction: np.ndarray,
    step: float,
    fx: float,
    phi0: float,
    *,
    c: float = 0.1,
) -> bool:
    """Goldstein bracketing inequalities.

    Parameters
    ----------
    c
        Parameter in :math:`(0, 0.5)` controlling the acceptance interval.
    """
    if not (0.0 < c < 0.5):
        raise ValueError("Goldstein parameter c must lie in (0, 0.5)")

    trial = func(x + step * direction)
    lower = fx + (1.0 - c) * step * phi0
    upper = fx + c * step * phi0
    return lower <= trial <= upper


def backtracking(
    func: ObjectiveFn,
    grad: GradientFn,
    x: np.ndarray,
    direction: np.ndarray,
    *,
    condition: ConditionFn = simple_decrease_condition,
    initial_step: float = 1.0,
    contraction: float = 0.5,
    max_iterations: int = 50,
    condition_kwargs: Optional[Dict[str, float]] = None,
) -> LineSearchResult:
    """Backtracking line search satisfying a user-provided condition.

    The routine tests the sequence :math:`t, \beta t, \beta^2 t, \ldots`
    with :math:`\beta =` ``contraction`` until the condition is met.
    When ``condition`` is :func:`goldstein_condition`, the first phase
    expands the step to ensure the left inequality holds before shrinking
    it back into the acceptable interval.
    """
    if not (0.0 < contraction < 1.0):
        raise ValueError("contraction must lie in (0, 1)")

    direction = np.asarray(direction, dtype=float)
    if direction.shape != x.shape:
        raise ValueError("direction must match shape of x")

    step = float(initial_step)
    fx = float(func(x))
    grad_x = grad(x)
    phi0 = float(np.dot(grad_x, direction))
    if phi0 >= 0:
        raise ValueError("direction is not a descent direction: grad^T p >= 0")

    kwargs = dict(condition_kwargs or {})
    evaluations = 0

    if condition is goldstein_condition:
        c = kwargs.get("c", 0.1)
        # Phase A: ensure left inequality holds by expanding the step.
        for _ in range(max_iterations):
            trial_val = func(x + step * direction)
            evaluations += 1
            if trial_val >= fx + (1.0 - c) * step * phi0:
                break
            step /= contraction
        # Phase B: contract until the right inequality is satisfied.
        for _ in range(max_iterations):
            if condition(func, grad, x, direction, step, fx, phi0, **kwargs):
                return LineSearchResult(step=step, evaluations=evaluations)
            step *= contraction
        raise RuntimeError("Goldstein backtracking failed to satisfy inequalities")

    for _ in range(max_iterations):
        if condition(func, grad, x, direction, step, fx, phi0, **kwargs):
            return LineSearchResult(step=step, evaluations=evaluations)
        step *= contraction
    raise RuntimeError("Backtracking failed to satisfy condition within max_iterations")
