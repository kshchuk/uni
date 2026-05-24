# Pattern Recognition — coursework (labs)

Undergraduate **Pattern Recognition** (*Rozpiznavannya obraziv* / image and pattern analysis) practical work from the Faculty of Computer Science and Cybernetics, Taras Shevchenko National University of Kyiv. The exercises use **Python** (Jupyter notebooks, NumPy, Matplotlib; OpenCV where noted; Plotly in some labs) and **LaTeX** reports where provided.

## What the course covers (at a glance)

Classical geometric and statistical ideas for describing point sets and simple decision rules: convex hulls, affine normalization, nested circles/ellipses (Petunin-style constructions), centroid-based metrics ($L_2$, $L_1$), low-dimensional visualization, and projection-based separation in 3D.

## Repository layout

| Directory | Focus |
|-----------|--------|
| `lab1/` | Nested **ellipses** from a 2D point cloud: convex hull, farthest pair, rotation, scaling to a square, nested circles, inverse map, empirical **membership probabilities** for test points. Notebook `lab-1.ipynb`, LaTeX `REPORT.tex`. |
| `lab2/` | Same **nested-ellipse / Petunin** pipeline as lab 1, but training and test points are sampled **inside a fixed polygon** (variant #1). Notebook `lab-2.ipynb`; numeric summary in `lab2_results.txt`. |
| `lab3/` | **Three-class** synthetic data (mixed uniform / Gaussian). Compare **centroid classifiers** under $L_2$ and $L_1$ with **2D and 3D Petunin ellipsoids**; optional separated vs overlapping regimes. Notebook `lab-3.ipynb`, Ukrainian LaTeX report `REPORT.tex`, exported figures under `figures/`, metrics helper `scripts/export_report_metrics.py`. |
| `lab4/` | **Multidimensional classification** in $\mathbb{R}^4$: class representatives by range midpoint vs arithmetic mean; **per-dimension voting** and **weighted $L_1$** distance. Notebook `lab-4.ipynb`, `REPORT.tex`, `scripts/export_report_metrics.py` (reads logic from the notebook). |
| `lab5/` | Three **3D** uniform classes. **Project** data onto candidate lines between class **centroids**; pick the best line using (1) minimum sum of orthogonal distances to the line and (2) maximum spread of 1D projections; then classify in 1D. Notebook `lab-5.ipynb`, `REPORT.tex`. |

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Declared dependencies: `numpy`, `opencv-python`, `plotly` (see `requirements.txt` for minimum versions). A local `.venv` may already exist; it is not required for Git and can stay untracked.

## Building PDF reports

Where a lab ships `REPORT.tex`, compile with `pdflatex` (run twice if the table of contents or cross-references look wrong). Lab 1 includes a `compile.sh` helper.

---

*Student materials; lab numbering follows the course syllabus.*
