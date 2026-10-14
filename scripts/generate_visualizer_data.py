#!/usr/bin/env python3
"""
Generate the standalone interactive visualizer presentation/pso_step_by_step_visualizer.html
using .replace() placeholders to avoid any Python f-string bracket escaping conflicts.
"""

import csv
import json
from pathlib import Path

ROOT = Path("/Users/macbookpro/Desktop/CS/4th Yr/Graph Theory/PIT/Particle-Swarm-Optimization")

def main():
    with (ROOT / "cdo_tsp_locations.csv").open(newline="") as f:
        locations = list(csv.DictReader(f))
    for r in locations:
        r["Route_Latitude"] = float(r["Route_Latitude"])
        r["Route_Longitude"] = float(r["Route_Longitude"])

    matrix = [[0.0] * 8 for _ in range(8)]
    matrix_m = [[0.0] * 8 for _ in range(8)]
    with (ROOT / "cdo_tsp_dataset.csv").open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            u = int(r["From_Node"].replace("V", ""))
            v = int(r["To_Node"].replace("V", ""))
            m = float(r["Distance_m"])
            matrix_m[u][v] = m
            matrix[u][v] = round(m / 1000.0, 2)

    with (ROOT / "results/summary.json").open() as f:
        summary = json.load(f)
    pso_tour = summary["pso_tour"]

    routes_file = ROOT / "data/routes.geojson"
    features = json.loads(routes_file.read_text())["features"] if routes_file.exists() else []
    routes_dict = {(f["properties"]["from"], f["properties"]["to"]): f["geometry"]["coordinates"] for f in features}

    tour_legs = []
    n = len(pso_tour)
    for i in range(n):
        u = pso_tour[i]
        v = pso_tour[(i + 1) % n]
        key = (f"V{u}", f"V{v}")
        pts = routes_dict.get(key, [])
        lat_lngs = [[round(pt[1], 6), round(pt[0], 6)] for pt in pts]
        tour_legs.append({
            "leg_index": i + 1,
            "from_node": f"V{u}",
            "to_node": f"V{v}",
            "from_name": locations[u]["Location_Name"],
            "to_name": locations[v]["Location_Name"],
            "from_street": locations[u].get("Road_Name", ""),
            "to_street": locations[v].get("Road_Name", ""),
            "distance_km": matrix[u][v],
            "distance_m": matrix_m[u][v],
            "path": lat_lngs
        })

    # Save data for visualizer
    data_payload = {
        "locations": locations,
        "matrix": matrix,
        "matrix_m": matrix_m,
        "tour_legs": tour_legs,
        "summary": summary
    }

    out_data = ROOT / "presentation/pso_visualizer_data.js"
    out_data.write_text(f"const PSO_DATA = {json.dumps(data_payload)};\n", encoding="utf-8")
    print(f"Generated {out_data} successfully.")

if __name__ == "__main__":
    main()
