"""Backtracking line-search implementation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .base import LineSearch, Objective
from .conditions import GoldsteinCondition, LineSearchCondition

__all__ = ["BacktrackingLineSearch"]


@dataclass
class BacktrackingLineSearch(LineSearch):
    """Backtracking line-search with optional Goldstein expansion phase.

    Args:
        condition (LineSearchCondition): Acceptance rule for candidate steps.
        initial_step (float): Starting trial step size.
        contraction (float): Multiplicative factor in ``(0, 1)`` used when shrinking.
        expansion (float): Factor ``> 1`` used during expansion for Goldstein.
        max_iter (int): Maximum number of shrink/expand iterations.
    """

    condition: LineSearchCondition
    initial_step: float = 1.0
    contraction: float = 0.5
    expansion: float = 2.0
    max_iter: int = 50

    def __post_init__(self) -> None:
        if not self.initial_step > 0:
            raise ValueError("initial_step must be positive")
        if not 0 < self.contraction < 1:
            raise ValueError("contraction must lie in (0, 1)")
        if not self.expansion > 1:
            raise ValueError("expansion must be > 1")
        if self.max_iter <= 0:
            raise ValueError("max_iter must be positive")

    def __call__(
        self,
        objective: Objective,
        point: np.ndarray,
        direction: np.ndarray,
        gradient: np.ndarray,
    ) -> float:
        step = float(self.initial_step)
        base_value = objective.value(point)
        phi0 = float(gradient @ direction)

        if isinstance(self.condition, GoldsteinCondition):
            # Goldstein requires expansion until left inequality holds
            step = self._expand_until_left(objective, point, direction, phi0, base_value)
            step = self._shrink_until_right(objective, point, direction, phi0, base_value, step)
            return step

        for _ in range(self.max_iter):
            if self.condition.is_satisfied(objective, point, direction, step, gradient):
                return step
            step *= self.contraction
        raise RuntimeError("Backtracking failed to satisfy condition")

    def _expand_until_left(
        self,
        objective: Objective,
        point: np.ndarray,
        direction: np.ndarray,
        phi0: float,
        base_value: float,
    ) -> float:
        step = float(self.initial_step)
        cond = self.condition
        for _ in range(self.max_iter):
            trial = point + step * direction
            lhs = base_value + (1.0 - cond.c) * step * phi0
            if objective.value(trial) >= lhs:
                return step
            step *= self.expansion
        return step

    def _shrink_until_right(
        self,
        objective: Objective,
        point: np.ndarray,
        direction: np.ndarray,
        phi0: float,
        base_value: float,
        step: float,
    ) -> float:
        cond = self.condition
        for _ in range(self.max_iter):
            trial = point + step * direction
            rhs = base_value + cond.c * step * phi0
            value = objective.value(trial)
            if value <= rhs:
                return step
            step *= self.contraction
        raise RuntimeError("Goldstein backtracking failed to satisfy right inequality")

