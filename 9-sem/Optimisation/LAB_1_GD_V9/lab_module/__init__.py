"""
Lab Module: Gradient Descent Optimization with Line Search

A comprehensive library for gradient-based optimization with various
line search strategies and visualization tools.

Main Components:
    - objectives: Differentiable objective functions (quadratic, etc.)
    - line_search: Line search conditions and algorithms
    - optimizers: Gradient descent with backtracking
    - visualization: 3D plots, convergence metrics, animations

Example:
    >>> from lab_module import (
    ...     build_variant9_objective,
    ...     gd_back_tracking,
    ...     goldstein_cond,
    ...     plot_metrics
    ... )
    >>> 
    >>> # Create objective function
    >>> obj = build_variant9_objective()
    >>> 
    >>> # Run optimization
    >>> x0 = [1.0, 1.0, 1.0]
    >>> x_min, history = gd_back_tracking(
    ...     obj.value,
    ...     obj.gradient,
    ...     x0,
    ...     cond=goldstein_cond,
    ...     max_iters=2000,
    ...     tol=1e-6
    ... )
    >>> 
    >>> # Visualize results
    >>> fig = plot_metrics(history)
    >>> fig.show()
"""

from .objectives import (
    DifferentiableObjective,
    QuadraticObjective,
    build_variant9_objective,
)

from .line_search import (
    LineSearchCondition,
    split_step_cond,
    goldstein_cond,
    back_tracking,
)

from .optimizers import (
    OptimizationHistory,
    norm2,
    gd_back_tracking,
)

from .visualization import (
    surface_for_slice,
    show_isosurface_with_path,
    plot_metrics,
    save_video_xyz,
)

__all__ = [
    # Objectives
    "DifferentiableObjective",
    "QuadraticObjective",
    "build_variant9_objective",
    # Line Search
    "LineSearchCondition",
    "split_step_cond",
    "goldstein_cond",
    "back_tracking",
    # Optimizers
    "OptimizationHistory",
    "norm2",
    "gd_back_tracking",
    # Visualization
    "surface_for_slice",
    "show_isosurface_with_path",
    "plot_metrics",
    "save_video_xyz",
]

__version__ = "1.0.0"
