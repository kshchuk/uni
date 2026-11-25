"""Контур: дискретизація, нормування, непроникнення для рухомих точок."""
import numpy as np

from mdo import Contour


def test_semicircle_geometry():
    c = Contour.semicircle(24)
    assert c.M == 24 and len(c.xc) == 23
    assert abs(c.size - 1.0) < 1e-12
    assert abs(c.delta - np.pi * 0.5 / 48) < 1e-15            # δ = L/(2M)
    np.testing.assert_allclose(np.hypot(c.nx, c.ny), 1.0)
    assert list(c.separation) == [0, 23]


def digit_five(M=31):
    """Контур «5»: планка, стовпчик, дуга; 4 точки відриву (кінці й кути)."""
    A, B, C = np.array([0.5, 1.25]), np.array([-0.5, 1.25]), np.array([-0.5, 0.45])
    OC, RC = np.array([0.0, -0.32]), 0.93
    a0 = np.arctan2(C[1] - OC[1], C[0] - OC[0])
    a1 = np.radians(170) - 2 * np.pi
    seg = lambda P, Q, n: P + np.linspace(0, 1, n + 1)[:, None] * (Q - P)
    L = [1.0, 0.8, RC * abs(a1 - a0)]
    n_ab, n_bc = round((M - 1) * L[0] / sum(L)), round((M - 1) * L[1] / sum(L))
    ang = np.linspace(a0, a1, (M - 1) - n_ab - n_bc + 1)
    arc = OC + RC * np.column_stack([np.cos(ang), np.sin(ang)])
    P = np.vstack([seg(A, B, n_ab), seg(B, C, n_bc)[1:], arc[1:]])
    sep = [0, n_ab, n_ab + n_bc, M - 1]
    return Contour.from_points(P[:, 0], P[:, 1], separation=sep).normalized()


def test_polyline_corners_are_nodes():
    V = [(0.5, 1.25), (-0.5, 1.25), (-0.5, 0.45), (0.3, -0.5)]
    c = Contour.polyline(V, 31)
    assert c.M == 31 and len(c.separation) == 4
    P = np.column_stack([c.x0, c.y0])
    for v in V:
        assert np.min(np.hypot(*(P - v).T)) < 1e-12


def test_five_normalized():
    c = digit_five()
    assert abs(c.size - 1) < 1e-12 and len(c.separation) == 4
    assert c.delta < c.ell.min() / 2                             # колокації поза колами δ


def test_keep_out_polyline_blocks_crossing():
    """Точка, що «перестрибує» відрізок, лишається на своєму боці не ближче δ."""
    c = Contour.segment((0, -0.5), (0, 0.5), 11)
    xo, yo = np.array([-0.1, 0.2]), np.array([0.0, 0.1])
    xn, yn = np.array([0.1, 0.01]), np.array([0.05, 0.1])
    x, y = c.keep_out(xo, yo, xn, yn)
    assert x[0] <= -c.delta + 1e-12                              # перетнув зліва → лишився зліва
    assert x[1] >= c.delta - 1e-12                               # впритул справа → відсунутий


def test_keep_out_arc_blocks_crossing():
    c = Contour.semicircle(24)
    cx, cy, R, *_ = c.arc
    xo, yo = np.array([cx - 0.8]), np.array([0.0])               # зовні, зліва від дуги
    xn, yn = np.array([cx - 0.3]), np.array([0.0])               # усередині «чаші»
    x, y = c.keep_out(xo, yo, xn, yn)
    assert np.hypot(x - cx, y - cy)[0] >= R + c.delta - 1e-12
