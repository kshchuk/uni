"""Variant 9 gradient descent laboratory module."""
from __future__ import annotations

from importlib import import_module
from typing import Any

from .objective import ArrayLike, gradient, hessian, objective
from .line_search import (
    LineSearch,
    LineSearchResult,
    goldstein_backtracking,
    goldstein_rule,
    simple_backtracking,
    simple_rule,
)
from .gradient_descent import (
    OptimizationHistory,
    OptimizationResult,
    gradient_descent,
)

__all__ = [
    "ArrayLike",
    "objective",
    "gradient",
    "hessian",
    "LineSearch",
    "LineSearchResult",
    "simple_backtracking",
    "goldstein_backtracking",
    "simple_rule",
    "goldstein_rule",
    "OptimizationHistory",
    "OptimizationResult",
    "gradient_descent",
    "DEFAULT_STARTS",
    "ExperimentConfig",
    "ExperimentOutcome",
    "build_default_suite",
    "run_experiment",
    "run_suite",
    "table",
    "isosurface",
    "surface_slice",
]

_EXPERIMENT_EXPORTS = {
    "DEFAULT_STARTS",
    "ExperimentConfig",
    "ExperimentOutcome",
    "build_default_suite",
    "run_experiment",
    "run_suite",
    "table",
}

_VISUAL_EXPORTS = {
    "isosurface",
    "surface_slice",
}


def __getattr__(name: str) -> Any:
    if name in _EXPERIMENT_EXPORTS:
        module = import_module(".experiments", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    if name in _VISUAL_EXPORTS:
        module = import_module(".visualization", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'lab_gd' has no attribute {name!r}")
