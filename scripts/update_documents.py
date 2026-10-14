"""Regenerate the report and presentation notes from the saved measured run.

Run after the solver, then review prose and figures. This command does not run
experiments or fetch data; it refuses to describe results for different inputs.
"""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cdo_tsp_pso_solver import fingerprint, load_dataset


def update():
    s = json.loads((ROOT / "results/summary.json").read_text())
    if s["input_sha256"] != fingerprint(ROOT):
        raise ValueError("Results are stale for the current CSVs; rerun the solver")
    if s["parameters"] != {"num_particles": 40, "max_iterations": 120, "w": .5,
                            "c1": .8, "c2": .8, "mutation": .2, "seed": 123}:
        raise ValueError("Document template describes the canonical default experiment")
    audit = json.loads((ROOT / "data/dataset_audit.json").read_text())
    locations, matrix = load_dataset(ROOT)
    with (ROOT / "results/tour_legs.csv").open() as f:
        legs = list(csv.DictReader(f))
    pso = f"{s['pso_distance_m']/1000:.4f}"
    exact = f"{s['exact_distance_m']/1000:.4f}"
    nn = f"{s['nearest_neighbor_distance_m']/1000:.4f}"
    gap = f"{s['optimality_gap_percent']:.4f}"
    extra = f"{s['pso_distance_m']-s['exact_distance_m']:.1f}"
    route = " → ".join(f"V{i}" for i in s["pso_tour"] + [0])
    exact_route = " → ".join(f"V{i}" for i in s["exact_tour"] + [0])
    repeats = s["repeated_runs"]
    status = "matches the proven optimum of the stored matrix" if s["matches_exact"] else "is an approximate solution for the stored matrix"
    convergence = (f"The first exact match occurred after {s['first_optimum_iteration']} completed updates."
                   if s["first_optimum_iteration"] is not None else "This demonstration run did not reach the exact optimum within 120 updates.")
    location_rows = "\n".join(f"| {p['Node_ID']} | {p['Location_Name']} | {p['Role']} | {p['Route_Latitude']:.7f} | {p['Route_Longitude']:.7f} |" for p in locations)
    matrix_rows = "\n".join(f"| V{i} | " + " | ".join(f"{v/10000:.4f}" for v in row) + " |" for i, row in enumerate(matrix))
    leg_rows = "\n".join(f"| {r['leg']} | {r['from_node']} | {r['to_node']} | {float(r['distance_m'])/1000:.4f} |" for r in legs)
    names = "; ".join(f"{p['Node_ID']}: {p['Location_Name']}" for p in locations)
    table = f"""| Method | Tour length (km) | Evidence |
|---|---:|---|
| Brute force | {exact} | All 5,040 depot-fixed orders evaluated |
| Nearest neighbor | {nn} | Deterministic greedy baseline from V0 |
| Discrete PSO, seed 123 | {pso} | 40 particles, 120 updates; {gap}% gap |"""

    report = f"""# Optimizing a Cagayan de Oro Tourist Driving Tour Using Particle Swarm Optimization

**Course:** Graph Theory
**Application:** Eight selected tourist destinations within Cagayan de Oro City
**Objective:** Minimize total inter-stop driving distance in a closed tour
**Result:** PSO {pso} km; exact matrix optimum {exact} km; gap {gap}%.
**Scope:** Static map-derived car-route costs. This is not a verified daily travel schedule.

## 1. Problem and objective

A group of tourists hires one vehicle to visit eight selected attractions in Cagayan de Oro. The group meets at Plaza Divisoria, visits each of the seven other selected destinations, and returns to the starting point. A driver needs an efficient visiting order that reduces the combined driving distance between stops.

The destinations are selected from the [LakbayPinas travel guide](https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/), published March 7, 2025. This project uses eight CDO destinations from that article, not all places in its title. Selection was fixed before optimization; PSO chooses the order, not which attractions are worth visiting. The article supplies destination ideas, not our road-distance values.

The area spans the downtown heritage cluster, the provincial-capitol area, Macasandig, Indahag, and the Malasag/Cugman area. The hilltop stops motivate a driving model. Dahilayan and Divine Mercy Shrine are excluded because they lie outside CDO. Rafting is not represented as a single location without a specified operator/meeting point.

### Starting location and required locations

V0 is the modeled meeting/return point on the car network beside Plaza Divisoria. V1–V7 are mandatory stops. Coordinates below are the **routing points**, not automatically the attraction centres or official entrances.

| Node | Tourist destination | Role | Route latitude | Route longitude |
|---|---|---|---:|---:|
{location_rows}

The full location table, source-object URLs, attraction coordinates, request coordinates, snapping distances and access assumptions are in `cdo_tsp_locations.csv`. Museo de Oro uses a road point on Corrales Avenue outside the campus. The cathedral uses a point on Gaston Circle. Their mapped road-node evidence is saved. Other sites use nearby points selected by the car-routing service; these are not verified parking spaces.

### Assumptions and constraints

1. One group uses one vehicle; capacity and refuelling do not constrain the visiting order.
2. Start and finish at V0. Schedule one visit to each other stop, with no omitted or duplicate stop.
3. Every inter-stop leg uses the saved OSRM recommended driving route. Costs remain fixed during optimization.
4. Direction matters: the distance from A to B can differ from B to A. The matrix is not symmetrized.
5. The model assumes visitor access can be arranged. It does not enforce opening hours, permits, reservations or time windows, and makes no claim that all activities fit into one day.
6. Parking searches, walking within attractions, sightseeing durations, admission fees, fuel prices and live traffic are outside the distance objective.
7. Connecting roads may repeat or pass near a stop before its scheduled visit. Visiting each destination once does not forbid reusing streets.
8. Access points are map-derived and have not been field-verified. Practical access must be checked before real travel.

### Quantity minimized

Let D[i,j] be the stored length of the recommended car route from stop i to stop j. For a permutation π of all eight nodes with π[0] = 0:

`minimize Z(π) = D[π[0],π[1]] + … + D[π[6],π[7]] + D[π[7],π[0]]`.

Z is reported in kilometres. This optimizes distance, not duration or transportation cost. OSRM chooses its recommended/fastest road route for each pair; its returned distance is not necessarily the shortest possible road distance. Therefore optimality is defined relative to the **stored matrix**, not every possible physical driving path.

## 2. Public data and reproducibility

Attraction identities and coordinates come from OpenStreetMap. Pairwise distances and road polylines come from OSRM's public driving service. Raw responses and full request URLs are retained in `data/raw/`, along with UTC retrieval times and SHA-256 hashes. No Google Maps measurements or invented road distances are used for this tourist dataset.

The source acquisition spans **{audit['acquired_from_utc']}** to **{audit['acquired_to_utc']}**. The Overpass response reports OSM base time **{audit['osm_base_timestamp']}**. OSRM graph version: **{audit['osrm_data_version']}**. These timestamps describe separate services and must not be treated as one identical map build.

The offline builder verifies the raw checksums, eight selected objects, all 64 matrix entries, and all 56 separately requested non-diagonal routes. Route/table lengths agree within {audit['max_route_table_difference_m']:.2f} m. It also checks road-segment sums and geometry endpoints. These are consistency checks, not a ground survey or proof of current site access.

The largest snap from request coordinate to routing point is {audit['max_snap_distance_m']:.3f} m. The source table retains tenths of metres because that is the provider's output precision; real-world positional/distance accuracy is lower and unmeasured here. Integer decimetres are used internally solely to make tour sums and exact comparisons unambiguous.

See [data/README.md](data/README.md) for access-point decisions, independent location corroboration, limitations and refresh instructions. © OpenStreetMap contributors; OSM-derived geographic and distance data are distributed under ODbL 1.0.

## 3. Graph model

The TSP is a complete directed weighted graph G = (V,A,D), with 8 vertices and 8 × 7 = **56 directed arcs**. Each arc represents one entire road journey between two modeled stops. Intermediate intersections belong to the underlying road network, not to the eight TSP vertices. Self-distances are zero and do not count as arcs.

| From / To (km) | V0 | V1 | V2 | V3 | V4 | V5 | V6 | V7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{matrix_rows}

![Directed travel-cost matrix](results/figure1_cdo_graph_network.png)

## 4. Assigned algorithm: discrete Particle Swarm Optimization

PSO keeps a population of candidate solutions. Here a particle is a visiting order beginning at V0. Its personal best is its lowest-cost historical order; the swarm's global best is the lowest-cost order found by any particle. A velocity is a sequence of swaps between non-depot positions, which preserves the permutation constraint.

This implementation is an explicit swap-based adaptation inspired by the PSO topic in Section 2.4 of Luna-Garcia et al. (2024). It is **not a verbatim reproduction of Appendix 4.4**. The changes and their probabilities are described below so the code and claims agree.

### Update procedure

1. Initialize 40 random depot-fixed permutations, evaluate them, and save personal/global bests. Record this as iteration 0.
2. For each update, freeze a copy of the global best as the shared target for that generation.
3. Independently retain and apply each swap from the previous velocity with probability w = 0.5.
4. Scan non-depot positions toward the personal best. When a position differs, accept an aligning swap with probability c1 = 0.8. Update the working permutation and its city-to-index map immediately.
5. Repeat sequential alignment toward the frozen global best with probability c2 = 0.8.
6. With probability 0.2, apply one random swap of two non-depot positions for exploration. Retain at most the latest 2n actual swaps as the next velocity.
7. Evaluate the updated position and improve personal best if its cost decreased. After all particles, update the global best and record its cost.
8. Stop after 120 updates and return the best observed tour. There is no early stopping or exact-solver information injected into PSO.

c1 and c2 are probabilities in [0,1], not continuous-PSO acceleration constants. Invalid values such as 1.5 are rejected. Computing and applying alignment swaps sequentially avoids stale-index cancellation. A local random generator makes seeds repeatable without changing Python's global random state. Every final updated population is evaluated.

### Complexity and limitations

For n locations, P particles and T updates, the bounded velocity and maintained index map give expected **O(Pn + TPn)** time and **O(Pn)** swarm memory, in addition to the O(n²) input matrix. If P and T are both chosen proportional to n, this implementation's expected time becomes O(n³). That is a conditional scaling statement, not a universal PSO bound or a proof of fast exact optimization.

PSO has no general optimality guarantee and may stagnate. The exact solver checks (n−1)! orders and computes n edges per order: O(n × (n−1)!) time. For this eight-node problem that is 5,040 tours. The PSO demonstration evaluates 40 × 121 = 4,840 candidates, including possible repeats. This small example does not establish a speed or scalability advantage.

## 5. Implemented comparisons and measured results

The repository implements discrete PSO, exact brute force, and nearest neighbor. There is no genetic algorithm. The notebook imports the same functions and CSVs as the command-line script.

{table}

The seeded PSO tour **{status}**. Its gap is **{gap}%**, or **{extra} metres** above the exact result. {convergence} Initial swarm best: **{s['initial_best_m']/1000:.4f} km**.

- PSO order: **{route}**.
- Exact benchmark order: **{exact_route}**.
- Seeded PSO compute time: {s['pso_seconds']:.6f} s.
- Brute-force compute time: {s['brute_force_seconds']:.6f} s.

Times are one local run under Python {s['python_version']}; they exclude downloads, plots and repeated-seed experiments and will vary by machine/run. Raw outcomes and input hashes are recorded in `results/summary.json`.

### Repeated seeds

Across seeds {repeats['seed_range'][0]}–{repeats['seed_range'][1]}, **{repeats['optimal_count']} of {repeats['count']}** runs matched the exact matrix optimum. Mean distance: **{repeats['mean_distance_m']/1000:.4f} km**; range: **{repeats['min_distance_m']/1000:.4f}–{repeats['max_distance_m']/1000:.4f} km**. All runs use the same parameters and matrix. This measures seed variation for one selected instance, not performance across cities or larger graphs. The demonstration seed 123 is separate from these 30 runs.

![Seeded PSO convergence](results/figure2_pso_convergence.png)

## 6. Closed-tour verification

| Leg | From | To | Distance (km) |
|---|---|---|---:|
{leg_rows}
| Total | | | **{pso}** |

The implementation checks that every node occurs exactly once, V0 is first, and the implicit final leg returns to V0. The audited leg sum equals the reported PSO cost. Reversing the order is not assumed equivalent because the input is asymmetric.

![PSO tour on saved road geometry](results/figure3_cdo_tour.png)

The road plot uses the saved geometry for each actual directed leg. It does not draw straight-line edges and label them as road routes. Its title uses the PSO cost and a conditional optimality statement. The route order can be used to discuss tourist-stop sequencing; it does not establish parking legality, entrance access or a feasible schedule of visits.

## 7. Verification and reproducible commands

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_dataset.py
python3 cdo_tsp_pso_solver.py
python3 scripts/update_documents.py
python3 -m unittest discover -s tests -v
```

Source-to-CSV reconstruction must reproduce identical files. Tests also cover directed return-leg costs, independent exact enumeration, valid sequential swaps, final-update evaluation, valid tours, reproducible seeds, invalid parameters, missing/duplicate CSV pairs, and loaded CSV changes. The notebook performs a temporary data rebuild before executing the shared experiment.

The original delivery dataset, solver, report, notebook and images remain in `archive/delivery-example-c44f835.zip`. They describe a separate historical scenario and are not evidence for these tourist results.

## 8. References

1. LakbayPinas (2025). [19 Must-Visit Cagayan de Oro Tourist Spots](https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/). Destination-selection source only.
2. [OpenStreetMap contributors](https://www.openstreetmap.org/copyright). Public geographic database; exact object references in the locations CSV.
3. [OSRM API documentation](https://project-osrm.org/docs/v5.24.0/api/). Driving table and route semantics; raw responses retained locally.
4. Luna-Garcia, R., Candano, T. M. C., and Caga-anan, R. L. (2024). [Performance Analysis of Classical Algorithms for the Traveling Salesman Problem](https://doi.org/10.62071/tmjm.v6i2.716). The Mindanawan Journal of Mathematics, 6(2), 79–111. Assigned PSO reference; implementation adaptations are stated in Section 4.
"""
    (ROOT / "CDO_TSP_PSO_Report.md").write_text(report)

    readme = f"""# Cagayan de Oro tourist TSP using discrete PSO

An eight-stop **driving-tour** problem using destinations from the [LakbayPinas guide](https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/). Start and finish at Plaza Divisoria. Minimize the sum of saved OSRM recommended car-route lengths.

**Verified saved result:** seed-123 PSO **{pso} km**; exact brute force **{exact} km**; gap **{gap}%**. PSO {status}. Across seeds 0–29, {repeats['optimal_count']}/{repeats['count']} runs match the exact matrix optimum.

## Destinations

{names}.

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
- `cdo_tsp_locations.csv`: eight locations, OSM source URLs, coordinates and access assumptions.
- `data/attractions.json`: selected source objects and designated routing-request points.
- `data/raw/`: saved public OSM/OSRM responses and their acquisition manifest.
- `data/routes.geojson`: all 56 directed road geometries.
- `data/README.md`: full source, access and routing protocol.

The matrix is asymmetric. OSRM table lengths follow its recommended/fastest car routes, not necessarily shortest-distance road paths. Exactness applies to this saved matrix. This is not a live-traffic model, verified parking/entrance guide, or feasible one-day schedule. On-site walking, sightseeing, opening hours and fees are excluded.

Distances retain provider precision, not survey accuracy. All raw routes are checked against table values and segment sums. The normal workflow needs no API key or internet. A new source snapshot is an explicit operation: `python3 scripts/fetch_sources.py --output /tmp/cdo-new-sources`.

## Implementation and outputs

Implemented comparisons: **discrete swap PSO, brute force, nearest neighbor**. The PSO adaptation uses valid probabilities, sequential alignment, retained velocity and explicit exploratory swaps. No genetic algorithm is claimed.

`results/summary.json`, `convergence.csv`, `repeated_runs.csv`, and `tour_legs.csv` contain measured outputs. Three PNGs show the directed cost matrix, convergence, and road-route geometry. Read [the report](CDO_TSP_PSO_Report.md) and [presentation script](CDO_TSP_Presentation_Script.md) for the problem, methods, results and caveats.

After deliberately updating inputs, rerun the experiment and then `python3 scripts/update_documents.py` to refresh the report, README and script from current results. For new cost data, map geometry must also match; otherwise use `--no-plots`. Old results are not automatically evidence for edited CSVs.

The original delivery project is preserved in `archive/delivery-example-c44f835.zip` (original commit c44f835), with its original claims intact for historical reference.

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0. Routing: OSRM.
"""
    (ROOT / "README.md").write_text(readme)

    script = f"""# Presentation script: CDO tourist driving tour using PSO

Target: 10–15 minutes including a live demonstration. The ten segments below allocate 12 minutes. These are speaker notes and visual instructions, not a rendered slide deck. Rehearse the pacing and include time for pointing at the matrix and route.

## Slide 1 — Problem and motivation (0:00–1:00)

**Show:** title, Cagayan de Oro location, start/end point.

“Our problem is planning the visiting order for a group of tourists travelling together by car in Cagayan de Oro. They begin at Plaza Divisoria, visit seven other selected attractions, and return to their starting point. We minimize the combined driving distance between stops. This is a Traveling Salesperson Problem because every selected destination must be scheduled once in a closed tour.”

Explain that the route is a mathematical distance model; it is not a promise that every activity fits into a single day.

## Slide 2 — Selected destinations and source (1:00–2:15)

**Show:** the eight-location table from the report and the LakbayPinas source link.

“We selected eight destinations from the LakbayPinas guide. Our set combines heritage sites, parks and hilltop attractions. We use only locations within Cagayan de Oro, as required by the assignment. The article supplies our attraction selection, while OpenStreetMap and OSRM supply the geographic data and driving-route costs.”

Read and locate: {names}.

“We do not include every place mentioned in the article. Dahilayan and Divine Mercy Shrine are outside CDO. Rafting would require a specific meeting point. The selected set is fixed before PSO begins.”

## Slide 3 — Assumptions and objective (2:15–3:15)

**Show:** the closed-tour sum and a short assumptions list.

“Our objective adds the distance of each consecutive leg, including the return to V0. We optimize distance in kilometres, not travel time or cost. One vehicle carries the group. Every selected stop is mandatory. Costs remain fixed, while opening hours, permits, sightseeing, parking and walking inside attractions are outside the optimization.”

“Our route endpoints are mapped car-network points. At Museo de Oro we use Corrales Avenue outside the campus, and at the cathedral we use Gaston Circle. These points are not certified parking spaces. Actual visitor access still needs confirmation.”

## Slide 4 — Directed graph and public dataset (3:15–4:30)

**Show:** `results/figure1_cdo_graph_network.png`.

“The model has eight vertices and 56 directed arcs. An arc represents a whole driving route, not just one street segment. Notice that opposite-direction costs can differ. We retain that asymmetry instead of averaging it away.”

Point to V0→V1 and V1→V0 in the matrix and compare their values.

“The saved source data contains all 64 entries, including zero diagonal entries, plus separately requested geometry for all 56 journeys. We check that route lengths, road-segment sums and matrix costs agree. These checks establish source consistency, not survey accuracy.”

“OSRM reports lengths of its recommended or fastest driving routes. Those legs are not necessarily the shortest-distance roads. Our exactness claims apply to the resulting fixed matrix.”

## Slide 5 — How a PSO particle represents a route (4:30–5:30)

**Show:** a permutation beginning with V0; pbest and gbest labels.

“Each particle is one possible visiting order. Its fitness is the total closed-tour distance. It remembers its best previous order, called the personal best. The swarm shares its best discovered order, called the global best. A swap exchanges two non-starting positions without losing or duplicating a destination.”

Demonstrate a swap of two stops and explain why V0 stays fixed. Mention that the implementation is a documented discrete adaptation of the assigned PSO topic, not a verbatim copy of the paper's appendix.

## Slide 6 — Updates, parameters and complexity (5:30–6:45)

**Show:** retain old swaps → personal alignment → global alignment → exploration → evaluate.

“We use 40 particles and 120 updates. Previous swaps are retained with probability 0.5. Personal and global alignment each use probability 0.8. A separate exploratory swap occurs with probability 0.2. Each alignment swap updates the working route immediately, so later swaps use current positions. We evaluate the final update too.”

“Iteration zero is the initial random population. We do not give PSO the exact answer. With bounded swap lists and an index map, the expected work is proportional to iterations times particles times locations. A cubic bound follows only if the particle and iteration budgets both scale linearly with location count.”

“PSO remains a heuristic. Polynomial execution with a fixed search budget does not guarantee the optimal answer.”

## Slide 7 — Live execution and measured comparison (6:45–8:30)

**Show:** terminal, then the results table. Run from the repository:

```bash
python3 cdo_tsp_pso_solver.py --output-dir /tmp/cdo-presentation-run
```

“The solver reads the two CSV files, checks the data, evaluates all 5,040 depot-fixed orders by brute force, and runs PSO. A nearest-neighbor baseline chooses the cheapest next unvisited stop.”

{table}

“In the saved seed-123 run, PSO returns {pso} kilometres. Brute force proves that {exact} kilometres is the minimum of this matrix. The PSO gap is {gap} percent, or {extra} metres. Thus this PSO result {status}.”

Point to the program's actual output rather than promising a particular machine runtime.

## Slide 8 — Convergence and repeated seeds (8:30–9:30)

**Show:** `results/figure2_pso_convergence.png` and the repeated-run count.

“The curve tracks the best observed distance, which cannot increase because we keep historical bests. It does not say that all particles become identical. {convergence} A flat curve can mean that a heuristic is no longer improving; it is not proof of optimality.”

“Across seeds 0 through 29, {repeats['optimal_count']} of {repeats['count']} runs match the exact optimum. The mean is {repeats['mean_distance_m']/1000:.4f} kilometres. This measures random-seed variation on one instance, not performance on all tourist routes.”

## Slide 9 — Route interpretation and audit (9:30–11:00)

**Show:** `results/figure3_cdo_tour.png` and the eight-leg table.

“The demonstrated PSO order is {route}. These lines follow saved road geometry. The downtown detail panel separates closely spaced stops.”

{leg_rows}

“Adding these eight legs gives {pso} kilometres. Every required stop appears once, and the final leg returns to V0. Road segments may repeat. Driving past an attraction does not count as its scheduled visit. Because costs are directed, the reverse tour can have a different length.”

For comparison, the exact benchmark order is **{exact_route}**. Label it as brute force, not as a PSO discovery unless that run actually found it.

## Slide 10 — Limitations and conclusion (11:00–12:00)

**Show:** data sources, model limits, and final comparison.

“We turned selected CDO tourist destinations into a reproducible directed TSP. The solver loads public-map-derived costs, PSO searches for an efficient order, and exhaustive enumeration checks how good that order is. Our reported PSO result is {pso} kilometres against the exact matrix optimum of {exact} kilometres.”

“The main limits are the fixed routing snapshot, assumed site access, and omitted opening hours, sightseeing time, parking and live traffic. Larger instances and time-window constraints are future work. A practical trip needs those checks before travel.”

Credit LakbayPinas for destination selection, OpenStreetMap contributors for geographic data (ODbL), OSRM for routing, and Luna-Garcia, Candano and Caga-anan (2024) for the assigned PSO reference. Full links and the adaptation details are in the report.
"""
    script = script.replace("\n" + leg_rows + "\n", "\n| Leg | From | To | Distance (km) |\n|---|---|---|---:|\n" + leg_rows + "\n")
    (ROOT / "CDO_TSP_Presentation_Script.md").write_text(script)
    print("Updated report, README and presentation notes from current results")


if __name__ == "__main__":
    update()
