#!/usr/bin/env python3
"""Генерує standalone інтерактивну HTML-візуалізацію 3D-розподілу температури
у тонкій пластині з нагрівачем позаду (розділ Д.3 звіту).

Виводить файл:
  lr1/figures/interactive_3d.html   (можна відкривати у будь-якому браузері)

Керування у результаті:
  - миша: обертання, наближення, панорамування 3D-сцени
  - слайдер часу знизу: перехід між моментами часу
  - кнопки Play / Pause для автопрогравання
  - toggle-кнопки: показати/сховати грані, внутрішній розтин, профіль по z
"""
import os
import numpy as np
import plotly.graph_objects as go

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

# --------------------------------------------------------------- problem
a = 1.0
Lx = Ly = 1.0
Lz = 1.0 / 50.0
Nx = Ny = 30
Nz = 6
hx = Lx / Nx
hy = Ly / Ny
hz = Lz / Nz
x = np.linspace(0.0, Lx, Nx + 1)
y = np.linspace(0.0, Ly, Ny + 1)
z = np.linspace(0.0, Lz, Nz + 1)
X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

x0 = 0.5 * Lx
y0 = 0.5 * Ly
Q = 1200.0  # потужність нагрівача; збільште для сильнішого нагріву
sigma_xy = 0.15
sigma_z = Lz / 6.0
F = (
    Q
    * np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * sigma_xy ** 2))
    * np.exp(-(Z ** 2) / (2 * sigma_z ** 2))
)

BIOT_FRONT = 0.35

tau_max = 1.0 / (2.0 * a * (1.0 / hx ** 2 + 1.0 / hy ** 2 + 1.0 / hz ** 2))
tau = 0.4 * tau_max
T_end = 0.01
nsteps = int(np.ceil(T_end / tau))
# 24 кадри (достатньо плавно, але HTML не надто великий)
N_FRAMES = 24
frame_ids = np.linspace(0, nsteps, N_FRAMES + 1).astype(int)


def laplacian_mixed(U, hx, hy, hz, Lz_plate, biot_front):
    nx, ny, nz_ = U.shape
    G = np.empty((nx + 2, ny + 2, nz_ + 2))
    G[1:-1, 1:-1, 1:-1] = U
    G[0, 1:-1, 1:-1] = G[2, 1:-1, 1:-1]
    G[-1, 1:-1, 1:-1] = G[-3, 1:-1, 1:-1]
    G[1:-1, 0, 1:-1] = G[1:-1, 2, 1:-1]
    G[1:-1, -1, 1:-1] = G[1:-1, -3, 1:-1]
    G[1:-1, 1:-1, 0] = G[1:-1, 1:-1, 2]
    G[1:-1, 1:-1, -1] = G[1:-1, 1:-1, -3] - 2.0 * hz * (biot_front / Lz_plate) * G[1:-1, 1:-1, -2]
    L = (
        (G[2:, 1:-1, 1:-1] - 2 * G[1:-1, 1:-1, 1:-1] + G[:-2, 1:-1, 1:-1]) / (hx * hx)
        + (G[1:-1, 2:, 1:-1] - 2 * G[1:-1, 1:-1, 1:-1] + G[1:-1, :-2, 1:-1]) / (hy * hy)
        + (G[1:-1, 1:-1, 2:] - 2 * G[1:-1, 1:-1, 1:-1] + G[1:-1, 1:-1, :-2]) / (hz * hz)
    )
    return L


print(f"Running 3D simulation: {nsteps} steps, saving {N_FRAMES+1} frames...")
U = np.zeros_like(X)
snapshots = [U.copy()]
snap_times = [0.0]
t = 0.0
for step in range(nsteps):
    dt = min(tau, T_end - t)
    Lap = laplacian_mixed(U, hx, hy, hz, Lz, BIOT_FRONT)
    U = U + dt * (Lap + F)
    t += dt
    if (step + 1) in frame_ids:
        snapshots.append(U.copy())
        snap_times.append(t)
print(f"Collected {len(snapshots)} snapshots, max w = {max(s.max() for s in snapshots):.4e}")

# -------------------------------------------------------- plotly figure
Z_SCALE = 15.0  # візуальний розтяг по z, інакше пластина майже пласка
z_vis = z * Z_SCALE
Lz_vis = Lz * Z_SCALE


def make_frame_traces(U, vmax):
    """Побудувати набір trace'ів для одного кадру:
    1. Задня грань z=0 (нагрівач)
    2. Передня грань z=Lz
    3. Грань x=0
    4. Грань x=Lx
    5. Грань y=0
    6. Грань y=Ly
    7. Внутрішня площина розтину y=y0 (для вмикання)
    """
    cmap = "Turbo"
    kwargs = dict(
        colorscale=cmap, cmin=0.0, cmax=vmax, showscale=False,
        lighting=dict(ambient=1.0, diffuse=0.35, specular=0.05),
    )
    traces = []

    # Задня z=0 (нагрівач)
    Z0 = np.zeros_like(X[:, :, 0])
    traces.append(
        go.Surface(
            x=X[:, :, 0], y=Y[:, :, 0], z=Z0,
            surfacecolor=U[:, :, 0], **kwargs, name="Задня z=0",
        )
    )
    # Передня z=Lz
    Zf = np.full_like(X[:, :, 0], Lz_vis)
    traces.append(
        go.Surface(
            x=X[:, :, 0], y=Y[:, :, 0], z=Zf,
            surfacecolor=U[:, :, -1], **kwargs, name="Передня z=Lz (конвекція)",
        )
    )
    # x=0
    Yl, Zl = np.meshgrid(y, z_vis, indexing="ij")
    Xl = np.zeros_like(Yl)
    traces.append(
        go.Surface(x=Xl, y=Yl, z=Zl, surfacecolor=U[0, :, :], **kwargs, name="x=0")
    )
    # x=Lx
    Xr = np.full_like(Yl, Lx)
    traces.append(
        go.Surface(x=Xr, y=Yl, z=Zl, surfacecolor=U[-1, :, :], **kwargs, name="x=Lx")
    )
    # y=0
    Xbw, Zbw = np.meshgrid(x, z_vis, indexing="ij")
    Yb_ = np.zeros_like(Xbw)
    traces.append(
        go.Surface(x=Xbw, y=Yb_, z=Zbw, surfacecolor=U[:, 0, :], **kwargs, name="y=0")
    )
    # y=Ly
    Yt = np.full_like(Xbw, Ly)
    traces.append(
        go.Surface(x=Xbw, y=Yt, z=Zbw, surfacecolor=U[:, -1, :], **kwargs, name="y=Ly")
    )
    # Внутрішня площина розтину y=y0 (прихована за замовчуванням)
    j0 = Ny // 2
    Yc = np.full_like(Xbw, y[j0])
    cut_trace = go.Surface(
        x=Xbw, y=Yc, z=Zbw, surfacecolor=U[:, j0, :], **kwargs,
        name="Розтин y=y0", visible=False,
    )
    traces.append(cut_trace)

    # Профіль по z через центр (як 3D-лінія з кольоровими маркерами)
    i0 = Nx // 2
    profile_vals = U[i0, j0, :]
    profile_line = go.Scatter3d(
        x=np.full_like(z_vis, x[i0]),
        y=np.full_like(z_vis, y[j0]),
        z=z_vis,
        mode="lines+markers",
        line=dict(color="white", width=6),
        marker=dict(
            size=6, color=profile_vals, colorscale=cmap, cmin=0.0, cmax=vmax,
            line=dict(color="black", width=1),
        ),
        name="Профіль по z",
        visible=False,
    )
    traces.append(profile_line)

    return traces


vmax_global = float(max(s.max() for s in snapshots) * 1.02)
# Початковий вигляд — останній кадр (при t=0 усе нуль і куб чорний на шкалі)
i0_last = len(snapshots) - 1
init_traces = make_frame_traces(snapshots[i0_last], vmax_global)

# Додаємо візуальну «шкалу» як додатковий невидимий об'єкт (для colorbar)
colorbar_trace = go.Surface(
    x=[[0]], y=[[0]], z=[[0]],
    surfacecolor=[[0]], colorscale="Turbo",
    cmin=0.0, cmax=vmax_global,
    showscale=True,
    colorbar=dict(title=dict(text="w", side="right"), thickness=18, len=0.7, x=1.02),
    opacity=0.0,
    name="colorbar",
    showlegend=False,
)

fig = go.Figure(data=init_traces + [colorbar_trace])

# Каркас паралелепіпеда -- як незмінний trace
corners = np.array([
    [0, 0, 0], [Lx, 0, 0], [Lx, Ly, 0], [0, Ly, 0],
    [0, 0, Lz_vis], [Lx, 0, Lz_vis], [Lx, Ly, Lz_vis], [0, Ly, Lz_vis],
])
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
for a_i, b_i in edges:
    fig.add_trace(
        go.Scatter3d(
            x=[corners[a_i, 0], corners[b_i, 0]],
            y=[corners[a_i, 1], corners[b_i, 1]],
            z=[corners[a_i, 2], corners[b_i, 2]],
            mode="lines",
            line=dict(color="rgba(80,80,80,0.85)", width=1.5),
            showlegend=False,
            hoverinfo="skip",
        )
    )

# Frames для слайдера потужності (використовуємо фінальний момент часу, масштабуємо за Q)
U_final_ref = snapshots[-1]
power_levels = np.array([300, 600, 900, 1200, 1500, 1800, 2400], dtype=float)
frames = []
for pwr in power_levels:
    scale = pwr / Q
    tr = make_frame_traces(U_final_ref * scale, vmax_global * (pwr / power_levels.max()))
    frames.append(
        go.Frame(
            data=tr,
            name=f"P{int(pwr)}",
            traces=list(range(len(tr))),  # оновлюємо перші 8 trace'ів
        )
    )
fig.frames = frames

# Шейп і вигляд сцени
fig.update_layout(
    title=(
        "3D: gaussian_back_heater; слайдер — потужність нагрівача (Q), "
        "показано фінальний момент часу"
    ),
    scene=dict(
        xaxis=dict(title="x", range=[0, Lx]),
        yaxis=dict(title="y", range=[0, Ly]),
        zaxis=dict(title=f"z (×{Z_SCALE:.0f}, реальна {Lz:.3f})", range=[0, Lz_vis]),
        aspectratio=dict(x=1, y=1, z=0.35),
        camera=dict(eye=dict(x=1.35, y=-0.55, z=0.45), center=dict(x=0.45, y=0.45, z=0.12)),
    ),
    width=1100,
    height=720,
    margin=dict(l=10, r=10, t=60, b=10),
)

# Слайдер потужності
steps = []
for pwr in power_levels:
    steps.append(
        dict(
            method="animate",
            label=f"{int(pwr)}",
            args=[
                [f"P{int(pwr)}"],
                dict(frame=dict(duration=0, redraw=True), mode="immediate",
                     transition=dict(duration=0)),
            ],
        )
    )

fig.update_layout(
    updatemenus=[
        # Кнопки toggles для розтину та профілю
        dict(
            type="buttons",
            direction="right",
            showactive=True,
            y=1.08, x=0.0, xanchor="left", yanchor="top",
            buttons=[
                dict(
                    label="Лише грані",
                    method="update",
                    args=[{"visible": [True, True, True, True, True, True, False, False]
                           + [True] * (len(fig.data) - 8)}],
                ),
                dict(
                    label="+ Розтин y=y0",
                    method="update",
                    args=[{"visible": [True, True, True, True, True, True, True, False]
                           + [True] * (len(fig.data) - 8)}],
                ),
                dict(
                    label="+ Профіль z",
                    method="update",
                    args=[{"visible": [True, True, True, True, True, True, True, True]
                           + [True] * (len(fig.data) - 8)}],
                ),
            ],
        ),
    ],
    sliders=[dict(
        active=int(np.where(power_levels == 1200)[0][0]),
        currentvalue=dict(prefix="Q = ", suffix=" (безрозм.)", xanchor="right"),
        pad=dict(t=50, b=10),
        steps=steps,
    )],
)

out = os.path.join(HERE, "interactive_3d.html")
fig.write_html(out, include_plotlyjs="cdn", full_html=True, auto_play=False)
print(f"Wrote {out}  ({os.path.getsize(out)/1024:.1f} KB)")
