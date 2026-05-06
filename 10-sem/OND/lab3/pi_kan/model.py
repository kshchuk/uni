from __future__ import annotations

from typing import Literal

import torch
import torch.nn as nn


def _scale_to_unit(x: torch.Tensor, radius: float = 1.0) -> torch.Tensor:
    # Keep values in [-1, 1] to stabilize polynomial basis.
    return torch.clamp(x / radius, -1.0, 1.0)


def chebyshev_basis(x: torch.Tensor, order: int) -> torch.Tensor:
    # T0=1, T1=x, Tn=2xTn-1-Tn-2
    b0 = torch.ones_like(x)
    if order == 0:
        return b0.unsqueeze(-1)
    b1 = x
    basis = [b0, b1]
    for _ in range(2, order + 1):
        basis.append(2.0 * x * basis[-1] - basis[-2])
    return torch.stack(basis, dim=-1)


def legendre_basis(x: torch.Tensor, order: int) -> torch.Tensor:
    # P0=1, P1=x, (n+1)Pn+1=(2n+1)xPn-nPn-1
    p0 = torch.ones_like(x)
    if order == 0:
        return p0.unsqueeze(-1)
    p1 = x
    basis = [p0, p1]
    for n in range(1, order):
        pn1 = ((2 * n + 1) * x * basis[-1] - n * basis[-2]) / (n + 1)
        basis.append(pn1)
    return torch.stack(basis, dim=-1)


class EdgeBasis1D(nn.Module):
    """
    Learnable 1D edge function:
      f(x) = sum_k w_k * basis_k(x) + bias
    Supports polynomial bases (SymPy-friendly) and optional smooth RBFs.
    """

    def __init__(
        self,
        basis_type: Literal["chebyshev", "legendre", "rbf"] = "chebyshev",
        basis_order: int = 8,
        rbf_centers: int = 16,
        rbf_sigma: float = 0.2,
        input_radius: float = 1.0,
    ) -> None:
        super().__init__()
        self.basis_type = basis_type
        self.basis_order = basis_order
        self.rbf_centers = rbf_centers
        self.rbf_sigma = rbf_sigma
        self.input_radius = input_radius

        if basis_type in {"chebyshev", "legendre"}:
            self.weights = nn.Parameter(torch.zeros(basis_order + 1))
            nn.init.normal_(self.weights, mean=0.0, std=0.05)
            self.bias = nn.Parameter(torch.zeros(1))
        elif basis_type == "rbf":
            centers = torch.linspace(-1.0, 1.0, rbf_centers)
            self.register_buffer("centers", centers)
            self.weights = nn.Parameter(torch.zeros(rbf_centers))
            nn.init.normal_(self.weights, mean=0.0, std=0.05)
            self.bias = nn.Parameter(torch.zeros(1))
        else:
            raise ValueError(f"Unsupported basis_type: {basis_type}")

    def _basis(self, x: torch.Tensor) -> torch.Tensor:
        x = _scale_to_unit(x, radius=self.input_radius)
        if self.basis_type == "chebyshev":
            return chebyshev_basis(x, self.basis_order)
        if self.basis_type == "legendre":
            return legendre_basis(x, self.basis_order)
        # RBF
        return torch.exp(-((x.unsqueeze(-1) - self.centers) / self.rbf_sigma) ** 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b = self._basis(x)
        return (b * self.weights).sum(dim=-1) + self.bias


class KANLayer(nn.Module):
    """
    KAN layer with per-edge 1D functions:
      y_j = sum_i f_ij(x_i)
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        basis_type: str,
        basis_order: int,
        rbf_centers: int,
        rbf_sigma: float,
        input_radius: float,
    ) -> None:
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.edges = nn.ModuleList(
            [
                EdgeBasis1D(
                    basis_type=basis_type,
                    basis_order=basis_order,
                    rbf_centers=rbf_centers,
                    rbf_sigma=rbf_sigma,
                    input_radius=input_radius,
                )
                for _ in range(in_features * out_features)
            ]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, in_features]
        out = []
        idx = 0
        for j in range(self.out_features):
            yj = 0.0
            for i in range(self.in_features):
                yj = yj + self.edges[idx](x[:, i])
                idx += 1
            out.append(yj)
        return torch.stack(out, dim=-1)


class PIKAN(nn.Module):
    def __init__(
        self,
        hidden_dim: int = 24,
        depth: int = 2,
        basis_type: str = "chebyshev",
        basis_order: int = 8,
        rbf_centers: int = 16,
        rbf_sigma: float = 0.2,
        input_radius: float = 0.5,
    ) -> None:
        super().__init__()
        dims = [2] + [hidden_dim] * depth + [1]
        layers = []
        for i in range(len(dims) - 1):
            layers.append(
                KANLayer(
                    in_features=dims[i],
                    out_features=dims[i + 1],
                    basis_type=basis_type,
                    basis_order=basis_order,
                    rbf_centers=rbf_centers,
                    rbf_sigma=rbf_sigma,
                    input_radius=input_radius,
                )
            )
        self.layers = nn.ModuleList(layers)

    def forward(self, xy: torch.Tensor) -> torch.Tensor:
        z = xy
        for k, layer in enumerate(self.layers):
            z = layer(z)
            if k < len(self.layers) - 1:
                # smooth nonlinearity between layers, keeps graph differentiable
                z = torch.tanh(z)
        return z

    def regularization(self) -> torch.Tensor:
        reg = 0.0
        for p in self.parameters():
            reg = reg + (p**2).mean()
        return reg


class PyKANAdapter(nn.Module):
    """
    Optional adapter. If pykan is unavailable, users should use PIKAN.
    """

    def __init__(self, width: list[int] | None = None, grid: int = 7, k: int = 3) -> None:
        super().__init__()
        width = width or [2, 16, 1]
        try:
            from kan import KAN as ExternalKAN  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("pykan is not installed. Install `pykan` or use custom PIKAN.") from exc
        self.model = ExternalKAN(width=width, grid=grid, k=k)

    def forward(self, xy: torch.Tensor) -> torch.Tensor:
        return self.model(xy)
