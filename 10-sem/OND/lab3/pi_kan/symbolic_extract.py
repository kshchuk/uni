from __future__ import annotations

import json
import gc
from pathlib import Path

import sympy as sp
import torch

from .config import PIKANConfig
from .model import PIKAN
from .system_def import PolynomialSystem


def _poly_basis_sym(basis_type: str, var: sp.Symbol, order: int) -> list[sp.Expr]:
    if basis_type == "chebyshev":
        return [sp.chebyshevt(k, var) for k in range(order + 1)]
    if basis_type == "legendre":
        return [sp.legendre(k, var) for k in range(order + 1)]
    raise ValueError(f"Unsupported symbolic direct basis: {basis_type}")


def extract_symbolic_polynomial(
    model: PIKAN,
    cfg: PIKANConfig,
    threshold: float | None = None,
) -> sp.Expr:
    """
    Direct symbolic extraction for polynomial basis (chebyshev / legendre).
    Note: for deep KAN with tanh this builds a symbolic surrogate of edge expansions
    and keeps tanh nodes as symbolic tanh. For a pure polynomial final form, use
    taylor_series_from_model below.
    """
    threshold = cfg.symbolic_threshold if threshold is None else threshold
    x, y = sp.symbols("x y", real=True)
    vars_prev = [x, y]

    for layer_idx, layer in enumerate(model.layers):
        vars_next = [sp.Symbol(f"z_{layer_idx}_{j}", real=True) for j in range(layer.out_features)]
        assignments = []
        edge_idx = 0
        for j in range(layer.out_features):
            expr_j = 0
            for i in range(layer.in_features):
                edge = layer.edges[edge_idx]
                edge_idx += 1
                v = vars_prev[i]
                if edge.basis_type in {"chebyshev", "legendre"}:
                    basis = _poly_basis_sym(edge.basis_type, v / cfg.domain_radius, edge.basis_order)
                    w = edge.weights.detach().cpu().numpy()
                    term = sum(float(w[k]) * basis[k] for k in range(len(w))) + float(edge.bias.detach().cpu())
                else:
                    # fallback symbolic for RBF edge
                    centers = edge.centers.detach().cpu().numpy()
                    weights = edge.weights.detach().cpu().numpy()
                    sigma = float(edge.rbf_sigma)
                    term = 0
                    for wk, ck in zip(weights, centers):
                        term += float(wk) * sp.exp(-((v / cfg.domain_radius - float(ck)) / sigma) ** 2)
                    term += float(edge.bias.detach().cpu())
                expr_j += term
            assignments.append(sp.expand(expr_j))
        if layer_idx < len(model.layers) - 1:
            vars_prev = [sp.tanh(a) for a in assignments]
        else:
            vars_prev = assignments

    expr = sp.expand(vars_prev[0])
    expr = sp.expand(expr)
    if threshold > 0:
        expr = prune_small_coeffs(expr, threshold=threshold, vars_=(x, y))
    return sp.simplify(expr)


def taylor_series_from_model(
    model: PIKAN,
    cfg: PIKANConfig,
    order: int | None = None,
    threshold: float | None = None,
    verbose: bool = False,
    cache_dir: str | None = None,
    cache_tag: str = "phi_taylor",
    resume: bool = True,
) -> sp.Expr:
    """
    Compute 2D Taylor polynomial of Phi at (0,0) using autograd derivatives.
    This is the recommended symbolic path for non-polynomial edge functions (rbf/splines).
    """
    order = cfg.taylor_order if order is None else order
    threshold = cfg.symbolic_threshold if threshold is None else threshold
    x, y = sp.symbols("x y", real=True)
    expr = 0
    device = next(model.parameters()).device
    dtype = next(model.parameters()).dtype
    cache_state_path: Path | None = None
    cache_expr_path: Path | None = None

    def nth_partial(ix: int, iy: int) -> float:
        pt = torch.zeros(1, 2, device=device, dtype=dtype, requires_grad=True)
        out = model(pt).squeeze()
        cur = out
        for _ in range(ix):
            cur = torch.autograd.grad(cur, pt, create_graph=True, retain_graph=False)[0][0, 0]
        for _ in range(iy):
            cur = torch.autograd.grad(cur, pt, create_graph=True, retain_graph=False)[0][0, 1]
        return float(cur.detach().cpu())

    terms: list[tuple[int, int, int]] = []
    for d in range(order + 1):
        for i in range(d + 1):
            j = d - i
            terms.append((d, i, j))
    total_terms = len(terms)
    start_idx = 0

    if cache_dir is not None:
        cdir = Path(cache_dir)
        cdir.mkdir(parents=True, exist_ok=True)
        cache_state_path = cdir / f"{cache_tag}_state.json"
        cache_expr_path = cdir / f"{cache_tag}_expr.txt"
        if resume and cache_state_path.exists() and cache_expr_path.exists():
            try:
                with open(cache_state_path, "r", encoding="utf-8") as f:
                    st = json.load(f)
                if int(st.get("order", -1)) == int(order):
                    start_idx = int(st.get("done_terms", 0))
                    expr_text = cache_expr_path.read_text(encoding="utf-8")
                    expr = sp.sympify(expr_text) if expr_text.strip() else 0
                    if verbose:
                        print(
                            f"[extractor] resumed from cache: done_terms={start_idx}/{total_terms}",
                            flush=True,
                        )
                elif verbose:
                    print("[extractor] cache exists but order mismatch, starting from scratch", flush=True)
            except Exception as exc:
                if verbose:
                    print(f"[extractor] cache load failed ({type(exc).__name__}), starting from scratch", flush=True)
                start_idx = 0
                expr = 0

    done_terms = start_idx
    if verbose:
        print(f"[extractor] Taylor order={order}, total partials={total_terms}", flush=True)

    current_d = None
    for idx, (d, i, j) in enumerate(terms):
        if idx < start_idx:
            continue
        if current_d != d:
            if current_d is not None and verbose:
                print(f"[extractor] degree d={current_d} finished", flush=True)
            current_d = d
            if verbose:
                print(f"[extractor] degree d={d} started", flush=True)

        c = nth_partial(i, j) / (sp.factorial(i) * sp.factorial(j))
        expr += c * (x**i) * (y**j)
        done_terms += 1
        if verbose and (done_terms % 5 == 0 or done_terms == total_terms):
            print(f"[extractor] progress {done_terms}/{total_terms}", flush=True)

        # Fine-grained autosave after every term.
        if cache_state_path is not None and cache_expr_path is not None:
            cache_expr_path.write_text(str(sp.expand(expr)), encoding="utf-8")
            with open(cache_state_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "order": int(order),
                        "done_terms": int(done_terms),
                        "last_degree": int(d),
                        "last_i": int(i),
                        "last_j": int(j),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        # Keep memory pressure lower on long high-order runs.
        if device.type == "mps":
            torch.mps.empty_cache()
        gc.collect()

    if current_d is not None and verbose:
        print(f"[extractor] degree d={current_d} finished", flush=True)

    expr = sp.expand(expr)
    expr = prune_small_coeffs(expr, threshold=threshold, vars_=(x, y))
    if verbose:
        print("[extractor] prune+simplify started", flush=True)
    return sp.simplify(expr)


def prune_small_coeffs(expr: sp.Expr, threshold: float, vars_: tuple[sp.Symbol, sp.Symbol]) -> sp.Expr:
    poly = sp.Poly(sp.expand(expr), *vars_)
    out = 0
    for monom, coeff in poly.terms():
        c = float(sp.N(coeff))
        if abs(c) >= threshold:
            out += c * vars_[0] ** monom[0] * vars_[1] ** monom[1]
    return sp.expand(out)


def save_symbolic_expression(expr: sp.Expr, output_dir: str) -> tuple[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    txt_path = out / "phi_symbolic.txt"
    tex_path = out / "phi_symbolic.tex"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(str(expr))
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(sp.latex(expr))
    return str(txt_path), str(tex_path)


def hamiltonian_sympy(
    system: PolynomialSystem,
    x: sp.Symbol | None = None,
    y: sp.Symbol | None = None,
) -> sp.Expr:
    if system.h_coeffs_by_degree is None:
        raise RuntimeError("System has no Hamiltonian coefficients.")
    if x is None or y is None:
        x, y = sp.symbols("x y", real=True)
    h = sp.Rational(1, 2) * (x**2 + y**2)
    for d, coeffs in sorted(system.h_coeffs_by_degree.items()):
        arr = coeffs.detach().cpu().numpy()
        for i, c in enumerate(arr):
            h += float(c) * x**i * y ** (d - i)
    return sp.expand(h)


def vector_field_P_Q_bautin_form(
    system: PolynomialSystem,
    x_sym: sp.Symbol | None = None,
    y_sym: sp.Symbol | None = None,
) -> tuple[sp.Expr, sp.Expr]:
    """
    Same ODE as the Hamiltonian field from ``system``, written in the Bautin notebook convention
    dx = -y + P(x,y), dy = x + Q(x,y).

    For H from ``hamiltonian_sympy``, one has dx = -∂H/∂y and dy = ∂H/∂x, hence
    P = -∂H/∂y + y and Q = ∂H/∂x - x (linear part cancels).

    Pass ``x_sym``, ``y_sym`` to match symbols used elsewhere (e.g. ``lyapunov_quantities`` in a notebook).
    """
    if x_sym is None or y_sym is None:
        x_sym, y_sym = sp.symbols("x y", real=True)
    H = hamiltonian_sympy(system, x_sym, y_sym)
    P = sp.expand(-sp.diff(H, y_sym) + y_sym)
    Q = sp.expand(sp.diff(H, x_sym) - x_sym)
    return P, Q


def phi_h_comparison_metrics(
    model: PIKAN,
    system: PolynomialSystem,
    radius: float,
    grid_n: int = 121,
) -> dict[str, float]:
    device = next(model.parameters()).device
    dtype = next(model.parameters()).dtype
    x = torch.linspace(-radius, radius, grid_n, device=device, dtype=dtype)
    y = torch.linspace(-radius, radius, grid_n, device=device, dtype=dtype)
    X, Y = torch.meshgrid(x, y, indexing="xy")
    pts = torch.stack([X.reshape(-1), Y.reshape(-1)], dim=-1)
    with torch.no_grad():
        phi = model(pts).squeeze(-1)
        h = system.hamiltonian_value(pts[:, 0], pts[:, 1])
        diff = phi - h
    return {
        "phi_h_mse": float((diff**2).mean().detach().cpu()),
        "phi_h_rmse": float(torch.sqrt((diff**2).mean()).detach().cpu()),
        "phi_h_max_abs": float(torch.abs(diff).max().detach().cpu()),
    }


def restore_from_checkpoint(
    checkpoint_path: str,
    cfg: PIKANConfig,
    map_location: str = "cpu",
    target_device: str | None = None,
) -> tuple[PIKAN, PolynomialSystem]:
    data = torch.load(checkpoint_path, map_location=map_location)
    model = PIKAN(
        hidden_dim=cfg.hidden_dim,
        depth=cfg.depth,
        basis_type=cfg.basis_type,
        basis_order=cfg.basis_order,
        rbf_centers=cfg.rbf_centers,
        rbf_sigma=cfg.rbf_sigma,
        input_radius=cfg.domain_radius,
    )
    model.load_state_dict(data["model_state_dict"])
    if target_device is not None:
        model = model.to(torch.device(target_device))
    model.eval()
    h_coeffs = data.get("h_coeffs_by_degree")
    if h_coeffs is not None:
        h_coeffs = {int(d): c for d, c in h_coeffs.items()}
    system = PolynomialSystem(
        n=int(data["degree_n"]),
        p_coeffs=(data.get("p_coeffs").to(torch.device(target_device)) if (data.get("p_coeffs") is not None and target_device is not None) else data.get("p_coeffs")),
        q_coeffs=(data.get("q_coeffs").to(torch.device(target_device)) if (data.get("q_coeffs") is not None and target_device is not None) else data.get("q_coeffs")),
        h_coeffs_by_degree=h_coeffs,
    )
    if target_device is not None and system.h_coeffs_by_degree is not None:
        dev = torch.device(target_device)
        system.h_coeffs_by_degree = {int(d): c.to(dev) for d, c in system.h_coeffs_by_degree.items()}
    return model, system
