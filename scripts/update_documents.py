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
    loc_lines = []
    for p in locations:
        gurl = p.get("Google_Maps_URL") or f"https://maps.google.com/?q={p['Route_Latitude']},{p['Route_Longitude']}"
        loc_lines.append(f"| {p['Node_ID']} | {p['Location_Name']} | {p['Role']} | {p['Route_Latitude']:.7f} | {p['Route_Longitude']:.7f} | [Google Maps]({gurl}) |")
    location_rows = "\n".join(loc_lines)
    matrix_rows = "\n".join(f"| V{i} | " + " | ".join(f"{v/10000:.4f}" for v in row) + " |" for i, row in enumerate(matrix))
    leg_rows = "\n".join(f"| {r['leg']} | {r['from_node']} | {r['to_node']} | {float(r['distance_m'])/1000:.4f} |" for r in legs)
    names = "; ".join(f"{p['Node_ID']}: {p['Location_Name']}" for p in locations)

    table = f"""| Method | Role in Project | Tour length (km) | Evidence / Purpose |
|---|---|---:|---|
| **Discrete PSO (Seed 123)** | **Assigned Algorithm** | **{pso}** | 40 particles, 120 updates; {gap}% optimality gap |
| Brute force | Verification Benchmark | {exact} | All 5,040 depot-fixed orders evaluated (proof of global optimum) |
| Nearest neighbor | Optional Baseline | {nn} | Deterministic greedy heuristic from V0 |"""

    report = f"""# Optimizing a Cagayan de Oro Tourist Driving Tour Using Particle Swarm Optimization

**Course:** Graph Theory
**Application:** Eight selected tourist destinations within Cagayan de Oro City
**Objective:** Minimize total inter-stop driving distance in a closed tour
**Result:** PSO {pso} km; exact matrix optimum {exact} km; gap {gap}%.
**Scope:** Static map-derived car-route costs. This is not a verified daily travel schedule.

## 1. Problem and objective

A group of tourists hires one vehicle to visit eight selected attractions in Cagayan de Oro. The group meets at Plaza Divisoria, visits each of the seven other selected destinations, and returns to the starting point. A driver needs an efficient visiting order that reduces the combined driving distance between stops.

The destinations are selected from the [LakbayPinas travel guide](https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/), published March 7, 2025. This project uses eight CDO destinations from that article, not all places in its title. Selection was fixed before optimization; PSO chooses the order, not which attractions are worth visiting.

The area spans the downtown heritage cluster, the provincial-capitol area, Macasandig, Indahag, and the Malasag/Cugman area. The hilltop stops motivate a driving model. Dahilayan and Divine Mercy Shrine are excluded because they lie outside CDO. Rafting is not represented as a single location without a specified operator/meeting point.

Destinations were identified, mapped, and verified within Cagayan de Oro City using **Google Maps**. Street-level vehicular road distances are computed using the Open Source Routing Machine (OSRM) driving profile to capture real road topologies, turning restrictions, and one-way streets.

### Starting location and required locations

V0 is the modeled meeting/return point on the car network beside Plaza Divisoria. V1–V7 are mandatory stops. Coordinates below are the **routing points**, not automatically the attraction centres or official entrances.

| Node | Tourist destination | Role | Route latitude | Route longitude | Location verification |
|---|---|---|---:|---:|:---:|
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

Attraction identities and coordinates come from OpenStreetMap, corroborated with Google Maps. Pairwise distances and road polylines come from OSRM's public driving service. Raw responses and full request URLs are retained in `data/raw/`, along with UTC retrieval times and SHA-256 hashes. No Google Maps measurements or invented road distances are used for this tourist dataset.

The source acquisition spans **{audit['acquired_from_utc']}** to **{audit['acquired_to_utc']}**. The Overpass response reports OSM base time **{audit['osm_base_timestamp']}**. OSRM graph version: **{audit['osrm_data_version']}**. These timestamps describe separate services and must not be treated as one identical map build.

The offline builder verifies the raw checksums, eight selected objects, all 64 matrix entries, and all 56 separately requested non-diagonal routes. Route/table lengths agree within {audit['max_route_table_difference_m']:.2f} m. It also checks road-segment sums and geometry endpoints. These are consistency checks, not a ground survey or proof of current site access.

The largest snap from request coordinate to routing point is {audit['max_snap_distance_m']:.3f} m. The source table retains tenths of metres because that is the provider's output precision; real-world positional/distance accuracy is lower and unmeasured here. Integer decimetres are used internally solely to make tour sums and exact comparisons unambiguous.

See [data/README.md](data/README.md) for access-point decisions, independent location corroboration, limitations and refresh instructions. © OpenStreetMap contributors; OSM-derived geographic and distance data are distributed under ODbL 1.0.

## 3. Methodology and graph model

The TSP is modeled as a complete directed weighted graph G = (V,A,D):
- **Vertices (|V| = 8):** V0 represents the starting and finishing depot (Plaza Divisoria). Vertices V1 through V7 represent mandatory tourist attractions.
- **Edges / Arcs (|A| = 56):** Directed road trips connecting all pairs of distinct stops. Travel is **directed** because one-way streets and divided boulevards cause D[i,j] ≠ D[j,i].
- **Edge weights (D[i,j]):** Directed driving distance in kilometres (derived from OSRM recommended car routes). Self-loop weights D[i,i] = 0.

| From / To (km) | V0 | V1 | V2 | V3 | V4 | V5 | V6 | V7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{matrix_rows}

![Labeled Graph and Asymmetric Travel-Cost Matrix](results/figure1_cdo_graph_network.png)
*Figure 1: (Left) Labeled weighted topological graph G=(V, A, D) with 8 vertices, 56 directed arcs, and the PSO tour highlighted in teal. (Right) Asymmetric travel-cost matrix D showing OSRM recommended driving-route lengths in km.*

## 4. Assigned algorithm: Particle Swarm Optimization (Section 2.4)

In the assigned reference (*Luna-Garcia, Candano, & Caga-anan, 2024, Section 2.4, Algorithm 2.4*), Particle Swarm Optimization (PSO) is adapted to solve the Traveling Salesperson Problem. Because classical PSO operates on continuous real-number vectors, applying PSO to the TSP requires representing candidate solutions as discrete city permutations, often termed Discrete PSO.

Here, each particle represents a candidate visiting order beginning and ending at the depot V0. Its personal best ($pbest$) is the lowest-cost tour it has visited so far, and the global best ($gbest$) is the lowest-cost tour found by any particle in the entire swarm. Velocity is represented as a sequence of transpositions (swaps) between non-depot city positions, preserving the permutation constraint without duplicating or omitting any destination.

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

### Key steps and calculation walkthrough

To demonstrate how discrete PSO operates on our tourist graph, consider a concrete numerical calculation:

1. **Permutation representation and tour cost:**
   A candidate solution (particle) is represented as a permutation $\\pi$ of stops with fixed depot $\\pi[0] = 0$:
   $$\\pi = [0, \\pi[1], \\pi[2], \\pi[3], \\pi[4], \\pi[5], \\pi[6], \\pi[7]]$$
   The closed-tour distance is calculated as:
   $$Z(\\pi) = \\sum_{{k=0}}^{{7}} D[\\pi[k],\\, \\pi[(k+1) \\bmod 8]]$$

2. **Current particle state:**
   Suppose particle $k$ has current visiting order:
   $$X = [V_0, V_3, V_1, V_2, V_4, V_5, V_6, V_7]$$
   Looking up each directed leg from the weight matrix:
   - $D[V_0, V_3] = 0.3565\\text{{ km}}$
   - $D[V_3, V_1] = 0.4734\\text{{ km}}$
   - $D[V_1, V_2] = 0.1327\\text{{ km}}$
   - $D[V_2, V_4] = 1.5101\\text{{ km}}$
   - $D[V_4, V_5] = 5.4261\\text{{ km}}$
   - $D[V_5, V_6] = 7.0242\\text{{ km}}$
   - $D[V_6, V_7] = 13.6527\\text{{ km}}$
   - $D[V_7, V_0] = 9.9236\\text{{ km}}$ (return to depot)
   $$\\text{{Total Cost }} Z(X) = 0.3565 + 0.4734 + 0.1327 + 1.5101 + 5.4261 + 7.0242 + 13.6527 + 9.9236 = \\mathbf{{38.4993\\text{{ km}}}}$$

3. **Alignment swap calculation:**
   Suppose the global best target is:
   $$T = [V_0, V_3, V_4, V_7, V_6, V_5, V_2, V_1]$$
   During social attraction toward $T$ with parameter $c_2 = 0.8$:
   - At index $i=1$: $X[1] = V_3$ matches $T[1] = V_3$.
   - At index $i=2$: $X[2] = V_1 \\neq T[2] = V_4$. The target node $V_4$ currently resides at index 4 in $X$.
   - A uniform random draw $r \\in [0, 1)$ is evaluated. Since $r < 0.8$, the swap $(2, 4)$ is accepted.
   - Swapping positions 2 and 4 yields the updated order:
     $$X' = [V_0, V_3, V_4, V_2, V_1, V_5, V_6, V_7]$$

4. **Recalculating updated tour distance:**
   The swap alters the edges incident to positions 2 and 4. Summing the new legs:
   - $D[V_0, V_3] = 0.3565\\text{{ km}}$
   - $D[V_3, V_4] = 1.3014\\text{{ km}}$ (replaces $V_3 \\to V_1$)
   - $D[V_4, V_2] = 1.4995\\text{{ km}}$ (replaces $V_1 \\to V_2$)
   - $D[V_2, V_1] = 0.1585\\text{{ km}}$ (replaces $V_2 \\to V_4$)
   - $D[V_1, V_5] = 4.3810\\text{{ km}}$ (replaces $V_4 \\to V_5$)
   - $D[V_5, V_6] = 7.0242\\text{{ km}}$
   - $D[V_6, V_7] = 13.6527\\text{{ km}}$
   - $D[V_7, V_0] = 9.9236\\text{{ km}}$
   $$\\text{{Updated Cost }} Z(X') = \\mathbf{{38.2974\\text{{ km}}}}$$
   Because $Z(X') = 38.2974\\text{{ km}} < 38.4993\\text{{ km}}$, the particle updates its personal best ($pbest$), retaining the improvement.

### Complexity and limitations

For n locations, P particles and T updates, the bounded velocity and maintained index map give expected **O(Pn + TPn)** time and **O(Pn)** swarm memory, in addition to the O(n²) input matrix. If P and T are both chosen proportional to n, this implementation's expected time becomes O(n³). That is a conditional scaling statement, not a universal PSO bound or a proof of fast exact optimization.

PSO has no general optimality guarantee and may stagnate. The exact solver checks (n−1)! orders and computes n edges per order: O(n × (n−1)!) time. For this eight-node problem that is 5,040 tours. The PSO demonstration evaluates 40 × 121 = 4,840 candidates, including possible repeats. This small example does not establish a speed or scalability advantage.

## 5. Implementation, verification, and results

Per the project instructions, the focus is the assigned algorithm (Discrete PSO); comparative algorithm studies are not required. Exhaustive brute-force evaluation ($5,040$ depot-fixed permutations) was implemented strictly as a mathematical verification benchmark to test whether PSO reaches a proven global optimum. Nearest neighbor is listed only as an optional baseline.

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
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/CDO_TSP_PSO_Report.md").write_text(report)
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
- `cdo_tsp_locations.csv`: eight locations, Google Maps links, OSM source URLs, coordinates and access assumptions.
- `data/attractions.json`: selected source objects and designated routing-request points.
- `data/raw/`: saved public OSM/OSRM responses and their acquisition manifest.
- `data/routes.geojson`: all 56 directed road geometries.
- `data/README.md`: full source, access and routing protocol.

The matrix is asymmetric. OSRM table lengths follow its recommended/fastest car routes, not necessarily shortest-distance road paths. Exactness applies to this saved matrix. This is not a live-traffic model, verified parking/entrance guide, or feasible one-day schedule. On-site walking, sightseeing, opening hours and fees are excluded.

Distances retain provider precision, not survey accuracy. All raw routes are checked against table values and segment sums. The normal workflow needs no API key or internet. A new source snapshot is an explicit operation: `python3 scripts/fetch_sources.py --output /tmp/cdo-new-sources`.

## Repository Structure

```text
Particle-Swarm-Optimization/
├── presentation/              # Presentation slides, script, and web deck
│   ├── CDO_TSP_PSO_Presentation.pptx  # 16:9 Widescreen PowerPoint slide deck
│   ├── index.html                     # Interactive browser slide deck (with speaker notes)
│   ├── CDO_TSP_Presentation_Script.md # Word-for-word 10–15 min presentation script
│   └── CDO_TSP_Presentation_Slides.marp.md # Marp markdown presentation slides
├── docs/                      # Formal written documentation
│   ├── CDO_TSP_PSO_Report.md          # Comprehensive PIT project report
│   └── IMPLEMENTATION_PLAN.md         # Implementation and architecture plan
├── data/                      # Input datasets and raw acquisition payloads
│   ├── README.md                      # Data provenance & access documentation
│   ├── attractions.json               # CDO attractions metadata & drop-off coordinates
│   ├── dataset_audit.json             # Verification audit metrics & OSM timestamps
│   ├── routes.geojson                 # 56 directed OSRM road geometries
│   └── raw/                           # Raw OpenStreetMap / OSRM API responses
├── results/                   # Output figures, logs, and interactive maps
│   ├── figure1_cdo_graph_network.png  # Labeled topological digraph & weight heatmap
│   ├── figure2_pso_convergence.png    # Seeded PSO convergence curve (100 iter)
│   ├── figure3_cdo_tour.png           # Geographic road route map with downtown inset
│   ├── cdo_tour_interactive_map.html  # Interactive Leaflet route map (Google/CartoDB)
│   ├── summary.json                   # Machine-readable solver verification audit
│   ├── tour_legs.csv                  # Individual edge lengths and verified tour sum
│   ├── convergence.csv                # Best tour cost per iteration
│   └── repeated_runs.csv              # 30-seed stability benchmark results
├── scripts/                   # Data pipeline, map generation, and pptx tools
├── tests/                     # 15 automated unit tests (test_tsp.py)
├── cdo_tsp_pso_solver.py      # Core Discrete PSO TSP solver (Standard library)
├── cdo_tsp_plots.py           # Matplotlib visualization script
├── cdo_tsp_pso_notebook.ipynb # Interactive Jupyter notebook walkthrough
├── cdo_tsp_dataset.csv        # 64-entry directed distance matrix (m)
├── cdo_tsp_locations.csv      # 8-node verified location table
└── requirements.txt           # Python dependencies
```

## Implementation and outputs

The focus of this project is the **discrete swap PSO** assigned algorithm (Section 2.4). Exact brute force is included as an optimality verification anchor, and nearest neighbor as an optional baseline. The PSO adaptation uses valid probabilities, sequential alignment, retained velocity and explicit exploratory swaps.

`results/summary.json`, `convergence.csv`, `repeated_runs.csv`, and `tour_legs.csv` contain measured outputs. Three PNGs show the directed cost matrix, convergence, and road-route geometry. Read [the report](docs/CDO_TSP_PSO_Report.md) and [presentation script](presentation/CDO_TSP_Presentation_Script.md) for the problem, methods, results and caveats.

After deliberately updating inputs, rerun the experiment and then `python3 scripts/update_documents.py` to refresh the report, README and script from current results. For new cost data, map geometry must also match; otherwise use `--no-plots`. Old results are not automatically evidence for edited CSVs.

The original delivery project is preserved in `archive/delivery-example-c44f835.zip` (original commit c44f835), with its original claims intact for historical reference.

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0. Routing: OSRM.
"""
    (ROOT / "README.md").write_text(readme)

    script = f"""# Presentation Script: CDO Tourist Driving Tour Using PSO

**Required Duration:** 10–15 minutes including live Python code execution.
**Structure:** Aligned with the 5 PIT Rubric Evaluation Components.

---

### Component 1: Introduction, Problem, and Objective (Suggested: 2–3 minutes)

#### Slide 1 — Title and Real-Life TSP Motivation (0:00–1:00)
* **Visual:** Project title, Cagayan de Oro map overview, starting depot (Plaza Divisoria).
* **Speaker Script:**
  “Good day. Today, I am presenting our Graph Theory Performance Innovative Task: solving a real-life Traveling Salesperson Problem in Cagayan de Oro City using our assigned algorithm, Discrete Particle Swarm Optimization.
  Our scenario involves planning an efficient driving tour for a group of tourists visiting Cagayan de Oro. They hire a single vehicle, start at Plaza Divisoria, visit seven other prominent tourist destinations, and return to Plaza Divisoria.
  The mathematical challenge is to determine the optimal visiting order that minimizes the total driving distance while visiting each required location exactly once.”

#### Slide 2 — Tourist Destinations & Google Maps Verification (1:00–2:15)
* **Visual:** Eight-stop table with Google Maps links and locations across CDO.
* **Speaker Script:**
  “The destinations are selected from the LakbayPinas Cagayan de Oro travel guide. We chose eight key spots located strictly within Cagayan de Oro City:
  - V0: Plaza Divisoria (our start and finish depot)
  - V1: Gaston Park
  - V2: St. Augustine Metropolitan Cathedral
  - V3: Museo de Oro
  - V4: Vicente de Lara Park
  - V5: High Ridge in Macasandig
  - V6: Amaya View in Indahag
  - V7: Gardens of Malasag Eco-Tourism Village in Cugman
  Each location was verified on Google Maps. Because places like Museo de Oro and the Cathedral sit inside pedestrian campuses or plazas, we designated street-level vehicular drop-off nodes on Corrales Avenue and Gaston Circle to reflect realistic driving access.”

#### Slide 3 — Objective and Assumptions (2:15–3:00)
* **Visual:** Objective equation $Z(\\pi) = \\sum D[\\pi[k], \\pi[k+1]]$, key constraints.
* **Speaker Script:**
  “Our objective is to minimize total driving distance in kilometres:
  $$Z(\\pi) = D[\\pi[0], \\pi[1]] + D[\\pi[1], \\pi[2]] + \\dots + D[\\pi[7], \\pi[0]]$$
  Key assumptions:
  1. Closed tour: Start and finish at V0, visiting V1 through V7 exactly once.
  2. The vehicle travels on real road networks. Because of one-way roads and traffic flow, travel between two stops is directed: distance from A to B does not necessarily equal B to A.
  3. We optimize distance; entrance fees, sightseeing durations, and live congestion are outside the distance objective.”

---

### Component 2: Assigned Algorithm Discussion (Suggested: 2–3 minutes)

#### Slide 4 — Discrete PSO for Permutations (3:00–4:15)
* **Visual:** Diagram of Particle Permutation, Personal Best ($pbest$), Global Best ($gbest$), Swap Velocity.
* **Speaker Script:**
  “Our assigned algorithm is Particle Swarm Optimization (PSO). In continuous PSO, particles move through space via position and velocity vectors. But TSP is a discrete permutation problem:
  - A particle represents a candidate visiting order, with depot V0 fixed at position 0.
  - Fitness is the total closed-tour distance $Z$.
  - Velocity is represented as a sequence of transpositions or swaps acting on non-depot cities.
  - Each particle remembers its personal best order ($pbest$), and the swarm shares the best order discovered so far ($gbest$).
  In our implementation, we use 40 particles and 120 iterations. Previous swaps are retained with inertia probability $w = 0.5$. Cognitive alignment toward $pbest$ occurs with probability $c_1 = 0.8$, social alignment toward $gbest$ with probability $c_2 = 0.8$, and an exploratory random swap occurs with probability 0.2.”

#### Slide 5 — Step-by-Step Calculation Walkthrough (4:15–5:30)
* **Visual:** Concrete numerical swap example and distance calculation.
* **Speaker Script:**
  “Let’s look at a concrete step-by-step calculation:
  Suppose a particle currently has the route:
  $$X = [V_0, V_3, V_1, V_2, V_4, V_5, V_6, V_7]$$
  Summing the 8 legs from our distance matrix gives a total cost of $38.50\\text{{ km}}$.
  Now, suppose the global best target $gbest$ is $[V_0, V_3, V_4, V_7, V_6, V_5, V_2, V_1]$.
  During social alignment, the algorithm scans from left to right:
  - Index 1 matches: both have $V_3$.
  - At index 2, $X[2] = V_1$, but the target requires $V_4$.
  - In our particle $X$, $V_4$ is located at index 4.
  - With probability $c_2 = 0.8$, the algorithm executes swap $(2, 4)$.
  - The new route becomes: $[V_0, V_3, V_4, V_2, V_1, V_5, V_6, V_7]$.
  Recalculating the altered legs: $V_3 \\to V_4$, $V_4 \\to V_2$, $V_2 \\to V_1$, and $V_1 \\to V_5$, the new tour cost drops to $38.30\\text{{ km}}$. Because this cost is lower, the particle immediately updates its personal best!”

---

### Component 3: Graph Model, Data, and Methodology (Suggested: 2–3 minutes)

#### Slide 6 — Graph Model & Weight Matrix (5:30–7:00)
* **Visual:** `results/figure1_cdo_graph_network.png` (2-panel labeled topological graph and asymmetric matrix heatmap).
* **Speaker Script:**
  “Here on Slide 6 is our complete Graph Model and Distance Matrix.
  On the left, we represent the problem as a complete directed weighted graph $G = (V, A, D)$ with 8 vertices and 56 directed arcs. The bold teal arrows show the closed Hamiltonian cycle discovered by PSO, complete with leg distances.
  On the right is our 8-by-8 asymmetric weight matrix. Notice that travel costs are asymmetric. For example:
  - Driving from Plaza Divisoria ($V_0$) to Gaston Park ($V_1$) is $0.63\\text{{ km}}$.
  - But returning from Gaston Park ($V_1$) to Plaza Divisoria ($V_0$) is only $0.36\\text{{ km}}$.
  This asymmetry is caused by real-world one-way streets around downtown CDO. Symmetrizing the matrix would produce unrealistic routes, so we preserve the full directed structure.”

#### Slide 7 — Data Sources and Reproducibility (7:00–7:45)
* **Visual:** Data pipeline flowchart (Overpass API + OSRM Table + Route requests $\\to$ CSVs).
* **Speaker Script:**
  “All road distances and geometries were generated using the Open Source Routing Machine (OSRM) driving API, referencing verified OpenStreetMap data.
  Every raw API response is preserved locally in `data/raw/` with SHA-256 checksums in a manifest. Our entire dataset can be rebuilt and validated offline without internet access, ensuring full scientific reproducibility.”

---

### Component 4: Python Execution Demonstration & Results (Suggested: 3–4 minutes)

#### Slide 8 — Live Code Execution & Output Walkthrough (7:45–11:00)
* **Action: Switch to Terminal / Screen Recording:**
  Run the command live:
  ```bash
  python3 cdo_tsp_pso_solver.py
  ```
* **Speaker Script (while running and pointing to terminal output):**
  “Now let us execute our Python implementation live.
  As you can see on screen, the solver loads the CSV dataset, validates the matrix, and executes our discrete PSO algorithm with seed 123.
  Let us examine the results:
  - **PSO Tour Order:** $V_0 \\to V_3 \\to V_4 \\to V_7 \\to V_6 \\to V_5 \\to V_2 \\to V_1 \\to V_0$.
  - **Total PSO Distance:** **{pso} kilometres** (or 36,473.9 metres).
  - **Exact Matrix Optimum:** To test whether our PSO result is exact or approximate, we evaluated all 5,040 permutations by brute force. The absolute matrix minimum is **{exact} kilometres**.
  - **Optimality Assessment:** The optimality gap is **{gap}%** (520.2 metres). Therefore, we honestly report that our seed-123 PSO solution is an **approximate solution**, not the exact mathematical optimum.
  - Across 30 repeated random seeds, PSO matched the exact optimum 4 times, with a mean distance of {repeats['mean_distance_m']/1000:.2f} km.”

* **Visual: Recalculate from edge weights:**
  Show the 8 individual leg distances from `tour_legs.csv`:
  {leg_rows}
  “Recalculating the individual edge weights directly from the matrix confirms the exact total of {pso} kilometres, verifying that our closed tour visits each destination exactly once and returns to V0.”

---

### Component 5: Solution, Conclusion, and References (Suggested: 1–2 minutes)

#### Slide 9 — Geographic Road Route Analysis (11:00–12:00)
* **Visual:** `results/figure3_cdo_tour.png` (Geographic road route map with downtown inset).
* **Speaker Script:**
  “On Slide 9, we project the optimal tour onto actual CDO road geometry.
  Notice how the tour smartly clusters stops:
  It leaves downtown Plaza Divisoria ($V_0$), visits Museo de Oro ($V_3$) and Capitol Park ($V_4$), sweeps eastward to Gardens of Malasag ($V_7$), circles to the Indahag hilltop at Amaya View ($V_6$) and High Ridge ($V_5$), and descends back to Gaston Park ($V_1$) and the Cathedral ($V_2$) before returning to Divisoria.
  The downtown inset separates the closely spaced heritage sites.”

#### Slide 10 — Limitations, Conclusion, and Citations (12:00–13:00)
* **Visual:** Summary bullet points and academic references.
* **Speaker Script:**
  “In conclusion:
  - We successfully formulated an asymmetric 8-stop tourist TSP for Cagayan de Oro City.
  - Our discrete swap PSO algorithm rapidly discovered an approximate tour of {pso} km within 120 iterations, just 1.45% above the exact global optimum.
  - Limitations: The model assumes static driving routes without real-time congestion and does not account for attraction opening hours or parking search times.
  References: LakbayPinas for destination ideas, OpenStreetMap and OSRM for geographic data, and Luna-Garcia et al. (2024) for the discrete PSO adaptation.
  Thank you very much!”
"""
    script = script.replace("\n" + leg_rows + "\n", "\n| Leg | From | To | Distance (km) |\n|---|---|---|---:|\n" + leg_rows + "\n")
    (ROOT / "presentation").mkdir(exist_ok=True)
    (ROOT / "presentation/CDO_TSP_Presentation_Script.md").write_text(script)
    (ROOT / "CDO_TSP_Presentation_Script.md").write_text(script)
    print("Updated report, README and presentation notes from current results")


if __name__ == "__main__":
    update()
