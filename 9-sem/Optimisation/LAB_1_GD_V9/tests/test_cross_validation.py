import numpy as np
import pytest

from lab_gd import (
    BacktrackingLineSearch,
    CrossValidationResult,
    GradientDescent,
    SimpleDecrease,
    cross_validate,
    parameter_grid,
    variant9_objective,
)


def test_parameter_grid_cartesian_product():
    grid = {"a": [1, 2], "b": ["x", "y"]}
    combinations = list(parameter_grid(grid))
    assert len(combinations) == 4
    observed = {(combo["a"], combo["b"]) for combo in combinations}
    expected = {(1, "x"), (1, "y"), (2, "x"), (2, "y")}
    assert observed == expected


def test_cross_validate_returns_scores():
    objective = variant9_objective()

    def factory(params):
        line_search = BacktrackingLineSearch(
            condition=SimpleDecrease(),
            initial_step=params["initial_step"],
        )
        return GradientDescent(line_search=line_search, tolerance=1e-8, max_iterations=80)

    grid = {"initial_step": [0.5, 1.0]}
    points = [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
        np.array([0.5, -0.5, 0.5]),
    ]

    results = cross_validate(objective, factory, grid, points, folds=2, random_state=42)
    assert len(results) == 2
    for result in results:
        assert isinstance(result, CrossValidationResult)
        assert len(result.scores) == 2
        assert all(score >= 5.0 for score in result.scores)
        assert pytest.approx(result.mean_score, rel=1e-6) >= 5.0


def test_cross_validate_requires_points():
    objective = variant9_objective()

    def factory(params):
        line_search = BacktrackingLineSearch(condition=SimpleDecrease())
        return GradientDescent(line_search=line_search)

    with pytest.raises(ValueError):
        cross_validate(objective, factory, {"step": [1.0]}, [], folds=2)


def test_cross_validate_validates_point_shapes():
    objective = variant9_objective()

    def factory(params):
        return GradientDescent(line_search=BacktrackingLineSearch(SimpleDecrease()))

    points = [np.zeros(3), np.zeros(2)]
    with pytest.raises(ValueError):
        cross_validate(objective, factory, {"dummy": [1]}, points, folds=2)
