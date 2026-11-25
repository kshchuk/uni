"""Лаб. №1: числа, вже перевірені в гайді й звіті."""
import numpy as np
import pytest

from mdo import Contour, SteadySolution

V = (1.0, 0.0)


@pytest.mark.parametrize("g0, G_ref, point_ref", [
    (0.0, [0.859029, 0.245437, 0.0, -0.245437, -0.859029], (0.7517, 0.2009, -0.7204, 0.2066)),
    (1.0, [1.132467, 0.401687, 0.140625, -0.089187, -0.585592], (0.6931, -0.0032, -0.2844, 0.2721)),
])
def test_control_example(g0, G_ref, point_ref):
    """Контрольний приклад: відрізок, M = 5, точка (−0.5, 0.3), δ = 0.01."""
    s = SteadySolution.solve(Contour.segment((0, -0.5), (0, 0.5), 5), V, g0)
    np.testing.assert_allclose(s.G, G_ref, atol=1e-6)
    x, y = np.array([-0.5]), np.array([0.3])
    u, v = s.velocity(x, y, 0.01)
    got = (u[0], v[0], s.phi(x, y, 0.01)[0], s.psi(x, y, 0.01, transformed=True)[0])
    np.testing.assert_allclose(got, point_ref, atol=1e-4)


@pytest.mark.parametrize("g0", [-1.0, 0.0, 1.0])
def test_semicircle_slae(g0):
    """Півколо M = 80: ΣΓ = Γ0 і непроникнення в колокаціях з машинною точністю."""
    s = SteadySolution.solve(Contour.semicircle(80), V, g0)
    assert abs(s.G.sum() - g0) < 1e-12
    assert s.residual() < 1e-12


def test_psi_direct_vs_transformed():
    """ψ за прямою і перетвореною формулами збігаються далі 0.1 від контуру (лаб. №1: 1.8e-4)."""
    c = Contour.semicircle(80)
    s = SteadySolution.solve(c, V, 1.0)
    X, Y = np.meshgrid(np.linspace(-1, 1, 120), np.linspace(-1, 1, 120))
    d = s.contour.h / 2
    far = np.min(np.hypot(X[..., None] - c.x0, Y[..., None] - c.y0), axis=-1) > 0.1
    diff = np.abs(s.psi(X, Y, d) - s.psi(X, Y, d, transformed=True))[far]
    assert diff.max() < 3e-4


def plate_exact(X, Y, gamma, a=0.5):
    """Точна швидкість для пластини x = 0, |y| ≤ a у потоці (1, 0) з циркуляцією gamma."""
    zp = -1j * (X + 1j * Y)
    root = np.sqrt(zp - a) * np.sqrt(zp + a)
    dw = np.cos(-np.pi / 2) - 1j * np.sin(-np.pi / 2) * zp / root + gamma / (2j * np.pi * root)
    vbar = -1j * dw
    return vbar.real, -vbar.imag


@pytest.mark.parametrize("g0, ref", [(0.0, [0.128, 0.060, 0.029]), (1.0, [0.162, 0.076, 0.037])])
def test_plate_convergence(g0, ref):
    """Похибка МДО проти точного розв'язку для пластини спадає ~1/M."""
    xp = np.linspace(-1, 1, 201)
    X, Y = np.meshgrid(xp, xp)
    mask = np.hypot(X, np.maximum(np.abs(Y) - 0.5, 0)) > 0.15
    errs = []
    for m in (10, 20, 40):
        s = SteadySolution.solve(Contour.segment((0, -0.5), (0, 0.5), m), V, g0)
        u, v = s.velocity(X, Y, 0.01)
        with np.errstate(divide="ignore", invalid="ignore"):
            ue, ve = plate_exact(X, Y, g0)
        errs.append(np.max(np.hypot(u - ue, v - ve)[mask]))
    np.testing.assert_allclose(errs, ref, rtol=0.05, atol=1e-3)


@pytest.mark.parametrize("g0, tol", [(0.0, 1e-5), (2.0, 1e-3)])
def test_cylinder(g0, tol):
    """Коло з розривом 4° (M = 80) проти точного розв'язку для циліндра."""
    gap, R = np.radians(4), 0.5
    c = Contour.arc_of_circle((0, 0), R, gap / 2, 2 * np.pi - gap / 2, 80)
    s = SteadySolution.solve(c, V, g0)
    xg = np.linspace(-1.2, 1.2, 101)
    X, Y = np.meshgrid(xg, xg)
    out = np.hypot(X, Y) >= 0.7
    u, v = s.velocity(X, Y, 0.01)
    z = X + 1j * Y
    with np.errstate(divide="ignore", invalid="ignore"):
        vbar = 1 - R**2 / z**2 + g0 / (2j * np.pi * z)
    assert np.max(np.hypot(u - vbar.real, v + vbar.imag)[out]) < tol
