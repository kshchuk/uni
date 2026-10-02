def solve_gammas(x0, y0, xc, yc, nx, ny, v_inf, gamma0):
    """Розв'язує СЛАР (7.1.19)-(7.1.20) і повертає Γ1..ΓM."""
    n = len(x0)
    # U[k, j], V[k, j]: швидкість у k-й колокації від j-го вихору Γ = 1, delta = 0
    U, V = vortex_velocity(xc[:, None], yc[:, None], x0[None, :], y0[None, :])
    A = np.empty((n, n))
    b = np.empty(n)
    A[:-1] = nx[:, None] * U + ny[:, None] * V   # рядки непроникнення
    b[:-1] = -(nx * v_inf[0] + ny * v_inf[1])
    A[-1] = 1.0                                  # рядок циркуляції
    b[-1] = gamma0
    return np.linalg.solve(A, b)


G = solve_gammas(x0, y0, xc, yc, nx, ny, V_INF, GAMMA0)

U, V = vortex_velocity(xc[:, None], yc[:, None], x0[None, :], y0[None, :])
uc = V_INF[0] + U @ G                            # повна швидкість у колокаціях
vc = V_INF[1] + V @ G
print(f"sum Γ = {G.sum():.12f}, max|V·n| = {np.abs(uc * nx + vc * ny).max():.1e}")
