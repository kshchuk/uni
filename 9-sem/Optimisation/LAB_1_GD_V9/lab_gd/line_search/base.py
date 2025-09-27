"""Interfaces for line-search strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

import numpy as np

__all__ = ["LineSearch", "DirectionProvider"]


class DirectionProvider(Protocol):
    """Callable protocol returning a descent direction."""

    def __call__(self, gradient: np.ndarray) -> np.ndarray:
        """Return a descent direction given the gradient."""


class LineSearch(ABC):
    """Abstract base class for line-search algorithms."""

    @abstractmethod
    def __call__(
        self,
        objective: "Objective",
        point: np.ndarray,
        direction: np.ndarray,
        gradient: np.ndarray,
    ) -> float:
        """Compute a step length along ``direction`` starting from ``point``."""


class Objective(Protocol):
    """Protocol describing the subset of objective functionality required."""

    def value(self, x: np.ndarray | tuple) -> float | np.ndarray:  # pragma: no cover
        ...

    def gradient(self, x: np.ndarray) -> np.ndarray:  # pragma: no cover
        ...
