"""Reusable toolkit for the Variant 9 gradient-descent laboratory."""

from .descent import (
    DescentHistory,
    euclidean_norm,
    gradient_descent,
    goldstein_condition,
    simple_decrease_condition,
)
from .line_search import LineSearchResult, backtracking
from .problem import CONSTANT_TERM, Q, gradient, minimiser, minimum_value, objective

__all__ = [
    "CONSTANT_TERM",
    "Q",
    "objective",
    "gradient",
    "minimiser",
    "minimum_value",
    "DescentHistory",
    "euclidean_norm",
    "gradient_descent",
    "backtracking",
    "LineSearchResult",
    "goldstein_condition",
    "simple_decrease_condition",
]

__version__ = "0.1.0"
