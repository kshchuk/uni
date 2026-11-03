def vortex_velocity(x, y, x0j, y0j, delta=0.0):
    """(u, v) від вихору Γ = 1 у точці (x0j, y0j): формули (7.2.23)-(7.2.26)."""
    dx = x - x0j
    dy = y - y0j
    R2 = np.maximum(dx**2 + dy**2, delta**2)    # регуляризація: R ≥ delta
    return -dy / (2 * np.pi * R2), dx / (2 * np.pi * R2)


def induced(x, y, xs, ys, gs, delta, chunk=4000):
    """Сумарна швидкість у точках (x, y) від вихорів (xs, ys) з інтенсивностями gs."""
    u = np.zeros(len(x))
    v = np.zeros(len(x))
    for s in range(0, len(x), chunk):           # шматками, щоб не забити пам'ять
        U, V = vortex_velocity(x[s:s + chunk, None], y[s:s + chunk, None],
                               xs[None, :], ys[None, :], delta)
        u[s:s + chunk] = U @ gs
        v[s:s + chunk] = V @ gs
    return u, v


def velocity(x, y, G, fx, fy, fg):
    """Швидкість (7.2.30): потік + приєднані вихори Γj + вільні вихори сліду γi."""
    ub, vb = induced(x, y, x0, y0, G, DELTA)
    uf, vf = induced(x, y, fx, fy, fg, DELTA)
    return V_INF[0] + ub + uf, V_INF[1] + vb + vf
