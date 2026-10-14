# Sources and routing protocol

## Attraction selection

Eight locations were selected from [LakbayPinas, 19 Must-Visit Cagayan de Oro Tourist Spots](https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/), dated March 7, 2025. The user selected an eight-location CDO-only driving tour. The article is the attraction-selection source, not a distance dataset. We retain section identifiers in `attractions.json` and the locations CSV; its descriptions, fees and opening-hour claims are not copied into the model.

The set combines four central heritage stops, another city park, two hilltop attractions, and an eastern recreation site. It is a selected scenario, not all destinations in the article and not an algorithmic selection of the best eight attractions. Dahilayan and Divine Mercy Shrine are outside CDO. Rafting needs a specified operator/assembly point before it can become one TSP node. Other CDO attractions were left out to keep a tractable eight-node assignment.

## Public mapping sources

- Attraction identity and coordinates: OpenStreetMap objects, fetched through the [Overpass API](https://overpass-api.de/). Exact object IDs and public URLs are saved.
- Directed pairwise costs: [OSRM public car-routing service](https://router.project-osrm.org/), table endpoint with `annotations=distance,duration` and no straight-line fallback.
- Road geometry: a separate route request for each of the 56 ordered pairs, reusing the table's endpoint hints. Segment-distance annotations permit a separate sum check.
- [OSRM API documentation](https://project-osrm.org/docs/v5.24.0/api/) states that table distances are lengths of fastest routes, not necessarily shortest-distance paths. This project's TSP minimizes the sum of those supplied route lengths. Durations are retained for provenance, not optimized and not presented as live traffic.

`raw/manifest.json` records each full request URL, actual UTC retrieval time and SHA-256 checksum. `raw/osm_attractions.json` records its OSM base timestamp. OSRM's graph date is reported in `dataset_audit.json` when available; it must not be inferred from the separate Overpass snapshot. New network downloads can change results. Committed snapshots support offline reproduction.

## Attraction coordinate versus routing point

An OSM area centre is a locator, not a verified entrance. `attractions.json` records the request coordinates; `cdo_tsp_locations.csv` separately records the POI coordinates, requested coordinates, snapped car-network coordinates, snapping distance and access assumption. The optimization starts and ends at those car-network points.

For the cathedral and Museo de Oro, designated public-road nodes on Gaston Circle and Corrales Avenue replace the POI centre. Their exact geometry is retained in `evidence/access_roads.json` and its query file. This avoids treating interior museum/cathedral coordinates as vehicle destinations. Other stops use the provider's nearby road point, capped at 100 metres from the request coordinate. These are **modeled access points, not certified parking spaces or verified entrances**. Museum permission, venue access, parking, walking inside attractions, closures and current opening hours require local confirmation before real travel.

Independent location corroboration:

- [City Tourism heritage-tour account](https://cagayandeoro.gov.ph/index.php/item/1989-heritage-and-cultural-tour-gipasiugdahan-sa-city-tourism-office.html): Divisoria, Gaston Park, cathedral and Museo de Oro.
- [High Ridge official location](https://highridgecdo.com/location/): Macasandig, CDO.
- [TIEZA Gardens of Malasag information](https://tieza.gov.ph/wp-content/uploads/2019/01/Gardens-of-Malasag.pdf): attraction identity; this older brochure is not used for current operating hours.
- [Provincial government on Vicente de Lara Park](https://www.misamisoriental.gov.ph/massage-therapy-available-na-sa-capitol-park/): park at the provincial capitol.
- Amaya View's saved OSM record identifies Indahag, Cagayan de Oro City; see its public object link in the locations CSV.

## Build and validation

Run `python scripts/build_dataset.py` from the repository. No network is needed. It checks raw hashes, request order, complete/finite matrices, zero diagonals, positive distinct-pair distances, route/table agreement (0.11 m rounding tolerance), endpoint agreement (1 m), and segment sums (1 m). It writes two ordinary CSV tables, `routes.geojson`, and `dataset_audit.json`. Those tolerances validate consistency of the provider outputs, not real-world measurement accuracy.

Distances retain OSRM's 0.1-metre output precision; this does **not** imply survey accuracy. The solver converts them to integer decimetres, so exact comparisons and tour sums have no floating-point rounding ambiguity. The matrix stays asymmetric. Reversing a tour may change its cost.

To acquire a new snapshot, run `python scripts/fetch_sources.py --output /tmp/cdo-new-sources`. Use `--resume` only for an interrupted snapshot; existing request URLs and hashes are checked. Review map identities and access assumptions before replacing `raw/`. A refresh is explicit and never performed by the solver or notebook.

## Attribution

© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright). OSM-derived source data and derived geographic/distance data are provided under the [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Routing calculations use OSRM. The travel article remains the property of its publisher; only the citation and destination selection are retained here.
