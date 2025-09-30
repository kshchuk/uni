"""Utilities for running numerical experiments with multiple start points."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .gradient_descent import OptimizationResult, gradient_descent
from .line_search import LineSearch, goldstein_rule, simple_rule

Vector = np.ndarray


@dataclass(slots=True)
class ExperimentConfig:
    name: str
    start: Vector
    line_search: LineSearch
    line_search_name: str
    tol: float = 1e-6
    max_iters: int = 500


@dataclass(slots=True)
class ExperimentOutcome:
    config: ExperimentConfig
    result: OptimizationResult

    @property
    def minimiser(self) -> Vector:
        return self.result.minimiser

    @property
    def iterations(self) -> int:
        return self.result.iterations

    @property
    def converged(self) -> bool:
        return all(self.result.history.line_success)


DEFAULT_STARTS: Sequence[Vector] = (
    np.array([1.0, 1.0, 1.0]),
    np.array([-10.0, 10.0, 1.0]),
    np.array([0.5, -0.75, 0.3]),
)


def build_default_suite() -> list[ExperimentConfig]:
    cfgs: list[ExperimentConfig] = []
    for idx, start in enumerate(DEFAULT_STARTS, start=1):
        cfgs.append(
            ExperimentConfig(
                name=f"simple_{idx}",
                start=start,
                line_search=simple_rule(t0=1.0, beta=0.5, max_iter=50),
                line_search_name="Simple decrease",
            )
        )
        cfgs.append(
            ExperimentConfig(
                name=f"goldstein_{idx}",
                start=start,
                line_search=goldstein_rule(t0=1.0, beta=0.5, c=0.2, max_iter=80),
                line_search_name="Goldstein",
            )
        )
    return cfgs


def run_experiment(config: ExperimentConfig) -> ExperimentOutcome:
    result = gradient_descent(
        x0=config.start,
        line_search=config.line_search,
        tol=config.tol,
        max_iters=config.max_iters,
    )
    return ExperimentOutcome(config=config, result=result)


def run_suite(configs: Iterable[ExperimentConfig] | None = None) -> list[ExperimentOutcome]:
    if configs is None:
        configs = build_default_suite()
    return [run_experiment(cfg) for cfg in configs]


def table(outcomes: Sequence[ExperimentOutcome]) -> str:
    lines = [
        "name,start,method,iters,step_success,value,minimiser",
    ]
    for outcome in outcomes:
        cfg = outcome.config
        hist = outcome.result.history
        success = all(hist.line_success)
        minimiser = ",".join(f"{coord:.6e}" for coord in outcome.minimiser)
        start_str = ",".join(f"{coord:.3f}" for coord in cfg.start)
        line = (
            f"{cfg.name},{start_str},{cfg.line_search_name},{outcome.iterations},"
            f"{success},{outcome.result.value:.12f},{minimiser}"
        )
        lines.append(line)
    return "\n".join(lines)


__all__ = [
    "ExperimentConfig",
    "ExperimentOutcome",
    "DEFAULT_STARTS",
    "build_default_suite",
    "run_experiment",
    "run_suite",
    "table",
]


if __name__ == "__main__":  # pragma: no cover
    print(table(run_suite()))
