"""Optimiser base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

import numpy as np

from ..line_search.base import Objective

__all__ = ["Optimizer", "History"]


class History(Protocol):
    """Protocol describing optimisation history containers."""

    def record(
        self,
        point: np.ndarray,
        value: float,
        step: float | None,
        grad_norm: float,
    ) -> None:  # pragma: no cover - interface only
        ...


class Optimizer(ABC):
    """Abstract base class for iterative optimisers."""

    @abstractmethod
    def minimise(
        self,
        objective: Objective,
        initial_point: np.ndarray,
        history: History | None = None,
    ) -> np.ndarray:
        """Return the computed minimiser starting from ``initial_point``."""

