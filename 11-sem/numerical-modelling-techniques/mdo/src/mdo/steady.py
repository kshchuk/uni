"""Лаб. №1: стаціонарна течія навколо контуру із заданою циркуляцією Γ0 [П, §7.1]."""
from dataclasses import dataclass

import numpy as np

from . import fields
from .contour import Contour
from .kernels import vortex_velocity


def influence_matrix(contour: Contour):
    """Матриця СЛАР: A_kj = n_k · V_j(x_k, y_k) (k < M), останній рядок — одиниці.

    Ліва частина (7.1.19)–(7.1.20) і (7.2.19)–(7.2.20); без регуляризації — колокації не
    збігаються з вихорами.
    """
    c = contour
    U, V = vortex_velocity(c.xc[:, None], c.yc[:, None], c.x0[None, :], c.y0[None, :])
    A = np.empty((c.M, c.M))
    A[:-1] = c.nx[:, None] * U + c.ny[:, None] * V
    A[-1] = 1.0
    return A


def solve_steady(contour: Contour, v_inf=(1.0, 0.0), gamma0=0.0):
    """Інтенсивності Γ1..ΓM з СЛАР (7.1.19)–(7.1.20)."""
    c = contour
    v_inf = np.asarray(v_inf, float)
    b = np.empty(c.M)
    b[:-1] = -(c.nx * v_inf[0] + c.ny * v_inf[1])
    b[-1] = gamma0
    return np.linalg.solve(influence_matrix(c), b)


@dataclass
class SteadySolution:
    """Розв'язок лаб. №1: контур, потік, Γ0 і знайдені Γj; поля на будь-якій сітці."""
    contour: Contour
    v_inf: np.ndarray
    gamma0: float
    G: np.ndarray

    @classmethod
    def solve(cls, contour, v_inf=(1.0, 0.0), gamma0=0.0):
        v_inf = np.asarray(v_inf, float)
        return cls(contour, v_inf, gamma0, solve_steady(contour, v_inf, gamma0))

    def _delta(self, delta):
        return self.contour.delta if delta is None else delta

    def velocity(self, X, Y, delta=None):
        """Швидкість (7.1.16′) з регуляризацією (7.1.18)."""
        c = self.contour
        return fields.velocity(X, Y, c.x0, c.y0, self.G, self.v_inf, self._delta(delta))

    def psi(self, X, Y, delta=None, transformed=False):
        """Функція течії: пряма (7.1.15′) або перетворена (7.1.23′)."""
        c = self.contour
        if transformed:
            return fields.chain_transformed(X, Y, c.x0, c.y0, self.G, self.v_inf,
                                            self._delta(delta))[1]
        return fields.psi(X, Y, c.x0, c.y0, self.G, self.v_inf, self._delta(delta))

    def phi(self, X, Y, delta=None, transformed=True):
        """Потенціал: перетворений (7.1.22′, один розріз) або прямий (7.1.13′, M розрізів)."""
        c = self.contour
        if transformed:
            return fields.chain_transformed(X, Y, c.x0, c.y0, self.G, self.v_inf,
                                            self._delta(delta))[0]
        return fields.phi_direct(X, Y, c.x0, c.y0, self.G, self.v_inf)

    def residual(self):
        """max |V·n| у колокаціях (без регуляризації) — має бути ~1e-15."""
        c = self.contour
        u, v = fields.velocity(c.xc, c.yc, c.x0, c.y0, self.G, self.v_inf, 0.0)
        return np.max(np.abs(u * c.nx + v * c.ny))
