import numpy as np

from lab_gd import (
    BacktrackingLineSearch,
    GoldsteinCondition,
    GradientDescent,
    IterationHistory,
    QuadraticForm,
    SimpleDecrease,
    variant9_objective,
)


def test_quadratic_form_value_on_grid():
    objective = variant9_objective()
    grid = np.linspace(-1.0, 1.0, 5)
    x1, x2, x3 = np.meshgrid(grid, grid, grid, indexing="xy")
    values = objective.value((x1, x2, x3))
    assert values.shape == x1.shape


def test_gradient_descent_simple_condition():
    objective = variant9_objective()
    line_search = BacktrackingLineSearch(SimpleDecrease())
    optimizer = GradientDescent(line_search=line_search, tolerance=1e-8, max_iterations=100)
    history = IterationHistory()

    start = np.array([1.0, 1.0, 1.0])
    xmin = optimizer.minimise(objective, start, history)

    assert np.linalg.norm(xmin) < 1e-6
    assert abs(objective.value(xmin) - 5.0) < 1e-6
    assert len(history.points) >= 1
    assert len(history.steps) == len(history.points) - 1


def test_gradient_descent_goldstein_condition():
    objective = variant9_objective()
    line_search = BacktrackingLineSearch(GoldsteinCondition(0.25))
    optimizer = GradientDescent(line_search=line_search, tolerance=1e-8, max_iterations=200)

    start = np.array([-10.0, 10.0, 1.0])
    xmin = optimizer.minimise(objective, start)

    assert np.linalg.norm(xmin) < 1e-5
    assert abs(objective.value(xmin) - 5.0) < 1e-5

