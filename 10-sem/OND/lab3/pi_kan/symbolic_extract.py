from __future__ import annotations

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

    def nth_partial(ix: int, iy: int) -> float:
        pt = torch.zeros(1, 2, device=device, dtype=dtype, requires_grad=True)
        out = model(pt).squeeze()
        cur = out
        for _ in range(ix):
            cur = torch.autograd.grad(cur, pt, create_graph=True, retain_graph=True)[0][0, 0]
        for _ in range(iy):
            cur = torch.autograd.grad(cur, pt, create_graph=True, retain_graph=True)[0][0, 1]
        return float(cur.detach().cpu())

    for d in range(order + 1):
        for i in range(d + 1):
            j = d - i
            c = nth_partial(i, j) / (sp.factorial(i) * sp.factorial(j))
            expr += c * (x**i) * (y**j)

    expr = sp.expand(expr)
    expr = prune_small_coeffs(expr, threshold=threshold, vars_=(x, y))
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


def hamiltonian_sympy(system: PolynomialSystem) -> sp.Expr:
    if system.h_coeffs_by_degree is None:
        raise RuntimeError("System has no Hamiltonian coefficients.")
    x, y = sp.symbols("x y", real=True)
    h = sp.Rational(1, 2) * (x**2 + y**2)
    for d, coeffs in sorted(system.h_coeffs_by_degree.items()):
        arr = coeffs.detach().cpu().numpy()
        for i, c in enumerate(arr):
            h += float(c) * x**i * y ** (d - i)
    return sp.expand(h)


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
    model.eval()
    h_coeffs = data.get("h_coeffs_by_degree")
    if h_coeffs is not None:
        h_coeffs = {int(d): c for d, c in h_coeffs.items()}
    system = PolynomialSystem(
        n=int(data["degree_n"]),
        p_coeffs=data.get("p_coeffs"),
        q_coeffs=data.get("q_coeffs"),
        h_coeffs_by_degree=h_coeffs,
    )
    return model, system
