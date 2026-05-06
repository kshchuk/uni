from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PIKANConfig:
    # Problem setup
    degree_n: int = 7
    domain_radius: float = 0.25
    collocation_points: int = 4096
    anchor_points: int = 256
    anchor_radius: float = 0.08

    # Training setup
    seed: int = 42
    adam_steps: int = 2000
    lbfgs_steps: int = 200
    adam_lr: float = 5e-4
    lbfgs_lr: float = 0.8
    log_every: int = 50

    # Model setup
    hidden_dim: int = 24
    depth: int = 2
    basis_type: str = "chebyshev"  # chebyshev | legendre | rbf
    basis_order: int = 8
    rbf_centers: int = 16
    rbf_sigma: float = 0.2

    # Loss weights
    lambda_anchor: float = 2.0
    lambda_origin: float = 5.0
    lambda_reg: float = 1e-6

    # Export and validation
    symbolic_threshold: float = 1e-4
    taylor_order: int = 8
    eval_grid_n: int = 121

    # Runtime
    device: str = "mps"  # GPU/ANE-first mode on Apple Silicon
    use_mps_if_available: bool = True
    output_dir: str = "lab3/pi_kan/outputs"
