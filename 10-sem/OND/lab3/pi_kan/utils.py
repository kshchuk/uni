from __future__ import annotations

import os
import random
from dataclasses import asdict

import numpy as np
import torch


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def resolve_device(use_mps_if_available: bool = False) -> torch.device:
    if use_mps_if_available and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def to_config_dict(config: object) -> dict:
    if hasattr(config, "__dataclass_fields__"):
        return asdict(config)
    return dict(config)
