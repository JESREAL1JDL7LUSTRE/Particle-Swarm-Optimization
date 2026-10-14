# Cagayan de Oro tourist TSP using discrete PSO

An eight-stop **driving-tour** problem using destinations from the [LakbayPinas guide](https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/). Start and finish at Plaza Divisoria. Minimize the sum of saved OSRM recommended car-route lengths.

**Verified saved result:** seed-123 PSO **36.4739 km**; exact brute force **35.9537 km**; gap **1.4469%**. PSO is an approximate solution for the stored matrix. Across seeds 0–29, 4/30 runs match the exact matrix optimum.

## Destinations

V0: Plaza Divisoria; V1: Gaston Park; V2: St. Augustine Metropolitan Cathedral; V3: Museo de Oro; V4: Vicente de Lara Park; V5: High Ridge; V6: Amaya View; V7: Gardens of Malasag Eco-Tourism Village.

## Run offline

Python 3.10+ is recommended. The solver and tests use the standard library; plotting uses Matplotlib. Source downloading additionally uses certifi when available.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_dataset.py
python3 cdo_tsp_pso_solver.py
python3 -m unittest discover -s tests -v
```

Run the solver with `--no-plots` for numerical results only. Paths default to the repository rather than the terminal's working directory. `--output-dir /tmp/cdo-run` writes an isolated experiment. `--seed` and `--runs` control the demonstration and repeated runs. Open `cdo_tsp_pso_notebook.ipynb` for the same shared workflow; its outputs go under `results/notebook_run/`.

For notebook execution, install `requirements-notebook.txt`, then run `python3 scripts/verify_notebook.py`. This executes every cell in a Jupyter kernel, compares numerical results with the canonical command-line run, and saves the executed notebook.

## Data and interpretation

- `cdo_tsp_dataset.csv`: 64 ordered distance/duration entries, one header. **This file is loaded by the solver.** Distance is in metres; duration is retained for reference only.
- `cdo_tsp_locations.csv`: eight locations, Google Maps links, OSM source URLs, coordinates and access assumptions.
- `data/attractions.json`: selected source objects and designated routing-request points.
- `data/raw/`: saved public OSM/OSRM responses and their acquisition manifest.
- `data/routes.geojson`: all 56 directed road geometries.
- `data/README.md`: full source, access and routing protocol.

The matrix is asymmetric. OSRM table lengths follow its recommended/fastest car routes, not necessarily shortest-distance road paths. Exactness applies to this saved matrix. This is not a live-traffic model, verified parking/entrance guide, or feasible one-day schedule. On-site walking, sightseeing, opening hours and fees are excluded.

Distances retain provider precision, not survey accuracy. All raw routes are checked against table values and segment sums. The normal workflow needs no API key or internet. A new source snapshot is an explicit operation: `python3 scripts/fetch_sources.py --output /tmp/cdo-new-sources`.

## Implementation and outputs

The focus of this project is the **discrete swap PSO** assigned algorithm. Exact brute force is included as an optimality verification anchor, and nearest neighbor as an optional baseline. The PSO adaptation uses valid probabilities, sequential alignment, retained velocity and explicit exploratory swaps.

`results/summary.json`, `convergence.csv`, `repeated_runs.csv`, and `tour_legs.csv` contain measured outputs. Three PNGs show the directed cost matrix, convergence, and road-route geometry. Read [the report](CDO_TSP_PSO_Report.md) and [presentation script](CDO_TSP_Presentation_Script.md) for the problem, methods, results and caveats.

After deliberately updating inputs, rerun the experiment and then `python3 scripts/update_documents.py` to refresh the report, README and script from current results. For new cost data, map geometry must also match; otherwise use `--no-plots`. Old results are not automatically evidence for edited CSVs.

The original delivery project is preserved in `archive/delivery-example-c44f835.zip` (original commit c44f835), with its original claims intact for historical reference.

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0. Routing: OSRM.
