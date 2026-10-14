# Tourist TSP implementation and verification

Scope confirmed by user: eight Cagayan de Oro locations selected from the LakbayPinas article, a driving tour, and Plaza Divisoria as start/end.

1. DONE — Preserved the original delivery project in archive/delivery-example-c44f835.zip; every archived file checked against commit c44f835.
2. DONE — Selected eight mapped attractions. Recorded OSM identities and separate routing points, including designated road nodes for the museum and cathedral. Field access and parking remain unverified and are stated assumptions.
3. DONE — Saved 58 raw API responses: attraction objects, one 8x8 directed matrix, and all 56 ordered road routes. Acquisition URLs/times/hashes retained. Every route distance matches the table; segment sums and endpoints checked. CSVs reproduce byte-for-byte offline.
4. DONE — Solver reads CSVs. Added valid swap probabilities, sequential alignment, retained velocity, bounded memory and final-update evaluation. Implemented brute-force and nearest-neighbor comparisons.
5. DONE — Generated measured results, three inspected figures, updated report, README, presentation notes, and shared-code notebook.
6. DONE — All 15 automated tests pass, all five notebook code cells executed in a real Jupyter kernel, and numerical outputs match the CLI. Three rendered figures were visually checked. Local document links resolve. Full evidence is recorded in results/verification.json.

## Measured outcome

- Seed 123 PSO: 36.4739 km; exact matrix optimum: 35.9537 km.
- Gap: 520.2 m (1.4469%). Seed 123 is approximate.
- Seeds 0–29: 4/30 runs reach the exact matrix optimum.
- These are results for a fixed OSRM-derived directed matrix, not a real-world global routing or itinerary-feasibility claim.

## Model boundaries

The tour uses lengths of OSRM recommended car routes. They are not necessarily shortest-distance road paths. Opening hours, activity durations, parking, live traffic, on-site walking, and permissions are excluded. All files explicitly distinguish modeled access points from verified entrances.

Tourism source: https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/
