tc = 0.5 * (t[:-1] + t[1:])                     # параметр посередині між сусідами
xc = XC + R * np.cos(tc)                        # M-1 точок колокації на дузі
yc = R * np.sin(tc)
nx = -np.cos(tc)                                # нормаль до центру кола
ny = -np.sin(tc)                                # (= ліворуч від обходу)

# Варіант посібника (7.1.2): середини хорд і нормалі до хорд
# dx, dy = np.diff(x0), np.diff(y0)
# ell = np.hypot(dx, dy)
# xc, yc = (x0[:-1] + x0[1:]) / 2, (y0[:-1] + y0[1:]) / 2
# nx, ny = -dy / ell, dx / ell

fig, ax = plt.subplots(figsize=(5, 5))
ax.plot(x0, y0, "o", mfc="white", label="особливості ω0j")
ax.plot(xc, yc, "x", label="колокації")
ax.quiver(xc, yc, nx, ny, scale=15, width=0.004)
ax.set_aspect("equal")
ax.legend()
plt.show()
