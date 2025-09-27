"""Gradient descent lab package."""

from .objectives.quadratic import QuadraticForm
from .objectives.variant9 import variant9_objective
from .optimizers.gradient_descent import GradientDescent
from .line_search.backtracking import BacktrackingLineSearch
from .line_search.conditions import SimpleDecrease, GoldsteinCondition
from .utils.history import IterationHistory
from .evaluation.cross_validation import CrossValidationResult, cross_validate, parameter_grid

__all__ = [
    "QuadraticForm",
    "variant9_objective",
    "GradientDescent",
    "BacktrackingLineSearch",
    "SimpleDecrease",
    "GoldsteinCondition",
    "IterationHistory",
    "CrossValidationResult",
    "cross_validate",
    "parameter_grid",
]
