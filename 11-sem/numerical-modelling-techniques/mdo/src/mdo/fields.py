"""Поля течії від системи вихорів: швидкість, функція течії ψ, потенціал φ, допоміжні сітки."""
import numpy as np

from .kernels import induced, theta


def velocity(X, Y, xs, ys, gs, v_inf, delta):
    """Швидкість (7.1.16′), (7.2.22): потік + Σ γ V(від вихору)."""
    u, v = induced(X, Y, xs, ys, gs, delta)
    return v_inf[0] + u, v_inf[1] + v


def psi(X, Y, xs, ys, gs, v_inf, delta):
    """Функція течії (7.1.15′), (6.4.43): y·u∞ − x·v∞ − Σ γ/(2π)·ln R, R = max(δ, r)."""
    out = Y * v_inf[0] - X * v_inf[1]
    for x0, y0, g in zip(np.ravel(xs), np.ravel(ys), np.ravel(gs)):
        out = out - g / (2 * np.pi) * np.log(np.maximum(np.hypot(X - x0, Y - y0), delta))
    return out


def phi_direct(X, Y, xs, ys, gs, v_inf):
    """Потенціал за прямою формулою (7.1.13′), (7.2.38): розріз від кожного вихору."""
    out = X * v_inf[0] + Y * v_inf[1]
    for x0, y0, g in zip(np.ravel(xs), np.ravel(ys), np.ravel(gs)):
        out = out + g * theta(X, Y, x0, y0)
    return out


def chain_transformed(X, Y, x0, y0, G, v_inf, delta):
    """Перетворені формули (7.1.22′)–(7.1.23′) для ланцюжка вихорів контуру.

    Вихори → диполі в серединах відрізків з моментами S_j = Γ1 + … + Γj і один вихор Γ0 у
    кінці ω0M: потенціал має один розріз (або жодного при Γ0 = 0). Повертає (φ, ψ).
    """
    S = np.cumsum(G)[:-1]
    ddx, ddy = np.diff(x0), np.diff(y0)
    xm, ym = (x0[:-1] + x0[1:]) / 2, (y0[:-1] + y0[1:]) / 2
    g0 = G.sum()
    RM = np.maximum(np.hypot(X - x0[-1], Y - y0[-1]), delta)
    phi = X * v_inf[0] + Y * v_inf[1] + g0 * theta(X, Y, x0[-1], y0[-1])
    ps = Y * v_inf[0] - X * v_inf[1] - g0 / (2 * np.pi) * np.log(RM)
    for j in range(len(S)):
        Xj, Yj = X - xm[j], Y - ym[j]
        R2 = np.maximum(Xj**2 + Yj**2, delta**2)
        phi = phi + S[j] / (2 * np.pi) * (ddy[j] * Xj - ddx[j] * Yj) / R2
        ps = ps - S[j] / (2 * np.pi) * (ddx[j] * Xj + ddy[j] * Yj) / R2
    return phi, ps


def flow_box(v_inf, back, ahead, half):
    """Межі прямокутника, що охоплює смугу від −back до ahead уздовж потоку і ±half поперек."""
    e = np.array([-back, ahead])[:, None] * np.asarray(v_inf)
    p = np.array([-v_inf[1], v_inf[0]]) * half
    pts = np.r_[e + p, e - p]
    return (pts[:, 0].min(), pts[:, 0].max()), (pts[:, 1].min(), pts[:, 1].max())


def grid(xlim, ylim, nx=300):
    """Рівномірна сітка з однаковим кроком по x і y."""
    ny = max(2, int(round(nx * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0]))))
    return np.meshgrid(np.linspace(*xlim, nx), np.linspace(*ylim, ny))
