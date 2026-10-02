def theta(x, y, x0j, y0j):
    """Круговий арктангенс (7.1.14): arg(z - ω0j) / 2π у межах [0, 1)."""
    return np.mod(np.arctan2(y - y0j, x - x0j), 2 * np.pi) / (2 * np.pi)


def phi_direct(X, Y, x0, y0, G, v_inf):
    """Пряма формула (7.1.13') — з розрізами від кожного вихору."""
    phi = X * v_inf[0] + Y * v_inf[1]
    for j in range(len(G)):
        phi += G[j] * theta(X, Y, x0[j], y0[j])
    return phi


def transformed(X, Y, x0, y0, G, v_inf, delta):
    """Перетворені формули (7.1.22'), (7.1.23'): диполі + вихор Γ0 у ω0M."""
    S = np.cumsum(G)[:-1]                        # S_j = Γ1 + ... + Γj, j = 1..M-1
    ddx, ddy = np.diff(x0), np.diff(y0)          # прирости вздовж контуру
    xm, ym = (x0[:-1] + x0[1:]) / 2, (y0[:-1] + y0[1:]) / 2   # середини ζj
    g0 = G.sum()
    RM = np.maximum(np.hypot(X - x0[-1], Y - y0[-1]), delta)
    phi = X * v_inf[0] + Y * v_inf[1] + g0 * theta(X, Y, x0[-1], y0[-1])
    psi = Y * v_inf[0] - X * v_inf[1] - g0 / (2 * np.pi) * np.log(RM)
    for j in range(len(S)):
        Xj, Yj = X - xm[j], Y - ym[j]
        R2 = np.maximum(Xj**2 + Yj**2, delta**2)
        phi += S[j] / (2 * np.pi) * (ddy[j] * Xj - ddx[j] * Yj) / R2
        psi -= S[j] / (2 * np.pi) * (ddx[j] * Xj + ddy[j] * Yj) / R2
    return phi, psi


phi, psi_t = transformed(X, Y, x0, y0, G, V_INF, DELTA)
far = np.min(np.hypot(X[..., None] - x0, Y[..., None] - y0), axis=-1) > 0.1
print(f"max|ψ - ψ_t| далі 0.1 від контуру: {np.abs(psi - psi_t)[far].max():.1e}")
