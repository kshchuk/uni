#!/usr/bin/env python3
"""Generate all figures for referat/referat.tex (deterministic seed)."""
from __future__ import annotations

import math
import os
import urllib.request
from io import BytesIO

os.environ.setdefault("MPLBACKEND", "Agg")


import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyArrowPatch, Rectangle
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

RNG = np.random.default_rng(42)

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"


def save(fig: plt.Figure, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# --- Fig 1: Pythagorean tree vs stochastic tree ---


def pythagoras_tree(ax, x0, y0, length, angle, depth, max_depth):
    if depth > max_depth or length < 0.8:
        return
    x1 = x0 + length * math.cos(angle)
    y1 = y0 + length * math.sin(angle)
    ax.plot([x0, x1], [y0, y1], color="#1a5276", lw=1.8 - depth * 0.12)
    new_len = length * 0.68
    pythagoras_tree(ax, x1, y1, new_len, angle + math.radians(42), depth + 1, max_depth)
    pythagoras_tree(ax, x1, y1, new_len, angle - math.radians(48), depth + 1, max_depth)


def stochastic_tree(ax, x0, y0, length, angle, depth, max_depth, rng: np.random.Generator):
    """L-system-like branching with independent random length and angle per child."""
    if depth > max_depth or length < 0.65:
        return
    x1 = x0 + length * math.cos(angle)
    y1 = y0 + length * math.sin(angle)
    ax.plot([x0, x1], [y0, y1], color="#1e8449", lw=1.6 - depth * 0.1)
    len_left = length * rng.uniform(0.48, 0.88)
    len_right = length * rng.uniform(0.48, 0.88)
    da1 = math.radians(rng.uniform(18, 62))
    da2 = math.radians(rng.uniform(18, 62))
    stochastic_tree(ax, x1, y1, len_left, angle + da1, depth + 1, max_depth, rng)
    stochastic_tree(ax, x1, y1, len_right, angle - da2, depth + 1, max_depth, rng)


def fig01_trees():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.8))
    for ax, title in ((ax1, "Детерміноване дерево Піфагора"), (ax2, "Стохастичне дерево")):
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=11)
    pythagoras_tree(ax1, 0, 0, 22, math.radians(90), 0, 10)
    ax1.set_xlim(-35, 35)
    ax1.set_ylim(0, 55)
    # Окремий ГПВЧ лише для дерева; стовбур теж випадковий — інакше перший відрізок збігається з Піфагором і силуети «дублюються»
    tree_rng = np.random.default_rng(2026)
    root_len = 22.0 * float(tree_rng.uniform(0.88, 1.12))
    root_deg = 90.0 + float(tree_rng.uniform(-18.0, 18.0))
    stochastic_tree(ax2, 0, 0, root_len, math.radians(root_deg), 0, 10, tree_rng)
    ax2.set_xlim(-38, 38)
    ax2.set_ylim(0, 55)
    fig.suptitle("Порівняння детермінованого та стохастичного росту", fontsize=12, fontweight="bold")
    return save(fig, "fig01_trees.png")


# --- Fig 2: heightmap + FIC schematic ---


def fractal_heightmap(n: int = 257) -> np.ndarray:
    """Multi-octave value noise (gradient-free approximation) for terrain-like surface."""
    x = np.linspace(0, 6, n)
    y = np.linspace(0, 6, n)
    X, Y = np.meshgrid(x, y)
    z = np.zeros_like(X)
    amp = 1.0
    for k in range(6):
        freq = 2**k
        gx = RNG.standard_normal((int(freq * 4) + 2, int(freq * 4) + 2))
        ix = (X * freq * 1.3).astype(int) % (gx.shape[1] - 1)
        iy = (Y * freq * 1.3).astype(int) % (gx.shape[0] - 1)
        z += amp * gx[iy, ix]
        amp *= 0.52
    z -= z.min()
    z /= z.max() + 1e-9
    return z


def _fallback_fic_texture(size: int = 240) -> np.ndarray:
    """Synthetic texture if Lenna cannot be loaded."""
    rng = np.random.default_rng(0)
    small = np.zeros((120, 120))
    for _ in range(400):
        cx, cy = rng.integers(10, 110, size=2)
        r0 = rng.integers(4, 18)
        y, x = np.ogrid[:120, :120]
        small += np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * r0**2))
    small = (small - small.min()) / (small.max() - small.min() + 1e-9)
    if Image is not None:
        im = Image.fromarray((small * 255).astype(np.uint8))
        out = np.asarray(im.resize((size, size), Image.Resampling.LANCZOS), dtype=np.float64) / 255.0
        return out
    from scipy.ndimage import zoom

    z = zoom(small, size / 120.0, order=1)
    return (z - z.min()) / (z.max() - z.min() + 1e-9)


def load_lenna_gray(size: int = 240) -> np.ndarray | None:
    """Classic 512×512 test image (grayscale), via OpenCV sample mirror; cite USC-SIPI in the paper."""
    if Image is None:
        return None
    url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg"
    req = urllib.request.Request(url, headers={"User-Agent": "pattern-recognition-referat/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read()
        im = Image.open(BytesIO(raw)).convert("L")
        im = im.resize((size, size), Image.Resampling.LANCZOS)
        return np.asarray(im, dtype=np.float64) / 255.0
    except Exception as exc:
        print(f"[fig02] Lenna download failed ({exc!r}); using synthetic texture.")
        return None


def fig02_landscape_fic():
    fig = plt.figure(figsize=(12.5, 5.4))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    h = fractal_heightmap(129)
    step = 3
    hs = h[::step, ::step]
    r = hs.shape[0]
    xx, yy = np.meshgrid(np.arange(r), np.arange(r))
    ax1.plot_surface(xx, yy, hs, cmap=cm.terrain, linewidth=0, antialiased=True, rstride=1, cstride=1)
    ax1.view_init(elev=52, azim=-115)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_zticks([])
    ax1.set_title("Процедурна висотна карта (мультиоктавний шум)", fontsize=10)

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_aspect("equal")
    ax2.axis("off")
    s = 240.0
    tex = load_lenna_gray(int(s))
    panel_note = "тестове зображення Lenna (USC-SIPI; див. список літератури)"
    if tex is None:
        tex = _fallback_fic_texture(int(s))
        panel_note = "синтетична текстура (немає Pillow або мережі для Lenna)"
    ax2.imshow(tex, cmap="bone", origin="lower", extent=[0, s, 0, s])
    # domain (larger, lower-left), range (smaller, upper-right); coords: origin lower
    ax2.add_patch(Rectangle((14, 14), 100, 100, fill=False, edgecolor="orange", lw=2))
    ax2.add_patch(Rectangle((168, 164), 44, 44, fill=False, edgecolor="cyan", lw=2))
    arr = FancyArrowPatch((64, 64), (188, 188), arrowstyle="->", mutation_scale=14, color="yellow", lw=1.8)
    ax2.add_patch(arr)
    ax2.text(14, 228, "domain", color="orange", fontsize=9, va="top")
    ax2.text(165, 228, "range", color="cyan", fontsize=9, va="top")
    ax2.set_title(f"Схема FIC: domain → range\n({panel_note})", fontsize=10)
    fig.tight_layout()
    return save(fig, "fig02_landscape_fic.png")


# --- Fig 3: vessel networks + FD bars ---


def branching_network(ax, chaotic: bool, seed: int):
    rng = np.random.default_rng(seed)
    nodes = [(0.0, 0.5)]
    edges = []
    for gen in range(9):
        new_nodes = []
        for x, y in nodes:
            nbranch = rng.integers(2, 4) if chaotic else 2
            for _ in range(nbranch):
                dx = rng.uniform(0.04, 0.09) if not chaotic else rng.uniform(0.02, 0.12)
                dy = rng.uniform(-0.12, 0.12) if chaotic else rng.uniform(-0.08, 0.08)
                if chaotic and rng.random() < 0.25:
                    dy += rng.choice([-0.18, 0.18])
                x2, y2 = min(x + dx, 1.0), np.clip(y + dy, 0.05, 0.95)
                edges.append(((x, y), (x2, y2)))
                new_nodes.append((x2, y2))
        nodes = new_nodes[: 55 if chaotic else 40]
    for (a, b) in edges:
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#c0392b" if chaotic else "#2874a6", lw=0.9, alpha=0.85)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def fig03_vessels_fd():
    fig = plt.figure(figsize=(11, 4.8))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)
    branching_network(ax1, chaotic=False, seed=1)
    ax1.set_title("Стилізація: ієрархічна мережа", fontsize=10)
    branching_network(ax2, chaotic=True, seed=2)
    ax2.set_title("Стилізація: «хаотична» мережа", fontsize=10)
    cats = ["Норма\n(умовно)", "Патологія\n(умовно)"]
    vals = [1.62, 1.89]
    ax3.bar(cats, vals, color=["#2874a6", "#c0392b"])
    ax3.set_ylabel("Оцінка FD (ілюстраційно)")
    ax3.set_title("Порівняння фрактальної розмірності", fontsize=10)
    fig.suptitle("Фрактальні властивості мереж (навчальна стилізація)", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return save(fig, "fig03_vessels_fd.png")


# --- Fig 4: dipole vs Koch ---


def koch_points(p1, p2, order):
    if order == 0:
        return [p1, p2]
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = (x2 - x1) / 3, (y2 - y1) / 3
    a = (x1, y1)
    b = (x1 + dx, y1 + dy)
    e = (x2 - dx, y2 - dy)
    d = (x2, y2)
    px, py = (b[0] + e[0]) / 2, (b[1] + e[1]) / 2
    vx, vy = e[0] - b[0], e[1] - b[1]
    cx, cy = -vy, vx
    h = math.sqrt(dx * dx + dy * dy) * math.sqrt(3) / 6
    ln = math.hypot(cx, cy) + 1e-9
    c = (px + cx / ln * h, py + cy / ln * h)
    left = koch_points(a, b, order - 1)[1:-1]
    mid = koch_points(b, c, order - 1)[1:-1]
    mid2 = koch_points(c, e, order - 1)[1:-1]
    right = koch_points(e, d, order - 1)[1:-1]
    return [a] + left + [b] + mid + [c] + mid2 + [e] + right + [d]


def fig04_antennas():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.plot([-1, 1], [0, 0], color="black", lw=3)
    ax1.plot([0, 0], [-0.15, 0.15], color="black", lw=2)
    ax1.set_title("Напівхвильовий диполь (схема)", fontsize=11)
    ax1.set_xlim(-1.2, 1.2)
    ax1.set_ylim(-0.5, 0.5)

    pts = koch_points((0, 0), (3, 0), 3)
    xs, ys = zip(*pts)
    ax2.plot(xs, ys, color="#6c3483", lw=2)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("Провідник у формі кривої Коха (3-я ітерація)", fontsize=11)
    ax2.set_xlim(-0.2, 3.2)
    ax2.set_ylim(-0.6, 0.8)
    fig.suptitle("Порівняння геометрії диполя та фрактального провідника", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return save(fig, "fig04_antennas.png")


def sierpinski_carpet_mask(u: np.ndarray, v: np.ndarray, iters: int = 5) -> np.ndarray:
    """1 = мідь, 0 = діелектрик; килим Серпінського на [0,1]^2."""
    x = np.asarray(u, dtype=np.float64).copy()
    y = np.asarray(v, dtype=np.float64).copy()
    ok = np.ones_like(x, dtype=bool)
    for _ in range(iters):
        xi = np.floor(np.clip(x, 0, 1 - 1e-12) * 3).astype(np.int32)
        yi = np.floor(np.clip(y, 0, 1 - 1e-12) * 3).astype(np.int32)
        xi = np.clip(xi, 0, 2)
        yi = np.clip(yi, 0, 2)
        ok &= ~((xi == 1) & (yi == 1))
        x = x * 3.0 - xi
        y = y * 3.0 - yi
    return ok.astype(np.float64)


def fig04b_fractal_patch_pcb():
    """Фотореалістичний рендер FR4 + мідний килим Серпінського (імітація макрознімку плати)."""
    from scipy.ndimage import gaussian_filter

    n = 960
    rng = np.random.default_rng(17)
    u = np.linspace(0, 1, n, endpoint=False) + 0.5 / n
    v = np.linspace(0, 1, n, endpoint=False) + 0.5 / n
    U, V = np.meshgrid(u, v, indexing="xy")
    board = (U > 0.05) & (U < 0.95) & (V > 0.05) & (V < 0.95)
    uc = (U - 0.05) / 0.90
    vc = (V - 0.05) / 0.90
    on_sq = (uc >= 0) & (uc <= 1) & (vc >= 0) & (vc <= 1)
    copper = sierpinski_carpet_mask(uc, vc, iters=5) * on_sq.astype(np.float64) * board.astype(np.float64)

    # Колір FR4 (зелена маска лаку) + легка текстура
    fr4_r = 0.07 + 0.012 * rng.standard_normal((n, n))
    fr4_g = 0.26 + 0.02 * rng.standard_normal((n, n))
    fr4_b = 0.11 + 0.012 * rng.standard_normal((n, n))
    fr4_r = np.clip(fr4_r, 0.05, 0.14)
    fr4_g = np.clip(fr4_g, 0.18, 0.36)
    fr4_b = np.clip(fr4_b, 0.08, 0.16)
    fr4 = np.dstack([fr4_r, fr4_g, fr4_b])
    # ледь видимі «подряпини» на лаку
    fr4 *= 0.92 + 0.08 * gaussian_filter(rng.standard_normal((n, n)), sigma=2.1)[..., None]

    dist = gaussian_filter(copper, sigma=1.2)
    edge = np.abs(gaussian_filter(copper, sigma=0.55) - gaussian_filter(copper, sigma=2.0))
    light = np.clip(0.55 + 0.45 * dist + 0.75 * edge, 0.4, 1.45)
    cr, cg, cb = 0.62, 0.38, 0.14
    m = copper > 0.5
    cu_r = np.clip(cr * light * (0.9 + 0.12 * rng.random((n, n))), 0, 1)
    cu_g = np.clip(cg * light * (0.85 + 0.08 * rng.random((n, n))), 0, 1)
    cu_b = np.clip(cb * light * (0.55 + 0.06 * rng.random((n, n))), 0, 1)
    copper_rgb = np.dstack([cu_r, cu_g, cu_b])
    img = np.where(m[..., None], copper_rgb, fr4)
    img = np.clip(img, 0, 1)
    # тінь по периметру плати
    fade = 0.25 + 0.75 * board.astype(np.float64)
    img *= fade[..., None]
    shade = np.linspace(1.04, 0.94, n)[:, None]
    img *= shade[..., None]
    img = np.clip(img, 0, 1)

    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    ax.imshow(img, origin="upper", interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout(pad=0.02)
    return save(fig, "fig04b_fractal_patch_pcb.png")


# --- Fig 5: fBm resampled ---


def fig05_finance_scales():
    """Self-similar-looking synthetic path (Weierstrass-type sum), not exact fBm — fast for batch plots."""
    n = 720
    t = np.linspace(0, 1, n)
    H = 0.55
    z = np.zeros(n)
    for k in range(14):
        f = 2**k
        amp = f ** (-H)
        ph = RNG.uniform(0, 2 * math.pi)
        z += amp * np.sin(2 * math.pi * f * t + ph)
    z = (z - z.mean()) / (z.std() + 1e-9)

    def panel(ax, zsub, title):
        m = min(len(zsub), 360)
        ax.plot(np.arange(m), zsub[:m], color="#1f618d", lw=0.8)
        ax.set_title(title, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))
    panel(axes[0], z, "Масштаб A (умовно «хвилина»)")
    panel(axes[1], z[::3], "Масштаб B (умовно «день»)")
    panel(axes[2], z[::12], "Масштаб C (умовно «місяць»)")
    fig.suptitle("Самоподібність профілю: один fBm-процес на різних масштабах", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return save(fig, "fig05_finance_scales.png")


# --- Fig 6: DLA + stylized snow ---


def dla_cluster(max_steps: int = 650, grid: int = 151):
    """Fast grid DLA (Witten--Sander style); walkers capped to keep runtime bounded."""
    g = grid // 2
    occ = np.zeros((grid, grid), dtype=bool)
    occ[g, g] = True
    for _ in range(max_steps):
        ang = RNG.uniform(0, 2 * math.pi)
        r = grid // 2 - 5
        x = int(g + r * math.cos(ang))
        y = int(g + r * math.sin(ang))
        for _ in range(3500):
            dx, dy = RNG.integers(-1, 2, size=2)
            x = int(np.clip(x + dx, 1, grid - 2))
            y = int(np.clip(y + dy, 1, grid - 2))
            if occ[y - 1 : y + 2, x - 1 : x + 2].any():
                occ[y, x] = True
                break
    return occ


def fig06_dla_snowflake():
    occ = dla_cluster(650, 151)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 5.0))
    yy, xx = np.where(occ)
    ax1.scatter(xx, yy, s=0.6, c="#2e86c1", alpha=0.85)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("2D DLA-кластер (симуляція)", fontsize=11)
    t = np.linspace(0, 2 * math.pi, 7, endpoint=False)
    for k in range(6):
        ang = t[k]
        xs = [0, 1.2 * math.cos(ang)]
        ys = [0, 1.2 * math.sin(ang)]
        ax2.plot(xs, ys, color="#5dade2", lw=2)
        for m in range(1, 4):
            r = 0.35 * m
            ax2.plot(
                [r * math.cos(ang), r * math.cos(ang + 0.25)],
                [r * math.sin(ang), r * math.sin(ang + 0.25)],
                color="#aed6f1",
                lw=1.2,
            )
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("Стилізована «сніжинка» (не фото)", fontsize=11)
    fig.suptitle("Випадковий ріст: DLA та дендритна симетрія", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return save(fig, "fig06_dla_snowflake.png")


# --- Fig 7: optimization landscape + agents ---


def fig07_sfs():
    fig = plt.figure(figsize=(10, 4.8))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    X = np.linspace(-3, 3, 80)
    Y = np.linspace(-3, 3, 80)
    XX, YY = np.meshgrid(X, Y)
    ZZ = 0.3 * (XX**2 + YY**2) - 2 * (np.cos(3 * XX) + np.cos(3 * YY))
    ax.plot_surface(XX, YY, ZZ, cmap=cm.viridis, alpha=0.55, linewidth=0)
    n = 220
    px = RNG.uniform(-2.8, 2.8, n)
    py = RNG.uniform(-2.8, 2.8, n)
    pz = 0.3 * (px**2 + py**2) - 2 * (np.cos(3 * px) + np.cos(3 * py)) + RNG.normal(0, 0.25, n)
    ax.scatter(px, py, pz, s=4, c="white", alpha=0.35)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.view_init(elev=35, azim=-60)
    ax.set_title("Ландшафт цільової функції + «хмара» агентів", fontsize=10)

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.contourf(XX, YY, ZZ, levels=28, cmap=cm.viridis)
    cx, cy = 0.05, 0.08
    ax2.scatter(cx, cy, s=80, c="red", marker="*", zorder=5)
    ax2.set_title("Контури та глобальний мінімум (схема)", fontsize=10)
    ax2.set_xticks([])
    ax2.set_yticks([])
    fig.suptitle("Ідея фрактального/стохастичного пошуку в складному ландшафті", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return save(fig, "fig07_sfs.png")


# --- Fig 8: synthetic cyclone + DMSP night-lights crop + mask ---


def _nightlights_crop_and_mask():
    """Фрагмент глобального композиту DMSP (figures/external/ext_earthlights.jpg) + бінарна маска."""
    path = ROOT / "figures/external/ext_earthlights.jpg"
    if Image is None or not path.is_file():
        return None, None
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=float) / 255.0
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    h, w = gray.shape
    # Типова орієнтація Earthlights: Європа/Середземномор'я ближче до центру кадру
    r0, r1 = int(h * 0.10), int(h * 0.90)
    c0, c1 = int(w * 0.36), int(w * 0.70)
    crop = gray[r0:r1, c0:c1]
    if crop.size < 64:
        return None, None
    thr = float(np.percentile(crop, 74.0))
    mask = (crop > thr).astype(float)
    from scipy.ndimage import binary_opening

    mask = binary_opening(mask, structure=np.ones((2, 2))).astype(float)
    return crop, mask
def fig08_cyclone_night():
    fig = plt.figure(figsize=(14.2, 5.1))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1.08, 1.0, 1.0], wspace=0.12)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])

    # Псевдо-ІЧ: 2D у декартових координатах (око + спіральні «рукави»)
    n = 321
    x = np.linspace(-1.05, 1.05, n)
    y = np.linspace(-1.05, 1.05, n)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    Th = np.arctan2(Y, X)
    mask_disc = (R < 0.98) & (R > 0.05)
    spiral = 0.42 * (1.0 + 0.55 * np.sin(5 * Th + 14.0 * R + 0.35 * np.sin(9.0 * R)))
    eyewall = np.exp(-((R - 0.38) ** 2) / 0.018)
    eye = np.exp(-((R - 0.12) ** 2) / 0.004)
    ir = spiral * (0.25 + 0.75 * R) + 1.1 * eyewall + 0.45 * eye
    ir = np.where(mask_disc, ir, np.nan)
    ax1.imshow(ir, cmap="inferno", origin="lower", extent=[x.min(), x.max(), y.min(), y.max()])
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("Синтетичний «циклон» (псевдо-ІЧ)", fontsize=11)

    crop, nmask = _nightlights_crop_and_mask()
    if crop is not None:
        ax2.imshow(crop, cmap="magma", origin="upper")
        ax2.axis("off")
        ax2.set_title("Фрагмент DMSP (яскравість)", fontsize=11)
        ax3.imshow(nmask, cmap="gray", origin="upper", vmin=0.0, vmax=1.0)
        ax3.axis("off")
        ax3.set_title("Бінарна маска (поріг)", fontsize=11)
        fig.suptitle(
            "Симуляція циклону; нічні вогні --- фрагмент реального композиту та маска «місто / не місто»",
            fontsize=11.5,
            fontweight="bold",
        )
    else:
        # Резерв, якщо немає figures/external/ext_earthlights.jpg (запустіть fetch_external_figures.sh)
        n = 256
        lights = np.zeros((n, n))
        yy, xx = np.ogrid[:n, :n]
        for _ in range(80):
            ox, oy = RNG.integers(20, n - 20, size=2)
            lights += np.exp(-((xx - ox) ** 2 + (yy - oy) ** 2) / (2 * RNG.integers(80, 400)))
        lights += 0.15 * RNG.random((n, n))
        lights = (lights > 0.35).astype(float)
        from scipy.ndimage import binary_dilation

        lights = binary_dilation(lights, iterations=1).astype(float)
        ax2.imshow(lights, cmap="magma", origin="upper")
        ax2.axis("off")
        ax2.set_title("Схема (немає DMSP-файлу)", fontsize=11)
        ax3.imshow(lights, cmap="gray", origin="upper")
        ax3.axis("off")
        ax3.set_title("Бінарна маска (заглушка)", fontsize=11)
        fig.suptitle(
            "Фрактальні аспекти «циклону» та урбанізованої підсвітки (частково симуляція)",
            fontsize=11.5,
            fontweight="bold",
        )

    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.91])
    return save(fig, "fig08_cyclone_night.png")


def main():
    outs = [
        fig01_trees(),
        fig02_landscape_fic(),
        fig03_vessels_fd(),
        fig04_antennas(),
        fig04b_fractal_patch_pcb(),
        fig05_finance_scales(),
        fig06_dla_snowflake(),
        fig07_sfs(),
        fig08_cyclone_night(),
    ]
    for p in outs:
        print(p)


if __name__ == "__main__":
    main()
