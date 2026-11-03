def time_step(G, fx, fy, fg, shed_total):
    """Один крок t_n -> t_n+1 за (7.2.28)-(7.2.36)."""
    # 1) кінцеві вихори відриваються: γ^p_{n+1} = Γ_p(t_n), p = 1 і M
    px = np.append(fx, [x0[0], x0[-1]])
    py = np.append(fy, [y0[0], y0[-1]])
    pg = np.append(fg, [G[0], G[-1]])
    # 2) швидкості всіх вільних вихорів у момент t_n (7.2.31)
    u, v = velocity(px, py, G, fx, fy, fg)
    dt = DELTA / np.max(np.hypot(u, v))         # крок за часом (7.2.27)
    # 3) пересування (7.2.32) і непроникнення для рухомих точок
    px, py = keep_out(px, py, px + u * dt, py + v * dt)
    shed_total += G[0] + G[-1]
    # 4) нові Γ1..ΓM із СЛАР (7.2.33)-(7.2.34)
    G = solve_gammas(px, py, pg, shed_total)
    return G, px, py, pg, shed_total, dt


def impulse(G, fx, fy, fg):
    """Гідродинамічний імпульс системи вихорів (ділений на ρ): Σ Γ (y, -x)."""
    return np.array([G @ y0 + fg @ fy, -(G @ x0) - fg @ fx])
