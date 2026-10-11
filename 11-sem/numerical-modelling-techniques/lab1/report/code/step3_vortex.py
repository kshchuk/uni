def vortex_velocity(x, y, x0j, y0j, delta=0.0):
    """(u, v) від вихору Γ = 1 у точці (x0j, y0j): формули (7.1.17), (7.1.18)."""
    dx = x - x0j
    dy = y - y0j
    R2 = np.maximum(dx**2 + dy**2, delta**2)    # регуляризація: R ≥ delta
    return -dy / (2 * np.pi * R2), dx / (2 * np.pi * R2)


DELTA = h / 2                    # кола сусідніх вихорів дотикаються [Л2, сл. 31]
print(f"DELTA = {DELTA:.4f}")
