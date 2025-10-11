"""
Objective function interfaces and implementations.

This module provides Protocol-based interfaces for differentiable objective
functions and concrete implementations for common objective types.
"""

from dataclasses import dataclass
from typing import Protocol
import numpy as np


class DifferentiableObjective(Protocol):
    """
    Protocol for differentiable objective functions.

    Any class implementing this protocol can be used with optimization
    algorithms that require function values and gradients.
    """

    @property
    def dimension(self) -> int:
        """Number of variables in the optimization problem."""
        ...

    def value(self, x: np.ndarray) -> float:
        """
        Evaluate the objective function at point x.

        Args:
            x: Point at which to evaluate the function.

        Returns:
            Function value f(x).
        """
        ...

    def gradient(self, x: np.ndarray) -> np.ndarray:
        """
        Compute the gradient of the objective function at point x.

        Args:
            x: Point at which to compute the gradient.

        Returns:
            Gradient vector ∇f(x).
        """
        ...

    def __call__(self, x: np.ndarray) -> float:
        """
        Evaluate the objective function (same as value).

        Args:
            x: Point at which to evaluate the function.

        Returns:
            Function value f(x).
        """
        ...


@dataclass(frozen=True)
class QuadraticObjective(DifferentiableObjective):
    """
    Quadratic objective function: f(x) = x^T Q x + b^T x + c.

    This class represents quadratic functions commonly used in optimization.
    The function is defined by a symmetric matrix Q, linear term b, and
    constant c.

    Attributes:
        Q: Symmetric matrix defining quadratic term (n x n).
        b: Linear coefficient vector (n,).
        c: Constant term (scalar).

    Example:
        >>> Q = np.array([[2.0, 0.0], [0.0, 1.0]])
        >>> b = np.zeros(2)
        >>> c = 0.0
        >>> obj = QuadraticObjective(Q=Q, b=b, c=c)
        >>> x = np.array([1.0, 2.0])
        >>> print(obj(x))  # 2*1^2 + 1*2^2 = 6.0
    """

    Q: np.ndarray
    b: np.ndarray
    c: float

    @property
    def dimension(self) -> int:
        """Number of variables (dimension of x)."""
        return self.Q.shape[0]

    def value(self, x: np.ndarray) -> float:
        """
        Compute f(x) = x^T Q x + b^T x + c.

        Args:
            x: Point at which to evaluate (n,).

        Returns:
            Function value.
        """
        return float(np.einsum("i,ij,j->", x, self.Q, x) + np.dot(self.b, x) + self.c)

    def gradient(self, x: np.ndarray) -> np.ndarray:
        """
        Compute ∇f(x) = 2Qx + b.

        Args:
            x: Point at which to compute gradient (n,).

        Returns:
            Gradient vector (n,).
        """
        return 2.0 * self.Q @ x + self.b

    def __call__(self, x: np.ndarray) -> float:
        """Evaluate f(x) (alias for value)."""
        return self.value(x)


def build_variant9_objective() -> QuadraticObjective:
    """
    Build the objective function for Variant 9.

    Creates the quadratic objective:
        f(x) = 200x₁² + 5x₂² + 144x₃² - 24x₁x₂ - 48x₁x₃ + 24x₂x₃ + 5

    This can be written in matrix form as:
        f(x) = x^T Q x + c

    where Q is the matrix:
        [[200, -12, -24],
         [-12,   5,  12],
         [-24,  12, 144]]

    and c = 5.

    Returns:
        QuadraticObjective instance for Variant 9.

    Example:
        >>> obj = build_variant9_objective()
        >>> x = np.array([0.0, 0.0, 0.0])
        >>> print(obj(x))  # Should be 5.0
        5.0
    """
    Q = np.array(
        [
            [200.0, -12.0, -24.0],
            [-12.0, 5.0, 12.0],
            [-24.0, 12.0, 144.0],
        ]
    )
    b = np.zeros(3)
    c = 5.0

    return QuadraticObjective(Q=Q, b=b, c=c)


__all__ = [
    "DifferentiableObjective",
    "QuadraticObjective",
    "build_variant9_objective",
]
