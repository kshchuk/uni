from matplotlib.animation import FuncAnimation
from IPython.display import HTML

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(x0, y0, "k-", lw=2)
dots = ax.scatter([], [], s=3, c=[], cmap="bwr", vmin=-1, vmax=1)
label = ax.set_title("")
ax.set_aspect("equal")
ax.set_xlim(-0.5, X_MAX)
ax.set_ylim(-1.6, 1.6)


def draw(i):
    tf, _, fxf, fyf, fgf = frames[i]
    dots.set_offsets(np.c_[fxf, fyf])
    dots.set_array(np.sign(fgf))
    label.set_text(f"t = {tf:.1f}")
    return dots, label


anim = FuncAnimation(fig, draw, frames=len(frames), interval=60)
plt.close(fig)
HTML(anim.to_jshtml())
