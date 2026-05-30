#!/usr/bin/env python3
"""Generate illustrations for Негладка_оптимізація.tex."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUTPUT_DIR = Path(__file__).resolve().parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

for style in ("ggplot", "seaborn-v0_8-whitegrid", "default"):
    try:
        plt.style.use(style)
        break
    except OSError:
        continue

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
    }
)


def save_figure(fig, name: str) -> Path:
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_subgradient_3d() -> Path:
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    x = np.linspace(-2, 2, 50)
    y = np.linspace(-2, 2, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sqrt(X**2 + Y**2)

    ax.plot_surface(X, Y, Z, cmap="coolwarm", alpha=0.6, edgecolor="none")
    ax.scatter([0], [0], [0], color="red", s=100, label="Точка зламу (0,0)")

    Z_plane1 = 0.5 * X + 0.5 * Y
    Z_plane2 = -0.5 * X + 0.5 * Y
    ax.plot_surface(X, Y, Z_plane1, color="green", alpha=0.3)
    ax.plot_surface(X, Y, Z_plane2, color="orange", alpha=0.3)

    ax.set_title("Субдиференціал: опорні гіперплощини у точці зламу")
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_zlabel("$f(x,y)$")
    ax.set_zlim(-1, 3)
    ax.legend(loc="upper left")
    return save_figure(fig, "subgradient_3d.png")


def plot_eps_subgradient() -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.linspace(0, 2.5, 100)
    f_x = x**2
    eps = 0.5
    f_x_eps = f_x - eps

    ax.plot(x, f_x, "b-", linewidth=2, label="$f(x) = x^2$")
    ax.plot(x, f_x_eps, "b--", linewidth=1.5, label="$f(x) - \\epsilon$")

    x0, y0 = 1, 1
    ax.plot(x0, y0, "ro", markersize=8, label="Точка $x_0$")

    ax.plot(x, 2 * (x - x0) + y0, "g-", label="Точний субградієнт $v=2$")
    ax.plot(x, 1 * (x - x0) + y0, "m-", linewidth=2, label="$\\epsilon$-субградієнт $v=1$")

    ax.fill_between(x, f_x_eps, f_x, color="blue", alpha=0.1)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_ylim(-0.5, 5)
    ax.set_title("Геометричний зміст $\\epsilon$-субградієнта")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    return save_figure(fig, "eps_subgradient.png")


def plot_clarke_descent() -> Path:
    fig, ax = plt.subplots(figsize=(7, 7))

    polygon_points = np.array([[1, 1], [1, 3], [3, 2], [2, 1]])
    poly = Polygon(
        polygon_points,
        closed=True,
        facecolor="skyblue",
        alpha=0.5,
        edgecolor="blue",
        linewidth=2,
    )
    ax.add_patch(poly)

    origin = np.array([0.0, 0.0])
    z_k = np.array([1.0, 1.0])
    g_k = -z_k / np.linalg.norm(z_k)

    ax.plot(origin[0], origin[1], "ko", markersize=8, label="Нуль (0,0)")
    ax.plot(z_k[0], z_k[1], "ro", markersize=8, label="Проекція $z_k$")

    ax.annotate("", xy=z_k, xytext=origin, arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.annotate("", xy=g_k, xytext=origin, arrowprops=dict(arrowstyle="->", color="green", lw=3))

    ax.text(1.5, 2.0, "$\\partial_C f(x_k)$", fontsize=14)
    ax.text(g_k[0] - 0.25, g_k[1] - 0.25, "$g_k$", fontsize=14, color="green")

    ax.set_xlim(-1.5, 4)
    ax.set_ylim(-1.5, 4)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_aspect("equal")
    ax.set_title("Напрямок найкрутішого спуску (проекція на $\\partial_C f$)")
    ax.legend()
    return save_figure(fig, "clarke_descent.png")


def plot_minkowski_gauge() -> Path:
    fig, ax = plt.subplots(figsize=(7, 7))

    u_points = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])
    ax.add_patch(
        Polygon(
            u_points,
            closed=True,
            facecolor="blue",
            alpha=0.3,
            edgecolor="blue",
            linewidth=2,
            label="Множина $U$",
        )
    )

    x_point = np.array([1.5, 1.5])
    lambda_val = np.abs(x_point[0]) + np.abs(x_point[1])

    lambda_u_points = u_points * lambda_val
    ax.add_patch(
        Polygon(
            lambda_u_points,
            closed=True,
            facecolor="red",
            alpha=0.1,
            edgecolor="red",
            linestyle="--",
            linewidth=2,
            label=r"$\lambda U$ (надута)",
        )
    )

    ax.plot(x_point[0], x_point[1], "ro", markersize=8, label="Точка $x$")
    ax.annotate("", xy=x_point, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
    ax.plot(0, 0, "ko", markersize=6)

    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)
    ax.set_aspect("equal")
    ax.set_title(r"Функція Мінковського: $x \in \lambda U \Rightarrow p_U(x) = 3$")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    return save_figure(fig, "minkowski_gauge.png")


def plot_fenchel_conjugate() -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.linspace(-1, 3, 100)
    f_x = 0.5 * x**2
    p = 1.5
    line_px = p * x

    ax.plot(x, f_x, "b-", linewidth=2, label=r"$f(x) = \frac{1}{2}x^2$")
    ax.plot(x, line_px, "g-", linewidth=2, label=r"Пряма $y = px$ (де $p=1.5$)")

    x_star = p
    y_f = 0.5 * x_star**2
    y_l = p * x_star

    ax.plot([x_star, x_star], [y_f, y_l], "r--", linewidth=3, label=r"Макс. зазор $= f^*(p)$")
    ax.plot(x_star, y_f, "bo")
    ax.plot(x_star, y_l, "go")

    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title(r"Спряжена функція Фенхеля: $f^*(p) = \sup_x (px - f(x))$")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    return save_figure(fig, "fenchel_conjugate.png")


def plot_bouligand_cones() -> Path:
    fig, ax = plt.subplots(figsize=(7, 7))

    x_points = np.array([[0, 0], [3, 1], [3, 3], [1, 3]])
    ax.add_patch(
        Polygon(
            x_points,
            closed=True,
            facecolor="gray",
            alpha=0.4,
            edgecolor="black",
            linewidth=2,
            label="Множина $X$",
        )
    )

    ax.plot(0, 0, "ko", markersize=8, label="Точка $x_0$ (кут)")

    ax.plot([0, 4], [0, 4 / 3], "g--", linewidth=2)
    ax.plot([0, 4 / 3], [0, 4], "g--", linewidth=2)
    ax.fill([0, 4 / 3, 4], [0, 4, 4 / 3], color="green", alpha=0.1, label="Дотичний конус $T(X, x_0)$")

    ax.plot([0, -1.5], [0, 4.5], "r-", linewidth=2)
    ax.plot([0, -4.5], [0, 1.5], "r-", linewidth=2)
    ax.add_patch(
        Polygon(
            np.array([[0, 0], [-1.5, 4.5], [-4.5, 4.5], [-4.5, 1.5]]),
            closed=True,
            facecolor="red",
            alpha=0.2,
            edgecolor="red",
            linewidth=1,
            label="Нормальний конус $N(X, x_0)$",
        )
    )

    ax.set_xlim(-4, 4)
    ax.set_ylim(-1, 4)
    ax.set_aspect("equal")
    ax.set_title("Дотичний та нормальний конуси у кутовій точці")
    ax.legend(loc="lower right")
    ax.grid(True, linestyle="--", alpha=0.4)
    return save_figure(fig, "bouligand_cones.png")


def plot_max_subdifferential() -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.linspace(0, 2, 200)
    f1 = x**2
    f2 = 2 - x
    f_max = np.maximum(f1, f2)

    ax.plot(x, f1, "b--", alpha=0.5, label=r"$f_1(x) = x^2$")
    ax.plot(x, f2, "g--", alpha=0.5, label=r"$f_2(x) = 2-x$")
    ax.plot(x, f_max, "r-", linewidth=3, label=r"$f(x) = \max(f_1, f_2)$")

    x_kink, y_kink = 1, 1
    ax.plot(x_kink, y_kink, "ko", markersize=8)

    x_tan = np.linspace(0.5, 1.5, 10)
    ax.plot(x_tan, 2 * (x_tan - x_kink) + y_kink, "b-", label="Дотична до $f_1$ ($v=2$)")
    ax.plot(x_tan, -1 * (x_tan - x_kink) + y_kink, "g-", label="Дотична до $f_2$ ($v=-1$)")
    ax.fill_between(
        x_tan,
        -1 * (x_tan - x_kink) + y_kink,
        2 * (x_tan - x_kink) + y_kink,
        color="red",
        alpha=0.1,
        label=r"$\partial f(1) = [-1, 2]$",
    )

    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title(r"Субдиференціал max: $\mathrm{co}\{\partial f_1, \partial f_2\}$")
    ax.set_ylim(0, 3)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    return save_figure(fig, "max_subdifferential.png")


def plot_relative_interior() -> Path:
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    xx, yy = np.meshgrid(np.linspace(-2, 2, 10), np.linspace(-2, 2, 10))
    zz = 0.5 * xx + 0.5 * yy
    ax.plot_surface(xx, yy, zz, color="gray", alpha=0.15, edgecolor="none")

    theta = np.linspace(0, 2 * np.pi, 80)
    r = 1.5
    xc = r * np.cos(theta)
    yc = r * np.sin(theta)
    zc = 0.5 * xc + 0.5 * yc

    disk_verts = [list(zip(xc, yc, zc))]
    ax.add_collection3d(
        Poly3DCollection(
            disk_verts,
            facecolor="blue",
            alpha=0.45,
            edgecolor="blue",
            linewidth=1.5,
        )
    )
    ax.plot(xc, yc, zc, color="blue", linewidth=2, label="Межа множини $X$")
    ax.scatter([0], [0], [0], color="red", s=100, label=r"Точка $x \in \mathrm{ri}\,X$")

    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_zlabel("$x_3$")
    ax.set_title(r"Відносне нутро $\mathrm{ri}\,X$: диск без 3D-об'єму")
    ax.legend(loc="upper left")
    return save_figure(fig, "relative_interior.png")


def plot_demyanov_shift() -> Path:
    fig, ax = plt.subplots(figsize=(7, 7))

    df_points = np.array([[-1, 1], [1, 2], [2, 0], [0, -1]])
    ax.add_patch(
        Polygon(
            df_points,
            closed=True,
            facecolor="blue",
            alpha=0.2,
            edgecolor="blue",
            linewidth=2,
            label=r"$\partial f(x_k)$",
        )
    )

    omega = np.array([2.0, 1.0])
    l_omega_points = df_points + omega
    ax.add_patch(
        Polygon(
            l_omega_points,
            closed=True,
            facecolor="green",
            alpha=0.3,
            edgecolor="green",
            linewidth=2,
            label=r"$L_\omega = \partial f(x_k) + \omega$",
        )
    )

    origin = np.array([0.0, 0.0])
    z_omega = np.array([2.0, 0.0])

    ax.plot(origin[0], origin[1], "ko", markersize=8, label="Початок координат (0,0)")
    ax.plot(z_omega[0], z_omega[1], "ro", markersize=8, label=r"Вектор мін. норми $z_k^\omega$")

    ax.annotate("", xy=omega, xytext=origin, arrowprops=dict(arrowstyle="->", color="gray", lw=2))
    ax.annotate("", xy=z_omega, xytext=origin, arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(1.0, 0.5, r"$\omega$", fontsize=14, color="gray")

    ax.set_xlim(-2, 4)
    ax.set_ylim(-2, 4)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_aspect("equal")
    ax.set_title(r"Метод Дем'янова: проекція нуля на $L_\omega$")
    ax.legend()
    return save_figure(fig, "demyanov_shift.png")


def main() -> None:
    paths = [
        plot_subgradient_3d(),
        plot_eps_subgradient(),
        plot_clarke_descent(),
        plot_minkowski_gauge(),
        plot_fenchel_conjugate(),
        plot_bouligand_cones(),
        plot_max_subdifferential(),
        plot_relative_interior(),
        plot_demyanov_shift(),
    ]
    for path in paths:
        print(f"Збережено: {path}")


if __name__ == "__main__":
    main()
