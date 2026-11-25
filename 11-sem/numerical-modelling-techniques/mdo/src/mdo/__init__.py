"""mdo — метод дискретних особливостей для плоских задач обтікання контуру.

Лаб. №1 (стаціонарна течія з циркуляцією Γ0)::

    from mdo import Contour, SteadySolution
    sol = SteadySolution.solve(Contour.semicircle(80), v_inf=(1, 0), gamma0=1.0)

Лаб. №2 (нестаціонарна відривна течія, доріжка Кармана)::

    from mdo import Contour, Simulation
    sim = Simulation(Contour.semicircle(24)).run(80)
"""
from .contour import Contour
from .fields import chain_transformed, flow_box, grid, phi_direct, psi, velocity
from .kernels import induced, theta, vortex_velocity
from .plotting import plot_contour, plot_four, plot_wake
from .steady import SteadySolution, influence_matrix, solve_steady
from .unsteady import Simulation

__all__ = ["Contour", "SteadySolution", "Simulation", "solve_steady", "influence_matrix",
           "vortex_velocity", "induced", "theta", "velocity", "psi", "phi_direct",
           "chain_transformed", "flow_box", "grid", "plot_contour", "plot_four", "plot_wake"]
__version__ = "0.1.0"
