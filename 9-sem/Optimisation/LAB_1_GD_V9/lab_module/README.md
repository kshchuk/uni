# Lab Module: Gradient Descent Optimization

A comprehensive Python library for gradient-based optimization with various line search strategies and visualization tools.

## Features

- **Multiple Line Search Conditions**: Simple backtracking (Armijo), Goldstein conditions
- **Gradient Descent Optimizer**: Fully configurable with convergence monitoring
- **Quadratic Objectives**: Easy-to-use interface for quadratic optimization problems
- **Rich Visualizations**: 3D isosurfaces, convergence plots, animated trajectories
- **Type-Safe**: Full type hints with Protocol-based interfaces
- **Well-Documented**: Google-style docstrings for all public APIs

## Installation

The module is already included in this project. Just ensure you have the dependencies:

```bash
pip install numpy plotly matplotlib pandas
```

For video generation, you also need `ffmpeg`:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

## Quick Start

```python
import numpy as np
from lab_module import (
    build_variant9_objective,
    gd_back_tracking,
    goldstein_cond,
    plot_metrics,
)

# Create objective function
obj = build_variant9_objective()

# Run optimization
x0 = np.array([1.0, 1.0, 1.0])
x_min, history = gd_back_tracking(
    f=obj.value,
    grad_f=obj.gradient,
    x0=x0,
    cond=goldstein_cond,
    max_iters=2000,
    tol=1e-6,
)

# Visualize results
fig = plot_metrics(history)
fig.show()

print(f"Minimum: {x_min}")
print(f"f(x*): {obj(x_min)}")
```

## Module Structure

```
lab_module/
├── __init__.py           # Package initialization, exports
├── objectives.py         # Objective function interfaces and implementations
├── line_search.py        # Line search conditions and algorithms
├── optimizers.py         # Optimization algorithms (gradient descent)
└── visualization.py      # Plotting and animation utilities
```

## Core Components

### 1. Objective Functions (`objectives.py`)

**Protocol Interface:**
```python
class DifferentiableObjective(Protocol):
    @property
    def dimension(self) -> int: ...
    def value(self, x: np.ndarray) -> float: ...
    def gradient(self, x: np.ndarray) -> np.ndarray: ...
    def __call__(self, x: np.ndarray) -> float: ...
```

**Quadratic Implementation:**
```python
obj = QuadraticObjective(
    Q=np.array([[2.0, 0.0], [0.0, 1.0]]),
    b=np.zeros(2),
    c=0.0,
)
```

**Factory for Variant 9:**
```python
obj = build_variant9_objective()
# Creates: f(x) = 200x₁² + 5x₂² + 144x₃² - 24x₁x₂ - 48x₁x₃ + 24x₂x₃ + 5
```

### 2. Line Search (`line_search.py`)

**Simple Backtracking (Armijo):**
```python
from lab_module import split_step_cond

x_min, history = gd_back_tracking(
    f, grad_f, x0,
    cond=split_step_cond,  # f(x + t*p) < f(x)
)
```

**Goldstein Conditions:**
```python
from lab_module import goldstein_cond

x_min, history = gd_back_tracking(
    f, grad_f, x0,
    cond=goldstein_cond,  # Two-sided bounds
    c=0.1,  # Goldstein parameter
)
```

**Custom Line Search:**
```python
from lab_module import back_tracking

t = back_tracking(
    f, grad_f, x, p=-gradient,
    cond=goldstein_cond,
    t0=1.0,      # Initial step size
    beta=0.5,    # Shrinking factor
    c=0.1,       # Condition parameter
)
```

### 3. Optimizers (`optimizers.py`)

**Gradient Descent:**
```python
from lab_module import gd_back_tracking

x_min, history = gd_back_tracking(
    f=objective_function,
    grad_f=gradient_function,
    x0=starting_point,
    cond=split_step_cond,  # or goldstein_cond
    max_iters=2000,
    tol=1e-6,
    t0=1.0,
    beta=0.5,
    c=0.1,
)
```

**History Dictionary:**
```python
history = {
    'x': [x0, x1, x2, ...],        # Points visited
    'f': [f0, f1, f2, ...],        # Function values
    't': [t0, t1, t2, ...],        # Step sizes used
    'grad_norm': [g0, g1, g2, ...] # Gradient norms
}
```

### 4. Visualization (`visualization.py`)

**Convergence Metrics:**
```python
from lab_module import plot_metrics

fig = plot_metrics(
    history,
    title="Optimization Progress",
    log_f=True,      # Log scale for f(x)
    log_grad=True,   # Log scale for gradient norm
    x_range=(0, 50), # Show first 50 iterations
)
fig.show()
```

**3D Isosurface:**
```python
from lab_module import show_isosurface_with_path

fig = show_isosurface_with_path(
    f=objective_function,
    history=history,
    grid_range=(-1.2, 1.2),
    vol_n=50,
    level=10.0,    # Isosurface level
    opacity=0.5,
)
fig.show()
```

**Animated Trajectory:**
```python
from lab_module import save_video_xyz

save_video_xyz(
    history,
    filename="optimization_path.mp4",
    fps=8,
)
```

## Design Patterns

The module follows SOLID principles and uses several design patterns:

1. **Strategy Pattern**: Different line search conditions (`split_step_cond`, `goldstein_cond`) can be swapped without changing optimizer code.

2. **Protocol Pattern**: `DifferentiableObjective` defines interface without inheritance, allowing duck typing.

3. **Factory Pattern**: `build_variant9_objective()` creates configured objective instances.

4. **Separation of Concerns**: Clear boundaries between optimization logic, line search, and visualization.

## Examples

See `demo_module_usage.ipynb` for comprehensive examples including:

- Basic optimization with different line search methods
- Convergence visualization
- 3D isosurface visualization
- Multiple starting points comparison
- Custom objective functions
- Video generation

## API Reference

### Objectives

- `DifferentiableObjective`: Protocol for objective functions
- `QuadraticObjective(Q, b, c)`: Quadratic objective implementation
- `build_variant9_objective()`: Factory for variant 9 objective

### Line Search

- `split_step_cond(...)`: Simple sufficient decrease
- `goldstein_cond(...)`: Goldstein conditions (two-sided)
- `back_tracking(...)`: Backtracking line search algorithm

### Optimizers

- `gd_back_tracking(...)`: Gradient descent with backtracking
- `norm2(v)`: Euclidean norm

### Visualization

- `plot_metrics(history, ...)`: Convergence plots
- `show_isosurface_with_path(...)`: 3D isosurface with path
- `surface_for_slice(...)`: 2D slice of 3D surface
- `save_video_xyz(...)`: Generate MP4 animation

## Type Hints

All public functions have complete type hints:

```python
def gd_back_tracking(
    f: Callable[[np.ndarray], float],
    grad_f: Callable[[np.ndarray], np.ndarray],
    x0: np.ndarray,
    cond: LineSearchCondition | None = None,
    max_iters: int = 2000,
    tol: float = 1e-6,
    t0: float = 1.0,
    beta: float = 0.5,
    c: float = 0.1,
) -> tuple[np.ndarray, OptimizationHistory]:
    ...
```

## Testing

You can test the module by running the demo notebook:

```bash
jupyter notebook demo_module_usage.ipynb
```

## License

This module is part of the Optimization course lab work (Variant 9).

## Author

Yaroslav
