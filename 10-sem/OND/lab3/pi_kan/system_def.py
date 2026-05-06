from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class PolynomialSystem:
    n: int
    p_coeffs: torch.Tensor | None = None  # legacy non-Hamiltonian mode
    q_coeffs: torch.Tensor | None = None
    # Hamiltonian mode: map degree d -> coeff tensor shape (d+1,)
    h_coeffs_by_degree: dict[int, torch.Tensor] | None = None

    def _homogeneous_poly(self, x: torch.Tensor, y: torch.Tensor, coeffs: torch.Tensor) -> torch.Tensor:
        terms = []
        for i in range(coeffs.shape[0]):
            terms.append(coeffs[i] * (x**i) * (y ** (self.n - i)))
        return torch.stack(terms, dim=0).sum(dim=0)

    def P(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        if self.p_coeffs is None:
            raise RuntimeError("P(x,y) is unavailable in Hamiltonian mode.")
        return self._homogeneous_poly(x, y, self.p_coeffs)

    def Q(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        if self.q_coeffs is None:
            raise RuntimeError("Q(x,y) is unavailable in Hamiltonian mode.")
        return self._homogeneous_poly(x, y, self.q_coeffs)

    def vector_field(self, x: torch.Tensor, y: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if self.h_coeffs_by_degree is not None:
            return self._hamiltonian_vector_field(x, y)
        # Base linear center part + homogeneous perturbation
        dx = -y + self.P(x, y)
        dy = x + self.Q(x, y)
        return dx, dy

    def _hamiltonian_vector_field(self, x: torch.Tensor, y: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # H(x,y)=0.5(x^2+y^2)+sum_{d=3}^{n+1} sum_i c_{d,i} x^i y^(d-i)
        dx = -y
        dy = x
        for d, coeffs in self.h_coeffs_by_degree.items():
            for i in range(d + 1):
                c = coeffs[i]
                jy = d - i
                if jy > 0:
                    dx = dx - c * jy * (x**i) * (y ** (jy - 1))
                if i > 0:
                    dy = dy + c * i * (x ** (i - 1)) * (y**jy)
        return dx, dy

    def hamiltonian_value(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        if self.h_coeffs_by_degree is None:
            raise RuntimeError("Hamiltonian value is unavailable for non-Hamiltonian mode.")
        h = 0.5 * (x**2 + y**2)
        for d, coeffs in self.h_coeffs_by_degree.items():
            for i in range(d + 1):
                h = h + coeffs[i] * (x**i) * (y ** (d - i))
        return h


def make_test_system(
    n: int = 7,
    scale: float = 0.1,
    seed: int = 42,
    device: torch.device | str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> PolynomialSystem:
    """
    Create one fixed random Hamiltonian-center system.
    H(x,y) = 0.5*(x^2+y^2) + H_nonlin, where H_nonlin uses random coefficients
    from degrees 3 to n+1. Then:
      dx = -dH/dy, dy = dH/dx.
    This guarantees L[H] = 0 exactly.
    """
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    h_coeffs_by_degree: dict[int, torch.Tensor] = {}
    for d in range(3, n + 2):
        c = scale * (2 * torch.rand(d + 1, generator=g) - 1)
        h_coeffs_by_degree[d] = c.to(device=device, dtype=dtype)
    return PolynomialSystem(
        n=n,
        h_coeffs_by_degree=h_coeffs_by_degree,
    )


def sample_collocation(
    m: int,
    r: float,
    device: torch.device | str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> tuple[torch.Tensor, torch.Tensor]:
    x = (2 * torch.rand(m, device=device, dtype=dtype) - 1) * r
    y = (2 * torch.rand(m, device=device, dtype=dtype) - 1) * r
    return x, y


def sample_anchor(
    k: int,
    r0: float,
    device: torch.device | str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> tuple[torch.Tensor, torch.Tensor]:
    # Sample uniformly in a disk near origin.
    theta = 2 * torch.pi * torch.rand(k, device=device, dtype=dtype)
    rho = r0 * torch.sqrt(torch.rand(k, device=device, dtype=dtype))
    x = rho * torch.cos(theta)
    y = rho * torch.sin(theta)
    return x, y


def sample_boundary(
    b: int,
    r: float,
    device: torch.device | str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> tuple[torch.Tensor, torch.Tensor]:
    theta = 2 * torch.pi * torch.rand(b, device=device, dtype=dtype)
    x = r * torch.cos(theta)
    y = r * torch.sin(theta)
    return x, y
