def velocity_field(X, Y, x0, y0, G, v_inf, delta):
    """Поле швидкості (7.1.16')."""
    u = np.full_like(X, v_inf[0])
    v = np.full_like(X, v_inf[1])
    for j in range(len(G)):
        du, dv = vortex_velocity(X, Y, x0[j], y0[j], delta)
        u += G[j] * du
        v += G[j] * dv
    return u, v


def psi_direct(X, Y, x0, y0, G, v_inf, delta):
    """Функція течії (7.1.15')."""
    psi = Y * v_inf[0] - X * v_inf[1]
    for j in range(len(G)):
        Rj = np.maximum(np.hypot(X - x0[j], Y - y0[j]), delta)
        psi -= G[j] / (2 * np.pi) * np.log(Rj)
    return psi


u, v = velocity_field(X, Y, x0, y0, G, V_INF, DELTA)
speed = np.hypot(u, v)
psi = psi_direct(X, Y, x0, y0, G, V_INF, DELTA)
