def frame_at(t_want):
    """Кадр, найближчий до заданого моменту часу."""
    return min(frames, key=lambda f: abs(f[0] - t_want))


fig, axes = plt.subplots(4, 1, figsize=(10, 11), sharex=True)
for ax, t_want in zip(axes, [5, 20, 40, T_END]):
    tf, Gf, fxf, fyf, fgf = frame_at(t_want)
    ax.scatter(fxf, fyf, s=3, c=np.sign(fgf), cmap="bwr", vmin=-1, vmax=1)
    ax.plot(x0, y0, "k-", lw=2)
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, X_MAX)
    ax.set_ylim(-1.6, 1.6)
    ax.set_title(f"t = {tf:.1f}")
fig.suptitle("Вільні вихори: синій — γ < 0 (за год. стрілкою), червоний — γ > 0")
plt.show()
