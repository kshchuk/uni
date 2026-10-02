s_arc = R * (t - t[0])                          # відстань уздовж дуги від верхнього кінця
fig, ax = plt.subplots(figsize=(7, 4))
for g0 in (-1.0, 0.0, 1.0):
    Gg = solve_gammas(x0, y0, xc, yc, nx, ny, V_INF, g0)
    ax.plot(s_arc, Gg / h, label=f"Γ0 = {g0:g}")
ax.set_xlabel("s — відстань уздовж дуги від верхнього кінця")
ax.set_ylabel("Γj / h ≈ γ(s)")
ax.set_title("Густина вихрового шару: різко зростає біля кінців")
ax.grid(alpha=0.3)
ax.legend()
plt.show()
