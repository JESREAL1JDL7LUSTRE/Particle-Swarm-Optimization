"""Execute every notebook cell in a real kernel and save the executed notebook.

Install requirements-notebook.txt first. Kernel selection follows your Jupyter
environment. Numerical results must agree with the canonical command-line run;
timings are intentionally excluded from the comparison.
"""
import json
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "cdo_tsp_pso_notebook.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    NotebookClient(notebook, timeout=180, kernel_name="python3",
                   resources={"metadata": {"path": str(ROOT)}}).execute()
    canonical = json.loads((ROOT / "results/summary.json").read_text())
    actual = json.loads((ROOT / "results/notebook_run/summary.json").read_text())
    for key in canonical:
        if key not in {"pso_seconds", "brute_force_seconds", "python_version"}:
            if actual[key] != canonical[key]:
                raise AssertionError(f"Notebook/CLI mismatch: {key}")
    for name in ("convergence.csv", "tour_legs.csv", "repeated_runs.csv"):
        if (ROOT / "results" / name).read_bytes() != (ROOT / "results/notebook_run" / name).read_bytes():
            raise AssertionError(f"Notebook/CLI mismatch: {name}")
    cells = [c for c in notebook.cells if c.cell_type == "code"]
    if any(c.execution_count is None or any(o.output_type == "error" for o in c.outputs) for c in cells):
        raise AssertionError("Notebook contains an unexecuted or failed code cell")
    nbformat.write(notebook, path)
    print(f"Executed {len(cells)} code cells; all numerical outputs match the CLI")


if __name__ == "__main__":
    main()
