"""Line-search acceptance conditions."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from .base import Objective

__all__ = ["LineSearchCondition", "SimpleDecrease", "GoldsteinCondition"]


class LineSearchCondition(ABC):
    """Abstract strategy describing when a trial step is acceptable."""

    @abstractmethod
    def is_satisfied(
        self,
        objective: Objective,
        point: np.ndarray,
        direction: np.ndarray,
        step: float,
        gradient: np.ndarray,
    ) -> bool:
        """Return ``True`` if the step satisfies the condition."""


class SimpleDecrease(LineSearchCondition):
    """Accept steps that strictly decrease the objective value."""

    def is_satisfied(
        self,
        objective: Objective,
        point: np.ndarray,
        direction: np.ndarray,
        step: float,
        gradient: np.ndarray,
    ) -> bool:
        trial = point + step * direction
        return objective.value(trial) < objective.value(point)


class GoldsteinCondition(LineSearchCondition):
    """Goldstein line-search acceptance condition.

    Args:
        c (float): Parameter in ``(0, 0.5)`` controlling the interval width.
    """

    def __init__(self, c: float = 0.2) -> None:
        if not 0 < c < 0.5:
            raise ValueError("Goldstein parameter c must lie in (0, 0.5)")
        self.c = float(c)

    def is_satisfied(
        self,
        objective: Objective,
        point: np.ndarray,
        direction: np.ndarray,
        step: float,
        gradient: np.ndarray,
    ) -> bool:
        phi0 = float(gradient @ direction)
        trial_value = objective.value(point + step * direction)
        base_value = objective.value(point)
        left_bound = base_value + (1 - self.c) * step * phi0
        right_bound = base_value + self.c * step * phi0
        return left_bound <= trial_value <= right_bound

