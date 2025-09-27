"""Simple optimisation history recorder."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np

__all__ = ["IterationHistory"]


@dataclass
class IterationHistory:
    """Container storing iteration information.

    Attributes:
        points (List[np.ndarray]): Sequence of visited points.
        values (List[float]): Objective value at each stored point.
        steps (List[float]): Step sizes used between points.
        grad_norms (List[float]): Norm of the gradient at each step.
    """

    points: List[np.ndarray] = field(default_factory=list)
    values: List[float] = field(default_factory=list)
    steps: List[float] = field(default_factory=list)
    grad_norms: List[float] = field(default_factory=list)

    def record(
        self,
        point: np.ndarray,
        value: float,
        step: float | None,
        grad_norm: float,
    ) -> None:
        self.points.append(point.copy())
        self.values.append(float(value))
        self.grad_norms.append(float(grad_norm))
        if step is not None:
            self.steps.append(float(step))

