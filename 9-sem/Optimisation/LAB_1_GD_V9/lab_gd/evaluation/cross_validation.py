"""Cross-validation utilities for optimiser hyperparameters."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Callable, Iterable, List, Mapping, Sequence

import numpy as np

from ..line_search.base import Objective
from ..optimizers.base import Optimizer
from ..utils.history import IterationHistory

__all__ = [
    "CrossValidationResult",
    "parameter_grid",
    "cross_validate",
]

Metric = Callable[[IterationHistory], float]
OptimizerFactory = Callable[[Mapping[str, Any]], Optimizer]
HistoryFactory = Callable[[], IterationHistory]


@dataclass(frozen=True)
class CrossValidationResult:
    """Stores scores obtained for a single parameter configuration."""

    params: Mapping[str, Any]
    scores: Sequence[float]

    @property
    def mean_score(self) -> float:
        """Return the average score across folds."""

        return float(np.mean(self.scores))


def parameter_grid(definition: Mapping[str, Sequence[Any]]) -> Iterable[Mapping[str, Any]]:
    """Yield dictionaries describing all combinations of parameters."""

    keys = list(definition.keys())
    values = [definition[key] for key in keys]
    for combination in product(*values):
        yield {key: value for key, value in zip(keys, combination)}


def _default_metric(history: IterationHistory) -> float:
    if not history.values:
        raise ValueError("history must contain recorded values")
    return float(history.values[-1])


def _make_folds(num_points: int, folds: int, shuffle: bool, rng: np.random.Generator) -> List[np.ndarray]:
    if folds <= 0:
        raise ValueError("folds must be positive")
    if num_points < folds:
        raise ValueError("Number of points must be >= folds")

    indices = np.arange(num_points)
    if shuffle:
        rng.shuffle(indices)

    return np.array_split(indices, folds)


def cross_validate(
    objective: Objective,
    optimizer_factory: OptimizerFactory,
    params: Mapping[str, Sequence[Any]],
    initial_points: Sequence[np.ndarray],
    folds: int = 3,
    *,
    metric: Metric | None = None,
    history_factory: HistoryFactory | None = None,
    shuffle: bool = True,
    random_state: int | None = None,
) -> List[CrossValidationResult]:
    """Evaluate parameter combinations using K-fold cross validation.

    Args:
        objective (Objective): Objective function to minimise.
        optimizer_factory (Callable): Builds an optimiser from a parameter dict.
        params (Mapping[str, Sequence[Any]]): Parameter grid definition.
        initial_points (Sequence[np.ndarray]): Points used as validation seeds.
        folds (int): Number of folds.
        metric (Callable): Scoring function applied to each history.
        history_factory (Callable): Creates history recorders. Defaults to ``IterationHistory``.
        shuffle (bool): Shuffle points before splitting.
        random_state (int | None): Seed for reproducibility.

    Returns:
        List[CrossValidationResult]: Scores for each parameter set.
    """

    metric_fn = metric or _default_metric
    make_history = history_factory or IterationHistory

    points = [np.asarray(p, dtype=float) for p in initial_points]
    if not points:
        raise ValueError("initial_points must not be empty")
    dimension = points[0].shape
    if any(p.shape != dimension for p in points):
        raise ValueError("All initial points must share the same shape")

    rng = np.random.default_rng(random_state)
    fold_indices = _make_folds(len(points), folds, shuffle, rng)

    results: List[CrossValidationResult] = []
    for combination in parameter_grid(params):
        param_copy = dict(combination)
        scores: List[float] = []
        for fold in fold_indices:
            if fold.size == 0:
                continue
            fold_scores: List[float] = []
            for idx in fold:
                history = make_history()
                optimizer = optimizer_factory(dict(param_copy))
                optimizer.minimise(objective, points[idx], history)
                fold_scores.append(metric_fn(history))
            scores.append(float(np.mean(fold_scores)))
        results.append(CrossValidationResult(params=param_copy, scores=tuple(scores)))

    return results
