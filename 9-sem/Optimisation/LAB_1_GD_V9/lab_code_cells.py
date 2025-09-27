
# Cell 0
import numpy as np

def f(x) -> np.ndarray:
    x1, x2, x3 = x
    return (200 * x1 ** 2 + 5 * x2 ** 2 + 144 * x3 ** 2
            - 24 * x1 * x2 - 48 * x1 * x3 + 24 * x2 * x3 + 5)

def grad_f(x) -> np.ndarray:
    x1, x2, x3 = x
    dfdx1 = 400 * x1 - 24 * x2 - 48 * x3
    dfdx2 = 10 * x2 - 24 * x1 + 24 * x3
    dfdx3 = 288 * x3 - 48 * x1 + 24 * x2
    return np.array([dfdx1, dfdx2, dfdx3])

grid = np.linspace(-1.2, 1.2, 12)

# Cell 1
import plotly.graph_objects as go
import ipywidgets as w
from IPython.display import display

# build surface for a chosen fixed variable and it's value
def surface_for_slice(slice_var="x3", slice_val=0.0):
    # Create 2D mesh for the two free variables
    if slice_var == "x1":
        X2, X3 = np.meshgrid(grid, grid)
        Z = f((np.full_like(X2, slice_val), X2, X3))
        x, y, z = X2, X3, Z
        xlab, ylab = "x2", "x3"
    elif slice_var == "x2":
        X1, X3 = np.meshgrid(grid, grid)
        Z = f((X1, np.full_like(X1, slice_val), X3))
        x, y, z = X1, X3, Z
        xlab, ylab = "x1", "x3"
    else:  # slice_var == "x3"
        X1, X2 = np.meshgrid(grid, grid)
        Z = f((X1, X2, slice_val))
        x, y, z = X1, X2, Z
        xlab, ylab = "x1", "x2"

    fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, showscale=False)])
    fig.update_layout(
        title=f"Surface of f with {slice_var} = {slice_val:.3f}",
        scene=dict(xaxis_title=xlab, yaxis_title=ylab, zaxis_title="f"),
        margin=dict(l=0, r=0, b=0, t=40),
        height=600
    )
    return fig

# choose which variable to fix and its value
slice_var_dd = w.Dropdown(options=["x1","x2","x3"], value="x3", description="Fix:")
slice_val_sl = w.FloatSlider(value=0.0, min=grid.min(), max=grid.max(), step=float(grid[1]-grid[0]), description="Value:")

# redraw whenever controls change
out = w.Output()
def _draw(*_):
    with out:
        out.clear_output(wait=True)
        display(surface_for_slice(slice_var_dd.value, slice_val_sl.value))

slice_var_dd.observe(_draw, names="value")
slice_val_sl.observe(_draw, names="value")

display(w.HBox([slice_var_dd, slice_val_sl]))
_draw()
display(out)


# Cell 2
X1, X2, X3 = np.meshgrid(grid, grid, grid, indexing="xy")
F = f((X1, X2, X3))

# Reasonable value range for the slider
Fmin, Fmax = np.percentile(F, 5), np.percentile(F, 95)

# --- widgets (Single level only) ---
F_value = w.FloatSlider(
    value=float((Fmin + Fmax) / 2),
    min=float(Fmin), max=float(Fmax),
    step=float((Fmax - Fmin) / 200),
    description="F =",
    readout_format=".2f",
    continuous_update=True
)
opacity = w.FloatSlider(value=0.6, min=0.1, max=1.0, step=0.05, description="Opacity")
showscale = w.Checkbox(value=True, description="Show colorbar")
btn = w.Button(description="Render", button_style="primary")
display(w.HBox([F_value, opacity, showscale, btn]))

out = w.Output()

def build_figure(F_level, opacity, showscale):
    # Single isosurface at F = F_level
    fig = go.Figure(go.Isosurface(
        x=X1.ravel(), y=X2.ravel(), z=X3.ravel(),
        value=F.ravel(),
        isomin=float(F_level), isomax=float(F_level),  # single level
        surface_count=1,
        opacity=float(opacity),
        caps=dict(x_show=False, y_show=False, z_show=False),
        colorscale="Viridis",
        showscale=bool(showscale),
        colorbar=dict(title="f", x=1.02, thickness=14, len=0.6,
                      tickfont=dict(size=10)) if showscale else None,
    ))

    fig.update_layout(
        title=f"Isosurface: F = {F_level:.2f}",
        scene=dict(xaxis_title="x1", yaxis_title="x2", zaxis_title="x3"),
        margin=dict(l=0, r=80 if showscale else 0, b=0, t=40),
        height=650
    )

    # Mark the global minimum at (0,0,0), F=5
    fig.add_scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers+text",
        marker=dict(size=6, symbol="diamond"),
        text=["min f=5 at (0,0,0)"],
        textposition="top center",
        name="Global minimum"
    )
    return fig

def _render(_=None):
    with out:
        out.clear_output(wait=True)
        display(build_figure(F_value.value, opacity.value, showscale.value))

btn.on_click(_render)
_render()
display(out)


# Cell 3
def simple_cond(f, x, p, t, f_x, grad_f) -> bool:
    """Condition for back-tracking line search: simple reduction of f.

    Parameters:
        f: Objective function, callable of the coordinates.
        x: Current point, numpy array.
        p: Search direction, numpy array.
        t: Step size (float).
        f_x: Function value at current point x (float).
    """
    x_new = x + t * p
    f_x_new = f(x_new)
    return f_x_new < f_x

# Cell 4
def goldstein_cond(f, x, p, t, f_x, grad_f, c=0.1) -> bool:
    """
    Goldstein condition:
      f(x) + (1-c) t g^T p  <=  f(x+t p)  <=  f(x) + c t g^T p

    Parameters:
        f: Objective function, callable of the coordinates.
        x: Current point, numpy array.
        p: Search direction, numpy array.
        t: Step size (float).
        f_x: Function value at current point x (float).
        grad_f: Gradient of f, callable of the coordinates.
        c: Parameter in (0, 0.5), typically around 0.1
    
    """
    g = grad_f(x)
    phi0 = np.dot(g, p)            # directional derivative at 0
    f_x_new = f(x + t * p)
    left = f_x + (1 - c) * t * phi0
    right = f_x + c * t * phi0

    return (left <= f_x_new) and (f_x_new <= right)

# Cell 5
def back_tracking(f, grad_f, x, p, cond, t0=1.0, beta=0.5, max_halves=100, c=0.1) -> float:
    """
    Goldstein line search (expand then shrink). Otherwise behaves like simple back-tracking.

    Back-tracking line search to find step size t along direction p from x
    satisfying the condition cond (a callable of (f, x, p, t)).


    Parameters:
        f: Objective function, callable of the coordinates.
        x: Current point, numpy array.
        p: Search direction, numpy array.
        cond: Condition function, callable of (f, x, p, t) returning bool.
        t0: Initial step size.
        beta: Factor for step size reduction or expansion (0 < beta < 1).
        max_halves: Maximum number of step size halvings.
    """
    t  = float(t0)
    fx = f(x)
    g  = grad_f(x)
    phi0 = np.dot(g, p)

    if cond is goldstein_cond:
        # Phase A: expand until LEFT bound holds
        for _ in range(max_halves):
            if f(x + t*p) >= fx + (1.0 - c)*t*phi0:
                break
            t /= beta
        # Phase B: shrink until RIGHT bound holds
        for _ in range(max_halves):
            if f(x + t*p) <= fx + c*t*phi0:
                return t
            t *= beta
        return t

    # simple rule (just decrease)
    for _ in range(max_halves):
        if simple_cond(f, x, p, t, fx, grad_f):
            return t
        t *= beta
    return t

# Cell 6
def norm2(v: np.ndarray) -> float:
    return np.sqrt(np.sum(v ** 2))

# Cell 7
def gd_back_tracking(f, grad_f, x0, cond, max_iters=50, tol=1e-6, c=0.5):
    """
    Gradient descent with back-tracking line search.

    Parameters:
        f: Objective function, callable of the coordinates.
        grad_f: Gradient function, callable returning numpy array.
        x0: Initial point, numpy array.
        cond: Condition function for line search.
        max_iters: Maximum number of iterations.
        tol: Tolerance for stopping criterion based on gradient norm.
    """
    x = np.array(x0, dtype=float)
    history = {"x":[x.copy()], "f":[f(x)], "t":[], "grad_norm":[]}

    for _ in range(max_iters):
        g = grad_f(x)
        gnorm = norm2(g)
        history["grad_norm"].append(gnorm)
        if gnorm < tol:
            break

        p = -g
        assert np.dot(g, p) < 0, "Not a descent direction!"

        # line search to find step size with the given condition (simple or Goldstein)
        t = back_tracking(f, grad_f, x, p, cond, c)
        assert t > 0, "Line search failed to find a valid step size!"

        x += t * p

        history["x"].append(x.copy())
        history["f"].append(f(x))
        history["t"].append(t)

    return x, history

# Cell 8
# Initial point
x0 = np.array([1.0, 1.0, 1.0])

# Run gradient descent with back-tracking
x_min, history = gd_back_tracking(f, grad_f, x0, simple_cond, max_iters=50, tol=1e-6)
print(f"Found minimum at x = {x_min}, f = {f(x_min)}")

# Cell 9
import numpy as np

def f_adapter(f_raw):
    def fA(x_tuple):
        try:
            return f_raw(x_tuple)         
        except TypeError:
            x1, x2, x3 = x_tuple
            return f_raw(x1, x2, x3)      
    return fA


# Cell 10
import plotly.graph_objects as go
import ipywidgets as w
from IPython.display import display

def show_isosurface_with_path(f_raw, history, grid_range=(-1.2, 1.2), vol_n=50):
    f = f_adapter(f_raw)

    P = np.array(history["x"])  # (K+1, 3)

    gmin, gmax = grid_range
    vol_grid = np.linspace(gmin, gmax, int(vol_n))
    X1v, X2v, X3v = np.meshgrid(vol_grid, vol_grid, vol_grid, indexing="xy")
    Fvol = f((X1v, X2v, X3v))
    Fmin, Fmax = np.percentile(Fvol, 5), np.percentile(Fvol, 95)

    level   = w.FloatSlider(value=float((Fmin+Fmax)/2), min=float(Fmin), max=float(Fmax),
                            step=float((Fmax-Fmin)/200), description="F =", readout_format=".2f",
                            continuous_update=True)
    opacity = w.FloatSlider(value=0.45, min=0.1, max=1.0, step=0.05,
                            description="Opacity", continuous_update=True)
    cbar    = w.Checkbox(value=True, description="Show colorbar")
    display(w.HBox([level, opacity, cbar]))

    figw = go.FigureWidget()
    figw.update_layout(
        title=f"Isosurface: F = {level.value:.2f}",
        height=650,
        margin=dict(l=0, r=80, b=0, t=40),
        scene=dict(xaxis_title="x1", yaxis_title="x2", zaxis_title="x3"),
    )

    iso = go.Isosurface(
        x=X1v.ravel(), y=X2v.ravel(), z=X3v.ravel(), value=Fvol.ravel(),
        isomin=float(level.value), isomax=float(level.value), surface_count=1,
        opacity=float(opacity.value),
        caps=dict(x_show=False, y_show=False, z_show=False),
        colorscale="Viridis", showscale=bool(cbar.value),
        colorbar=dict(title="f", x=1.02, thickness=14, len=0.6, tickfont=dict(size=10))
    )
    path = go.Scatter3d(
        x=P[:,0], y=P[:,1], z=P[:,2],
        mode="lines+markers", name="Path",
        marker=dict(size=4), line=dict(width=4),
        hovertemplate="iter=%{customdata}<br>x1=%{x:.3f}, x2=%{y:.3f}, x3=%{z:.3f}<extra></extra>",
        customdata=np.arange(len(P))
    )
    figw.add_traces([iso, path])
    display(figw)

    iso_tr = figw.data[0]
    def _on_level(ch):
        val = float(ch["new"])
        with figw.batch_update():
            iso_tr.isomin = val
            iso_tr.isomax = val
            figw.layout.title = f"Isosurface: F = {val:.2f}"
    def _on_opacity(ch):
        iso_tr.opacity = float(ch["new"])
    def _on_cbar(ch):
        iso_tr.showscale = bool(ch["new"])
        figw.layout.margin.r = 80 if iso_tr.showscale else 0

    level.observe(_on_level, names="value")
    opacity.observe(_on_opacity, names="value")
    cbar.observe(_on_cbar, names="value")


# Cell 11
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def plot_metrics(history, log_f=True, log_grad=True):
    fvals = np.array(history.get("f", []))
    tvals = np.array(history.get("t", []))
    gnorm = np.array(history.get("grad_norm", []))

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("f(x_k)", "step size t_k", "||grad f(x_k)||"),
        specs=[[{"type":"scatter"}, {"type":"scatter"}],
               [{"type":"scatter"}, None]]
    )
    if fvals.size:
        fig.add_trace(go.Scatter(y=fvals, mode="lines+markers", name="f"), row=1, col=1)
        if log_f: fig.update_yaxes(type="log", row=1, col=1)
    if tvals.size:
        fig.add_trace(go.Scatter(y=tvals, mode="lines+markers", name="t"), row=1, col=2)
    if gnorm.size:
        fig.add_trace(go.Scatter(y=gnorm, mode="lines+markers", name="||grad||"), row=2, col=1)
        if log_grad: fig.update_yaxes(type="log", row=2, col=1)

    fig.update_layout(height=700, width=900, title_text="Optimization metrics")
    fig.update_xaxes(title_text="iteration", row=1, col=1)
    fig.update_xaxes(title_text="iteration", row=1, col=2)
    fig.update_xaxes(title_text="iteration", row=2, col=1)
    fig.update_yaxes(title_text="f", row=1, col=1)
    fig.update_yaxes(title_text="t", row=1, col=2)
    fig.update_yaxes(title_text="||grad f||", row=2, col=1)
    fig.show()


# Cell 12
import matplotlib.pyplot as plt
from matplotlib import animation

def save_video_xyz(history, filename="path_xyz.mp4", fps=8):
    P = np.array(history["x"])
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("x1"); ax.set_ylabel("x2"); ax.set_zlabel("x3")

    pad = 0.15
    ax.set_xlim(P[:,0].min()-pad, P[:,0].max()+pad)
    ax.set_ylim(P[:,1].min()-pad, P[:,1].max()+pad)
    ax.set_zlim(P[:,2].min()-pad, P[:,2].max()+pad)

    line, = ax.plot([], [], [], lw=2, c="tab:blue")
    point, = ax.plot([], [], [], "o", c="tab:red")

    def init():
        line.set_data([], []); line.set_3d_properties([])
        point.set_data([], []); point.set_3d_properties([])
        return line, point

    def update(i):
        line.set_data(P[:i+1,0], P[:i+1,1])
        line.set_3d_properties(P[:i+1,2])
        point.set_data(P[i,0:1], P[i,1:2])
        point.set_3d_properties(P[i,2:3])
        return line, point

    ani = animation.FuncAnimation(fig, update, init_func=init,
                                  frames=len(P), interval=int(1000/fps), blit=True)
    ani.save(filename, writer="ffmpeg", fps=fps)
    plt.close(fig)
    print(f"Saved 3D trajectory video to {filename}")


# Cell 13
show_isosurface_with_path(f, history, grid_range=(-1.2, 1.2), vol_n=50)
plot_metrics(history, log_f=True, log_grad=True)
save_video_xyz(history, filename="opt_path_simple.mp4", fps=8)


# Cell 14
x0 = np.array([-10.0, 10.0, 1.0])

# Run gradient descent with back-tracking
x_min, history = gd_back_tracking(f, grad_f, x0, goldstein_cond, max_iters=50, tol=1e-6, c=0.7)
print(f"Found minimum at x = {x_min}, f = {f(x_min)}")

# Cell 15
show_isosurface_with_path(f, history, grid_range=(-1.2, 1.2), vol_n=50)
plot_metrics(history, log_f=True, log_grad=True)
save_video_xyz(history, filename="opt_path_goldstein.mp4", fps=8)

