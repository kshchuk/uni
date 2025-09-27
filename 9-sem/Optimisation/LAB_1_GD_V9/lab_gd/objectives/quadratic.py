"""Quadratic objective functions used in optimisation experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

__all__ = ["QuadraticForm"]


@dataclass(frozen=True)
class QuadraticForm:
    """Quadratic form ``0.5 x^T A x + b^T x + c``.

    Args:
        matrix (np.ndarray): Symmetric positive definite matrix ``A``.
        linear (np.ndarray): Linear term ``b``. Defaults to zeros.
        constant (float): Constant term ``c``. Defaults to 0.0.

    Raises:
        ValueError: If shapes of ``matrix`` and ``linear`` are incompatible.
    """

    matrix: np.ndarray
    linear: np.ndarray | None = None
    constant: float = 0.0

    def __post_init__(self) -> None:
        matrix = np.asarray(self.matrix, dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("matrix must be square")
        object.__setattr__(self, "matrix", matrix)
        if self.linear is None:
            linear = np.zeros(matrix.shape[0], dtype=float)
        else:
            linear = np.asarray(self.linear, dtype=float)
            if linear.shape != (matrix.shape[0],):
                raise ValueError("linear term shape must match matrix dimensions")
        object.__setattr__(self, "linear", linear)
        object.__setattr__(self, "constant", float(self.constant))

    @property
    def dimension(self) -> int:
        """int: Dimensionality of the quadratic form."""

        return self.matrix.shape[0]

    def value(self, x: Iterable[float] | np.ndarray) -> float | np.ndarray:
        """Evaluate the quadratic form at ``x``.

        Supports both single points and array-like grids where the
        first axis enumerates the coordinates.
        """

        vec = np.asarray(x, dtype=float)
        if vec.shape == (self.dimension,):
            return float(0.5 * vec @ self.matrix @ vec + self.linear @ vec + self.constant)

        if vec.ndim >= 2 and vec.shape[0] == self.dimension:
            flat = vec.reshape(self.dimension, -1)
            quad = 0.5 * np.sum(flat * (self.matrix @ flat), axis=0)
            linear = self.linear @ flat
            values = quad + linear + self.constant
            return values.reshape(vec.shape[1:])

        raise ValueError("Point has incompatible shape")

    def gradient(self, x: Iterable[float] | np.ndarray) -> np.ndarray:
        """Evaluate the gradient of the quadratic form at ``x``.

        Args:
            x (Iterable[float] | np.ndarray): Point in ``R^n``.

        Returns:
            np.ndarray: Gradient vector ``\nabla f(x)``.
        """

        vec = np.asarray(x, dtype=float)
        if vec.shape != (self.dimension,):
            raise ValueError("Point has incompatible shape")
        return self.matrix @ vec + self.linear

    def minimizer(self) -> np.ndarray:
        """Compute the minimiser ``x`` solving ``A x + b = 0``.

        Returns:
            np.ndarray: Minimising point.

        Raises:
            np.linalg.LinAlgError: If the system cannot be solved.
        """

        return np.linalg.solve(self.matrix, -self.linear)

    def minimum_value(self) -> float:
        """Compute the minimum value of the quadratic form."""

        xmin = self.minimizer()
        return self.value(xmin)
