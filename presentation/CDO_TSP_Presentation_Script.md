# Presentation Script: CDO Tourist Driving Tour Using PSO

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
* **Visual:** Objective equation $Z(\pi) = \sum D[\pi[k], \pi[k+1]]$, key constraints.
* **Speaker Script:**
  “Our objective is to minimize total driving distance in kilometres:
  $$Z(\pi) = D[\pi[0], \pi[1]] + D[\pi[1], \pi[2]] + \dots + D[\pi[7], \pi[0]]$$
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
  Summing the 8 legs from our distance matrix gives a total cost of $38.50\text{ km}$.
  Now, suppose the global best target $gbest$ is $[V_0, V_3, V_4, V_7, V_6, V_5, V_2, V_1]$.
  During social alignment, the algorithm scans from left to right:
  - Index 1 matches: both have $V_3$.
  - At index 2, $X[2] = V_1$, but the target requires $V_4$.
  - In our particle $X$, $V_4$ is located at index 4.
  - With probability $c_2 = 0.8$, the algorithm executes swap $(2, 4)$.
  - The new route becomes: $[V_0, V_3, V_4, V_2, V_1, V_5, V_6, V_7]$.
  Recalculating the altered legs: $V_3 \to V_4$, $V_4 \to V_2$, $V_2 \to V_1$, and $V_1 \to V_5$, the new tour cost drops to $38.30\text{ km}$. Because this cost is lower, the particle immediately updates its personal best!”

---

### Component 3: Graph Model, Data, and Methodology (Suggested: 2–3 minutes)

#### Slide 6 — Graph Model & Weight Matrix (5:30–7:00)
* **Visual:** `results/figure1_cdo_graph_network.png` (2-panel labeled topological graph and asymmetric matrix heatmap).
* **Speaker Script:**
  “Here on Slide 6 is our complete Graph Model and Distance Matrix.
  On the left, we represent the problem as a complete directed weighted graph $G = (V, A, D)$ with 8 vertices and 56 directed arcs. The bold teal arrows show the closed Hamiltonian cycle discovered by PSO, complete with leg distances.
  On the right is our 8-by-8 asymmetric weight matrix. Notice that travel costs are asymmetric. For example:
  - Driving from Plaza Divisoria ($V_0$) to Gaston Park ($V_1$) is $0.63\text{ km}$.
  - But returning from Gaston Park ($V_1$) to Plaza Divisoria ($V_0$) is only $0.36\text{ km}$.
  This asymmetry is caused by real-world one-way streets around downtown CDO. Symmetrizing the matrix would produce unrealistic routes, so we preserve the full directed structure.”

#### Slide 7 — Data Sources and Reproducibility (7:00–7:45)
* **Visual:** Data pipeline flowchart (Overpass API + OSRM Table + Route requests $\to$ CSVs).
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
  - **PSO Tour Order:** $V_0 \to V_3 \to V_4 \to V_7 \to V_6 \to V_5 \to V_2 \to V_1 \to V_0$.
  - **Total PSO Distance:** **36.4739 kilometres** (or 36,473.9 metres).
  - **Exact Matrix Optimum:** To test whether our PSO result is exact or approximate, we evaluated all 5,040 permutations by brute force. The absolute matrix minimum is **35.9537 kilometres**.
  - **Optimality Assessment:** The optimality gap is **1.4469%** (520.2 metres). Therefore, we honestly report that our seed-123 PSO solution is an **approximate solution**, not the exact mathematical optimum.
  - Across 30 repeated random seeds, PSO matched the exact optimum 4 times, with a mean distance of 36.63 km.”

* **Visual: Recalculate from edge weights:**
  Show the 8 individual leg distances from `tour_legs.csv`:
  | 1 | V0 | V3 | 0.3565 |
| 2 | V3 | V4 | 1.3014 |
| 3 | V4 | V7 | 8.7112 |
| 4 | V7 | V6 | 13.5305 |
| 5 | V6 | V5 | 7.3656 |
| 6 | V5 | V2 | 4.6876 |
| 7 | V2 | V1 | 0.1585 |
| 8 | V1 | V0 | 0.3626 |
  “Recalculating the individual edge weights directly from the matrix confirms the exact total of 36.4739 kilometres, verifying that our closed tour visits each destination exactly once and returns to V0.”

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
  - Our discrete swap PSO algorithm rapidly discovered an approximate tour of 36.4739 km within 120 iterations, just 1.45% above the exact global optimum.
  - Limitations: The model assumes static driving routes without real-time congestion and does not account for attraction opening hours or parking search times.
  References: LakbayPinas for destination ideas, OpenStreetMap and OSRM for geographic data, and Luna-Garcia et al. (2024) for the discrete PSO adaptation.
  Thank you very much!”
