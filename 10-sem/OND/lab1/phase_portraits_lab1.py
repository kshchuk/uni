import numpy as np
import matplotlib.pyplot as plt


def normalize_vectors(u, v):
    mag = np.hypot(u, v)
    mag[mag == 0] = 1.0
    return u / mag, v / mag


def plot_system(
    f,
    xlim,
    ylim,
    density,
    seeds,
    title,
    output_name,
    stream_color="royalblue",
    separatrices=None,
    separatrix_labels=None,
):
    x = np.linspace(xlim[0], xlim[1], 29)
    y = np.linspace(ylim[0], ylim[1], 29)
    X, Y = np.meshgrid(x, y)
    U, V = f(X, Y)
    Un, Vn = normalize_vectors(U, V)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    ax.quiver(X, Y, Un, Vn, color="black", alpha=0.9, pivot="mid", scale=26)

    ax.streamplot(
        X,
        Y,
        U,
        V,
        color=stream_color,
        density=density,
        linewidth=2.2,
        arrowsize=1.2,
        start_points=np.array(seeds, dtype=float),
    )

    ax.axhline(0, color="black", linewidth=1.1)
    ax.axvline(0, color="black", linewidth=1.1)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.25)

    if separatrices:
        # Draw separatrices as invariant straight lines through the origin.
        # Each separatrix is given by a direction vector (vx, vy).
        x_line = np.linspace(xlim[0], xlim[1], 300)
        for i, (vx, vy) in enumerate(separatrices):
            if abs(vx) < 1e-12:
                ax.plot(
                    [0, 0],
                    [ylim[0], ylim[1]],
                    "--",
                    color="darkgreen",
                    linewidth=2.0,
                    label="Сепаратриси" if i == 0 else None,
                )
            else:
                k = vy / vx
                y_line = k * x_line
                mask = (y_line >= ylim[0]) & (y_line <= ylim[1])
                ax.plot(
                    x_line[mask],
                    y_line[mask],
                    "--",
                    color="darkgreen",
                    linewidth=2.0,
                    label="Сепаратриси" if i == 0 else None,
                )
        ax.legend(loc="upper right")
        if separatrix_labels:
            for text, x0, y0 in separatrix_labels:
                ax.text(
                    x0,
                    y0,
                    text,
                    color="darkgreen",
                    fontsize=11,
                    fontweight="bold",
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5),
                )

    fig.tight_layout()
    fig.savefig(output_name)
    plt.close(fig)


def system3(x, y):
    return -2 * x - 5 * y, 2 * x + 2 * y


def system6(x, y):
    return x, 2 * x - y


if __name__ == "__main__":
    seeds3 = [
        [2, 0],
        [4, 0],
        [-3, 1.5],
        [1.5, -2],
        [-2.5, -1],
        [0.8, 2.4],
    ]
    plot_system(
        system3,
        xlim=(-5, 5),
        ylim=(-5, 5),
        density=1.05,
        seeds=seeds3,
        title="Фазовий портрет: Завдання 3 (Центр)",
        output_name="portrait3_python.png",
        stream_color="blue",
        separatrices=None,
        separatrix_labels=None,
    )

    seeds6 = [
        [1, 0],
        [-1, 0],
        [0.5, 1],
        [-0.5, -1],
        [0, 2.5],
        [0, -2.5],
    ]
    plot_system(
        system6,
        xlim=(-3, 3),
        ylim=(-3, 3),
        density=1.0,
        seeds=seeds6,
        title="Фазовий портрет: Завдання 6 (Сідло)",
        output_name="portrait6_python.png",
        stream_color="red",
        separatrices=[(1, 1), (0, 1)],
        separatrix_labels=[("y=x", 1.55, 1.45), ("x=0", 0.08, 2.25)],
    )

    print("Saved: portrait3_python.png, portrait6_python.png")

    # --- Task 3: circles in (xi, eta) plane ---
    fig, ax = plt.subplots(figsize=(7, 7), dpi=140)
    theta = np.linspace(0, 2 * np.pi, 500)
    for r in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        ax.plot(r * np.cos(theta), r * np.sin(theta), "b-", linewidth=1.6)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)
    ax.set_aspect("equal")
    ax.axhline(0, color="black", linewidth=1.1)
    ax.axvline(0, color="black", linewidth=1.1)
    ax.set_xlabel(r"$\xi$", fontsize=14)
    ax.set_ylabel(r"$\eta$", fontsize=14)
    ax.set_title(
        r"Траєкторії перетвореної системи ($\xi, \eta$): кола",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig("circles_xi_eta.png")
    plt.close(fig)
    print("Saved: circles_xi_eta.png")

    # --- Task 3: ellipses 2x^2+4xy+5y^2=C in (x,y) ---
    xg = np.linspace(-5, 5, 600)
    yg = np.linspace(-5, 5, 600)
    Xg, Yg = np.meshgrid(xg, yg)
    F3 = 2 * Xg**2 + 4 * Xg * Yg + 5 * Yg**2

    fig, ax = plt.subplots(figsize=(7, 7), dpi=140)
    levels3 = [2, 6, 12, 20, 30, 42]
    cs = ax.contour(Xg, Yg, F3, levels=levels3, colors="blue", linewidths=1.6)
    ax.clabel(cs, fmt={lv: f"C={lv}" for lv in levels3}, fontsize=8)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect("equal")
    ax.axhline(0, color="black", linewidth=1.1)
    ax.axvline(0, color="black", linewidth=1.1)
    ax.set_xlabel("x", fontsize=14)
    ax.set_ylabel("y", fontsize=14)
    ax.set_title(
        r"Еліпси $2x^2+4xy+5y^2=C$ (початкові координати)",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig("ellipses_xy.png")
    plt.close(fig)
    print("Saved: ellipses_xy.png")

    # --- Task 6: hyperbolas xi*eta=C in (xi,eta) ---
    xig = np.linspace(-3, 3, 600)
    etag = np.linspace(-3, 3, 600)
    XI, ETA = np.meshgrid(xig, etag)
    F6t = XI * ETA

    fig, ax = plt.subplots(figsize=(7, 7), dpi=140)
    levels6t = [-2, -1, -0.5, -0.2, 0.2, 0.5, 1, 2]
    cs6 = ax.contour(XI, ETA, F6t, levels=levels6t, colors="red", linewidths=1.6)
    ax.clabel(cs6, fmt={lv: f"{lv}" for lv in levels6t}, fontsize=8)
    ax.plot([-3, 3], [0, 0], "--", color="darkgreen", linewidth=1.8, label=r"$\eta=0$")
    ax.plot([0, 0], [-3, 3], "--", color="darkgreen", linewidth=1.8, label=r"$\xi=0$")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.axhline(0, color="black", linewidth=0.6)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_xlabel(r"$\xi$", fontsize=14)
    ax.set_ylabel(r"$\eta$", fontsize=14)
    ax.set_title(
        r"Гіперболи $\xi\,\eta=C$ (перетворена система)",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig("hyperbolas_xi_eta.png")
    plt.close(fig)
    print("Saved: hyperbolas_xi_eta.png")

    # --- Task 6: curves x(y-x)=C in (x,y) ---
    xg6 = np.linspace(-3, 3, 600)
    yg6 = np.linspace(-3, 3, 600)
    Xg6, Yg6 = np.meshgrid(xg6, yg6)
    F6xy = Xg6 * (Yg6 - Xg6)

    fig, ax = plt.subplots(figsize=(7, 7), dpi=140)
    levels6xy = [-2, -1, -0.5, -0.2, 0.2, 0.5, 1, 2]
    cs6xy = ax.contour(Xg6, Yg6, F6xy, levels=levels6xy, colors="red", linewidths=1.6)
    ax.clabel(cs6xy, fmt={lv: f"{lv}" for lv in levels6xy}, fontsize=8)
    xln = np.linspace(-3, 3, 300)
    ax.plot(xln, xln, "--", color="darkgreen", linewidth=1.8, label="y=x")
    ax.plot([0, 0], [-3, 3], "--", color="darkgreen", linewidth=1.8, label="x=0")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.axhline(0, color="black", linewidth=1.1)
    ax.axvline(0, color="black", linewidth=1.1)
    ax.set_xlabel("x", fontsize=14)
    ax.set_ylabel("y", fontsize=14)
    ax.set_title(
        r"Криві $x(y-x)=C$ (початкові координати)",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig("saddle_curves_xy.png")
    plt.close(fig)
    print("Saved: saddle_curves_xy.png")
