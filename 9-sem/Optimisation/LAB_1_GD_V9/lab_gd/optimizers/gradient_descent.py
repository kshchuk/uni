"""Gradient descent optimiser with pluggable line-search."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..line_search.base import LineSearch, Objective
from ..utils.history import IterationHistory
from .base import Optimizer

__all__ = ["GradientDescent"]


@dataclass
class GradientDescent(Optimizer):
    """Gradient descent using a provided line-search strategy."""

    line_search: LineSearch
    tolerance: float = 1e-6
    max_iterations: int = 100

    def minimise(
        self,
        objective: Objective,
        initial_point: np.ndarray,
        history: IterationHistory | None = None,
    ) -> np.ndarray:
        point = np.asarray(initial_point, dtype=float)
        if point.ndim != 1:
            raise ValueError("initial_point must be a 1D array")

        value = objective.value(point)
        gradient = objective.gradient(point)
        grad_norm = float(np.linalg.norm(gradient))

        if history is not None:
            history.record(point, value, None, grad_norm)

        for _ in range(self.max_iterations):
            if grad_norm <= self.tolerance:
                break

            direction = -gradient
            if float(gradient @ direction) >= 0:
                raise RuntimeError("Direction is not a descent direction")

            step = self.line_search(objective, point, direction, gradient)
            if step <= 0:
                raise RuntimeError("Line-search returned non-positive step")

            point = point + step * direction
            value = objective.value(point)
            gradient = objective.gradient(point)
            grad_norm = float(np.linalg.norm(gradient))

            if history is not None:
                history.record(point, value, step, grad_norm)

        return point

