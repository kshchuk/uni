# PI-KAN for Center-Focus (N >= 7)

This module implements a Physics-Informed KAN in PyTorch to learn a candidate
Lyapunov function / first integral `Phi(x,y)` for planar polynomial systems:

For the default experiment, the test system is Hamiltonian:

`H(x,y) = 0.5*(x^2+y^2) + H_nonlin(x,y)`, `dx/dt = -dH/dy`, `dy/dt = dH/dx`.

## Highlights

- Custom KAN (`lab3/pi_kan/model.py`) with:
  - default polynomial edge basis (`chebyshev` / `legendre`) for SymPy-friendly extraction,
  - optional smooth `rbf` basis.
- Physics-informed loss (`lab3/pi_kan/train.py`):
  - `L_pde = mean((grad(Phi) · v)^2)`,
  - `L_anchor = mean((Phi - (x^2+y^2))^2)` near origin,
  - `L_origin = ||grad Phi(0,0)||^2 + ||H(Phi)(0,0)-2I||_F^2`.
- Symbolic extraction (`lab3/pi_kan/symbolic_extract.py`):
  - direct symbolic route for polynomial bases,
  - Taylor-series route for non-polynomial basis (`rbf`),
  - `vector_field_P_Q_bautin_form` maps the Hamiltonian field to $\dot x=-y+P$, $\dot y=x+Q$ for comparison with the Bautin/Lyapunov notebook convention.

## Files

- `config.py` - configuration dataclass.
- `system_def.py` - Hamiltonian-center test system + collocation/anchor sampling.
- `model.py` - custom PI-KAN architecture and optional `PyKANAdapter`.
- `train.py` - training loop (`Adam -> LBFGS`) + logs/checkpoint.
- `symbolic_extract.py` - symbolic export/pruning.
- `../pi_kan_experiment.ipynb` - end-to-end demo notebook.

## Installation

From workspace root:

```bash
pip install -r lab3/pi_kan/requirements.txt
```

## Run Training

From workspace root:

```bash
python -m lab3.pi_kan.train
# Optional overrides (must match notebook if you compare SymPy vs checkpoint):
python -m lab3.pi_kan.train --degree-n 6 --seed 42 --hamiltonian-scale 0.1
```

The random Hamiltonian demo is fixed by `PIKANConfig.degree_n`, `seed`, and `hamiltonian_scale` (passed through to `make_test_system`). Use the same triple anywhere you rebuild the system for cross-checks (e.g. `bautin_ideal.ipynb`).

Outputs are saved into `lab3/pi_kan/outputs/`:

- `best_model.pt`
- `train_logs.json`
- `run_config.json`

## Notebook Demo

Open and run:

- `lab3/pi_kan_experiment.ipynb`

It performs:

1. training,
2. residual validation (`mean/max |Lie|`),
3. symbolic extraction (`phi_symbolic.txt`, `phi_symbolic.tex`),
4. `Phi` vs generated `H` comparison metrics.

## MacBook Air M4 Notes

- Default mode is GPU/ANE-first (`device="mps"`, `use_mps_if_available=True`).
- If higher-order autograd ops are unsupported on MPS at runtime, training
  automatically falls back to CPU.
- If you see memory pressure:
  - reduce `collocation_points`,
  - reduce `basis_order`,
  - reduce `hidden_dim` / `depth`.

## Quick API Example

```python
from lab3.pi_kan.config import PIKANConfig
from lab3.pi_kan.train import train
from lab3.pi_kan.symbolic_extract import extract_symbolic_polynomial

cfg = PIKANConfig(degree_n=6, basis_type="chebyshev", device="mps", use_mps_if_available=True)
result = train(cfg)
phi_sym = extract_symbolic_polynomial(result["model"], cfg)
print(phi_sym)
```
