# Матриця СЛАР залежить лише від геометрії контуру, тож будуємо її один раз
U, V = vortex_velocity(xc[:, None], yc[:, None], x0[None, :], y0[None, :])
A = np.empty((M, M))
A[:-1] = nx[:, None] * U + ny[:, None] * V      # ліва частина (7.2.19)
A[-1] = 1.0                                     # ліва частина (7.2.20)
A_inv = np.linalg.inv(A)


def solve_gammas(fx, fy, fg, shed_total):
    """Γ1..ΓM на новому кроці за (7.2.19)-(7.2.20).

    shed_total — сума інтенсивностей усіх вихорів, що відірвались від контуру.
    """
    uf, vf = induced(xc, yc, fx, fy, fg, DELTA)  # швидкість від сліду в колокаціях
    b = np.empty(M)
    b[:-1] = -(nx * (V_INF[0] + uf) + ny * (V_INF[1] + vf))
    b[-1] = -shed_total                          # повна циркуляція = 0 (Кельвін)
    return A_inv @ b


empty = np.empty(0)
G = solve_gammas(empty, empty, empty, 0.0)      # t = t0: сліду ще немає
u_c, v_c = velocity(xc, yc, G, empty, empty, empty)
print(f"sum Γ = {G.sum():.2e}, max|V·n| = {np.abs(u_c * nx + v_c * ny).max():.1e}")
