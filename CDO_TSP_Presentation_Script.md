# Presentation script: CDO tourist driving tour using PSO

Target: 10–15 minutes including a live demonstration. The ten segments below allocate 12 minutes. These are speaker notes and visual instructions, not a rendered slide deck. Rehearse the pacing and include time for pointing at the matrix and route.

## Slide 1 — Problem and motivation (0:00–1:00)

**Show:** title, Cagayan de Oro location, start/end point.

“Our problem is planning the visiting order for a group of tourists travelling together by car in Cagayan de Oro. They begin at Plaza Divisoria, visit seven other selected attractions, and return to their starting point. We minimize the combined driving distance between stops. This is a Traveling Salesperson Problem because every selected destination must be scheduled once in a closed tour.”

Explain that the route is a mathematical distance model; it is not a promise that every activity fits into a single day.

## Slide 2 — Selected destinations and source (1:00–2:15)

**Show:** the eight-location table from the report and the LakbayPinas source link.

“We selected eight destinations from the LakbayPinas guide. Our set combines heritage sites, parks and hilltop attractions. We use only locations within Cagayan de Oro, as required by the assignment. The article supplies our attraction selection, while OpenStreetMap and OSRM supply the geographic data and driving-route costs.”

Read and locate: V0: Plaza Divisoria; V1: Gaston Park; V2: St. Augustine Metropolitan Cathedral; V3: Museo de Oro; V4: Vicente de Lara Park; V5: High Ridge; V6: Amaya View; V7: Gardens of Malasag Eco-Tourism Village.

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

| Method | Tour length (km) | Evidence |
|---|---:|---|
| Brute force | 35.9537 | All 5,040 depot-fixed orders evaluated |
| Nearest neighbor | 38.4993 | Deterministic greedy baseline from V0 |
| Discrete PSO, seed 123 | 36.4739 | 40 particles, 120 updates; 1.4469% gap |

“In the saved seed-123 run, PSO returns 36.4739 kilometres. Brute force proves that 35.9537 kilometres is the minimum of this matrix. The PSO gap is 1.4469 percent, or 520.2 metres. Thus this PSO result is an approximate solution for the stored matrix.”

Point to the program's actual output rather than promising a particular machine runtime.

## Slide 8 — Convergence and repeated seeds (8:30–9:30)

**Show:** `results/figure2_pso_convergence.png` and the repeated-run count.

“The curve tracks the best observed distance, which cannot increase because we keep historical bests. It does not say that all particles become identical. This demonstration run did not reach the exact optimum within 120 updates. A flat curve can mean that a heuristic is no longer improving; it is not proof of optimality.”

“Across seeds 0 through 29, 4 of 30 runs match the exact optimum. The mean is 36.6298 kilometres. This measures random-seed variation on one instance, not performance on all tourist routes.”

## Slide 9 — Route interpretation and audit (9:30–11:00)

**Show:** `results/figure3_cdo_tour.png` and the eight-leg table.

“The demonstrated PSO order is V0 → V3 → V4 → V7 → V6 → V5 → V2 → V1 → V0. These lines follow saved road geometry. The downtown detail panel separates closely spaced stops.”

| Leg | From | To | Distance (km) |
|---|---|---|---:|
| 1 | V0 | V3 | 0.3565 |
| 2 | V3 | V4 | 1.3014 |
| 3 | V4 | V7 | 8.7112 |
| 4 | V7 | V6 | 13.5305 |
| 5 | V6 | V5 | 7.3656 |
| 6 | V5 | V2 | 4.6876 |
| 7 | V2 | V1 | 0.1585 |
| 8 | V1 | V0 | 0.3626 |

“Adding these eight legs gives 36.4739 kilometres. Every required stop appears once, and the final leg returns to V0. Road segments may repeat. Driving past an attraction does not count as its scheduled visit. Because costs are directed, the reverse tour can have a different length.”

For comparison, the exact benchmark order is **V0 → V3 → V1 → V2 → V5 → V6 → V7 → V4 → V0**. Label it as brute force, not as a PSO discovery unless that run actually found it.

## Slide 10 — Limitations and conclusion (11:00–12:00)

**Show:** data sources, model limits, and final comparison.

“We turned selected CDO tourist destinations into a reproducible directed TSP. The solver loads public-map-derived costs, PSO searches for an efficient order, and exhaustive enumeration checks how good that order is. Our reported PSO result is 36.4739 kilometres against the exact matrix optimum of 35.9537 kilometres.”

“The main limits are the fixed routing snapshot, assumed site access, and omitted opening hours, sightseeing time, parking and live traffic. Larger instances and time-window constraints are future work. A practical trip needs those checks before travel.”

Credit LakbayPinas for destination selection, OpenStreetMap contributors for geographic data (ODbL), OSRM for routing, and Luna-Garcia, Candano and Caga-anan (2024) for the assigned PSO reference. Full links and the adaptation details are in the report.
