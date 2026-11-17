def frame_at(t_want):
    """Кадр, найближчий до заданого моменту часу."""
    return min(frames, key=lambda f: abs(f[0] - t_want))


def flow_box(back, ahead, half):
    """Межі рисунка: смуга вздовж потоку від -back до ahead, ±half поперек."""
    e = np.array([-back, ahead])[:, None] * V_INF          # кінці смуги вздовж V∞
    p = np.array([-V_INF[1], V_INF[0]]) * half              # напрям поперек потоку
    pts = np.r_[e + p, e - p]
    return (pts[:, 0].min(), pts[:, 0].max()), (pts[:, 1].min(), pts[:, 1].max())


xlim, ylim = flow_box(0.6, X_MAX, 1.6)
fig, axes = plt.subplots(2, 2, figsize=(13, 7.5))
for ax, t_want in zip(axes.flat, [5, 20, 40, T_END]):
    tf, Gf, fxf, fyf, fgf = frame_at(t_want)
    ax.scatter(fxf, fyf, s=3, c=np.sign(fgf), cmap="bwr", vmin=-1, vmax=1)
    ax.plot(x0, y0, "k-", lw=2)
    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(f"t = {tf:.1f}")
fig.suptitle("Вільні вихори: синій — γ < 0 (за год. стрілкою), червоний — γ > 0")
plt.show()
