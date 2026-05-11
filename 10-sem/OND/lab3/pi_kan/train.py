from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import torch

from .config import PIKANConfig
from .model import PIKAN
from .system_def import PolynomialSystem, make_test_system, sample_anchor, sample_collocation
from .utils import ensure_dir, resolve_device, set_seed


def _grad_scalar_output(output: torch.Tensor, inputs: torch.Tensor) -> torch.Tensor:
    return torch.autograd.grad(
        outputs=output,
        inputs=inputs,
        grad_outputs=torch.ones_like(output),
        create_graph=True,
        retain_graph=True,
    )[0]


def compute_loss(
    model: PIKAN,
    system: PolynomialSystem,
    xc: torch.Tensor,
    yc: torch.Tensor,
    xa: torch.Tensor,
    ya: torch.Tensor,
    cfg: PIKANConfig,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    collocation = torch.stack([xc, yc], dim=-1).requires_grad_(True)
    phi_c = model(collocation).squeeze(-1)
    grads = _grad_scalar_output(phi_c, collocation)
    dphi_dx = grads[:, 0]
    dphi_dy = grads[:, 1]

    dx, dy = system.vector_field(collocation[:, 0], collocation[:, 1])
    lie = dphi_dx * dx + dphi_dy * dy
    l_pde = (lie**2).mean()

    anchors = torch.stack([xa, ya], dim=-1)
    phi_a = model(anchors).squeeze(-1)
    target_a = xa**2 + ya**2
    l_anchor = ((phi_a - target_a) ** 2).mean()

    # Hard origin constraints: grad Phi(0)=0 and Hessian Phi(0)=2I
    origin = torch.zeros(1, 2, device=xc.device, dtype=xc.dtype, requires_grad=True)
    phi0 = model(origin).squeeze(-1)
    grad0 = _grad_scalar_output(phi0, origin)  # [1, 2]
    h_rows = []
    for i in range(2):
        gi = grad0[:, i]
        hi = _grad_scalar_output(gi, origin)  # [1,2]
        h_rows.append(hi)
    hessian = torch.stack(h_rows, dim=0).squeeze(1)  # [2,2]

    eye2 = 2.0 * torch.eye(2, device=xc.device, dtype=xc.dtype)
    l_origin = (grad0**2).mean() + ((hessian - eye2) ** 2).mean()

    l_reg = model.regularization()
    total = l_pde + cfg.lambda_anchor * l_anchor + cfg.lambda_origin * l_origin + cfg.lambda_reg * l_reg

    parts = {
        "total": total,
        "pde": l_pde.detach(),
        "anchor": l_anchor.detach(),
        "origin": l_origin.detach(),
        "reg": l_reg.detach(),
        "lie_l2": torch.sqrt((lie**2).mean()).detach(),
    }
    return total, parts


def _train_adam(
    model: PIKAN,
    system: PolynomialSystem,
    cfg: PIKANConfig,
    device: torch.device,
    logs: list[dict[str, Any]],
) -> dict[str, Any]:
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.adam_lr)
    best = {"loss": float("inf"), "state_dict": None, "step": -1}
    for step in range(1, cfg.adam_steps + 1):
        xc, yc = sample_collocation(cfg.collocation_points, cfg.domain_radius, device=device)
        xa, ya = sample_anchor(cfg.anchor_points, cfg.anchor_radius, device=device)

        optimizer.zero_grad(set_to_none=True)
        loss, parts = compute_loss(model, system, xc, yc, xa, ya, cfg)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        loss_val = float(loss.detach().cpu())
        if loss_val < best["loss"]:
            best["loss"] = loss_val
            best["state_dict"] = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best["step"] = step

        if step % cfg.log_every == 0 or step == 1 or step == cfg.adam_steps:
            entry = {
                "stage": "adam",
                "step": step,
                "loss_total": float(parts["total"].detach().cpu()),
                "loss_pde": float(parts["pde"].cpu()),
                "loss_anchor": float(parts["anchor"].cpu()),
                "loss_origin": float(parts["origin"].cpu()),
                "lie_l2": float(parts["lie_l2"].cpu()),
            }
            logs.append(entry)
            print(
                f"[adam {step:5d}] total={entry['loss_total']:.4e} "
                f"pde={entry['loss_pde']:.4e} anchor={entry['loss_anchor']:.4e} "
                f"origin={entry['loss_origin']:.4e} lie_l2={entry['lie_l2']:.4e}"
            )
    return best


def _train_lbfgs(
    model: PIKAN,
    system: PolynomialSystem,
    cfg: PIKANConfig,
    device: torch.device,
    logs: list[dict[str, Any]],
) -> dict[str, Any]:
    optimizer = torch.optim.LBFGS(
        model.parameters(),
        lr=cfg.lbfgs_lr,
        max_iter=cfg.lbfgs_steps,
        history_size=25,
        line_search_fn="strong_wolfe",
    )
    best = {"loss": float("inf"), "state_dict": None, "step": -1}

    # Fixed collocation batch during LBFGS for stable closure behavior
    xc, yc = sample_collocation(cfg.collocation_points, cfg.domain_radius, device=device)
    xa, ya = sample_anchor(cfg.anchor_points, cfg.anchor_radius, device=device)

    step_counter = {"n": 0}

    def closure() -> torch.Tensor:
        optimizer.zero_grad(set_to_none=True)
        loss, parts = compute_loss(model, system, xc, yc, xa, ya, cfg)
        loss.backward()
        step_counter["n"] += 1
        if step_counter["n"] % cfg.log_every == 0 or step_counter["n"] == 1:
            entry = {
                "stage": "lbfgs",
                "step": step_counter["n"],
                "loss_total": float(parts["total"].detach().cpu()),
                "loss_pde": float(parts["pde"].cpu()),
                "loss_anchor": float(parts["anchor"].cpu()),
                "loss_origin": float(parts["origin"].cpu()),
                "lie_l2": float(parts["lie_l2"].cpu()),
            }
            logs.append(entry)
            print(
                f"[lbfgs {entry['step']:5d}] total={entry['loss_total']:.4e} "
                f"pde={entry['loss_pde']:.4e} anchor={entry['loss_anchor']:.4e} "
                f"origin={entry['loss_origin']:.4e} lie_l2={entry['lie_l2']:.4e}"
            )
        loss_val = float(loss.detach().cpu())
        if loss_val < best["loss"]:
            best["loss"] = loss_val
            best["state_dict"] = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best["step"] = step_counter["n"]
        return loss

    optimizer.step(closure)
    return best


def _save_artifacts(
    model: PIKAN,
    system: PolynomialSystem,
    cfg: PIKANConfig,
    logs: list[dict[str, Any]],
    out_dir: Path,
    ckpt_name: str = "best_model.pt",
) -> tuple[str, str, str]:
    ckpt_path = out_dir / ckpt_name
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": asdict(cfg),
            "p_coeffs": system.p_coeffs.detach().cpu() if system.p_coeffs is not None else None,
            "q_coeffs": system.q_coeffs.detach().cpu() if system.q_coeffs is not None else None,
            "h_coeffs_by_degree": {
                int(d): c.detach().cpu() for d, c in (system.h_coeffs_by_degree or {}).items()
            },
            "degree_n": system.n,
        },
        ckpt_path,
    )

    logs_path = out_dir / "train_logs.json"
    with open(logs_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    cfg_path = out_dir / "run_config.json"
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, ensure_ascii=False, indent=2)

    return str(ckpt_path), str(cfg_path), str(logs_path)


def train(cfg: PIKANConfig | None = None) -> dict[str, Any]:
    cfg = cfg or PIKANConfig()
    set_seed(cfg.seed)
    device = resolve_device(use_mps_if_available=cfg.use_mps_if_available)
    if cfg.device == "cpu":
        device = torch.device("cpu")

    out_dir = Path(cfg.output_dir)
    ensure_dir(str(out_dir))

    model = PIKAN(
        hidden_dim=cfg.hidden_dim,
        depth=cfg.depth,
        basis_type=cfg.basis_type,
        basis_order=cfg.basis_order,
        rbf_centers=cfg.rbf_centers,
        rbf_sigma=cfg.rbf_sigma,
        input_radius=cfg.domain_radius,
    ).to(device)
    system = make_test_system(
        n=cfg.degree_n,
        scale=cfg.hamiltonian_scale,
        seed=cfg.seed,
        device=device,
    )
    logs: list[dict[str, Any]] = []

    # Resume from checkpoint if requested.
    if cfg.resume_from_checkpoint:
        ckpt = torch.load(cfg.resume_from_checkpoint, map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])
        h_coeffs = ckpt.get("h_coeffs_by_degree")
        if h_coeffs is not None:
            h_coeffs = {int(d): c.to(device=device) for d, c in h_coeffs.items()}
        system = PolynomialSystem(
            n=int(ckpt["degree_n"]),
            p_coeffs=ckpt.get("p_coeffs").to(device=device) if ckpt.get("p_coeffs") is not None else None,
            q_coeffs=ckpt.get("q_coeffs").to(device=device) if ckpt.get("q_coeffs") is not None else None,
            h_coeffs_by_degree=h_coeffs,
        )
        print(f"Resumed from checkpoint: {cfg.resume_from_checkpoint}")

    # MPS fallback guard for higher-order autograd operations.
    if str(device) == "mps":
        try:
            xc, yc = sample_collocation(8, cfg.domain_radius, device=device)
            xa, ya = sample_anchor(8, cfg.anchor_radius, device=device)
            test_loss, _ = compute_loss(model, system, xc, yc, xa, ya, cfg)
            _ = float(test_loss.detach().cpu())
        except Exception as exc:
            print(f"MPS autograd check failed ({type(exc).__name__}); falling back to CPU.")
            device = torch.device("cpu")
            model = model.to(device)
            system = make_test_system(
                n=cfg.degree_n,
                scale=cfg.hamiltonian_scale,
                seed=cfg.seed,
                device=device,
            )

    interrupted = False
    try:
        if not cfg.only_lbfgs and cfg.adam_steps > 0:
            best_adam = _train_adam(model, system, cfg, device, logs)
            if best_adam["state_dict"] is not None:
                model.load_state_dict(best_adam["state_dict"])
        else:
            print("Skipping Adam phase.")

        best_lbfgs = _train_lbfgs(model, system, cfg, device, logs)
        if best_lbfgs["state_dict"] is not None:
            model.load_state_dict(best_lbfgs["state_dict"])
    except KeyboardInterrupt:
        interrupted = True
        print("\nKeyboardInterrupt received: saving interrupt checkpoint...")

    ckpt_name = "interrupt_model.pt" if interrupted else "best_model.pt"
    ckpt_path, cfg_path, logs_path = _save_artifacts(
        model=model,
        system=system,
        cfg=cfg,
        logs=logs,
        out_dir=out_dir,
        ckpt_name=ckpt_name,
    )
    print(f"Saved checkpoint: {ckpt_path}")
    return {
        "model": model,
        "system": system,
        "logs": logs,
        "checkpoint_path": ckpt_path,
        "config_path": cfg_path,
        "logs_path": logs_path,
        "device": str(device),
        "interrupted": interrupted,
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train PI-KAN model.")
    p.add_argument(
        "--resume-from-checkpoint",
        type=str,
        default=None,
        help="Path to checkpoint (best_model.pt) to resume from.",
    )
    p.add_argument(
        "--only-lbfgs",
        action="store_true",
        help="Skip Adam and run only LBFGS (typically with --resume-from-checkpoint).",
    )
    p.add_argument(
        "--degree-n",
        type=int,
        default=None,
        help="System size n: nonlinear Hamiltonian terms for degrees 3..n+1 (default: PIKANConfig.degree_n).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for Hamiltonian coefficients (default: PIKANConfig.seed).",
    )
    p.add_argument(
        "--hamiltonian-scale",
        type=float,
        default=None,
        help="Scale for random nonlinear H coefficients (default: PIKANConfig.hamiltonian_scale).",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    cfg_kw: dict[str, Any] = {
        "resume_from_checkpoint": args.resume_from_checkpoint,
        "only_lbfgs": args.only_lbfgs,
    }
    if args.degree_n is not None:
        cfg_kw["degree_n"] = args.degree_n
    if args.seed is not None:
        cfg_kw["seed"] = args.seed
    if args.hamiltonian_scale is not None:
        cfg_kw["hamiltonian_scale"] = args.hamiltonian_scale
    cfg = PIKANConfig(**cfg_kw)
    train(cfg)
