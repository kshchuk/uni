"""Variant 9 objective definition."""

from __future__ import annotations

import numpy as np

from .quadratic import QuadraticForm

__all__ = ["variant9_objective"]


def variant9_objective() -> QuadraticForm:
    """Return the quadratic objective for variant 9."""

    matrix = np.array(
        [
            [400.0, -24.0, -48.0],
            [-24.0, 10.0, 24.0],
            [-48.0, 24.0, 288.0],
        ]
    )
    return QuadraticForm(matrix=matrix, constant=5.0)

