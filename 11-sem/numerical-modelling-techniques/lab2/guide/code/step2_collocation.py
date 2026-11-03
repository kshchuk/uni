tc = 0.5 * (t[:-1] + t[1:])                     # параметр посередині між сусідами
xc = XC + R * np.cos(tc)                        # M-1 точок колокації на дузі
yc = R * np.sin(tc)
nx = -np.cos(tc)                                # нормаль до центру кола
ny = -np.sin(tc)                                # (= ліворуч від обходу)

fig, ax = plt.subplots(figsize=(6, 6))
for xj, yj in zip(x0, y0):                      # кола радіуса δ навколо вихорів
    ax.add_patch(plt.Circle((xj, yj), DELTA, fill=False, color="0.6", lw=0.8))
ax.plot(x0, y0, "o", color="tab:red", ms=4, label="приєднані вихори ω0j")
ax.plot(xc, yc, "x", color="k", ms=5, label="колокації")
ax.quiver(xc, yc, nx, ny, color="tab:green", scale=12, width=0.005)
ax.set_aspect("equal")
ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.show()
