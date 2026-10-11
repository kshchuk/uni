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

k = slice(None, None, 4)                        # кожна 4-та нормаль, щоб стрілки не злипались
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(x0, y0, "o", mfc="white", label="особливості ω0j")
ax.plot(xc, yc, "x", label="колокації")
ax.quiver(xc[k], yc[k], nx[k], ny[k], color="tab:green", scale=8, width=0.006)
ax.set_aspect("equal")
ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.show()
