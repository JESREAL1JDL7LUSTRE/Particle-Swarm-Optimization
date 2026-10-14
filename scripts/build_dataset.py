"""Rebuild and validate CSVs offline from the saved OSM/OSRM responses."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = "https://lakbaypinas.com/19-must-visit-cagayan-de-oro-tourist-spots-travel/"


def separation_m(a, b):
    """Haversine separation of two [longitude, latitude] points, metres."""
    x1, y1, x2, y2 = map(math.radians, (*a, *b))
    h = math.sin((y2-y1)/2)**2 + math.cos(y1)*math.cos(y2)*math.sin((x2-x1)/2)**2
    return 6371008.8 * 2 * math.asin(min(1, math.sqrt(h)))


def build(output=ROOT, raw=ROOT / "data/raw"):
    output, raw = Path(output), Path(raw)
    manifest = json.loads((raw / "manifest.json").read_text())
    selection = json.loads((ROOT / "data/attractions.json").read_text())
    n = len(selection)
    expected = {"osm_attractions.json", "osrm_table.json"} | {
        f"route_V{i}_V{j}.json" for i in range(n) for j in range(n) if i != j}
    if set(manifest) != expected:
        raise ValueError("Raw manifest must include POIs, table, and every ordered route")
    for name, entry in manifest.items():
        if hashlib.sha256((raw / name).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Raw checksum mismatch: {name}")
    pois = json.loads((raw / "osm_attractions.json").read_text())
    elements = {(e["type"], e["id"]): e for e in pois["elements"]}
    table = json.loads((raw / "osrm_table.json").read_text())
    table_url = manifest["osrm_table.json"]["url"]
    requested = [list(map(float, pair.split(","))) for pair in urlsplit(table_url).path.rsplit("/", 1)[-1].split(";")]
    if requested != [[p["request_lon"], p["request_lat"]] for p in selection]:
        raise ValueError("Selection does not match the saved table request order/coordinates")
    if table.get("code") != "Ok" or table.get("fallback_speed_cells"):
        raise ValueError("Routing table failed or contains straight-line fallback cells")
    if any(len(table[k]) != n for k in ("sources", "destinations", "distances", "durations")):
        raise ValueError("Wrong matrix size")
    evidence = json.loads((ROOT / "data/evidence/access_roads.json").read_text())
    access_nodes = {node: point for way in evidence["elements"]
                    for node, point in zip(way["nodes"], way["geometry"])}
    locations, routes, pairs = [], [], []
    max_route_difference = 0.0
    for i, p in enumerate(selection):
        e = elements[(p["osm_type"], p["osm_id"])]
        coord = e.get("center", e)
        source, destination = table["sources"][i], table["destinations"][i]
        if source["location"] != destination["location"] or source["distance"] > 100:
            raise ValueError(f"Ambiguous or distant routing access: {p['code']}")
        if abs(separation_m(requested[i], source["location"]) - source["distance"]) > 1:
            raise ValueError("Reported snapping distance does not match the requested point")
        if "access_osm_node" in p:
            actual = access_nodes[p["access_osm_node"]]
            if (p["request_lat"], p["request_lon"]) != (actual["lat"], actual["lon"]):
                raise ValueError("Designated access coordinate does not match saved road node")
        elif (p["request_lat"], p["request_lon"]) != (coord["lat"], coord["lon"]):
            raise ValueError("Attraction moved: review new coordinates before rebuilding")
        locations.append({
            "Node_ID": p["code"], "Location_Name": p["name"],
            "Role": "Start/finish" if i == 0 else "Required tourist stop",
            "Latitude": coord["lat"], "Longitude": coord["lon"],
            "Request_Latitude": p["request_lat"], "Request_Longitude": p["request_lon"],
            "Route_Latitude": source["location"][1], "Route_Longitude": source["location"][0],
            "Snap_Distance_m": round(source["distance"], 3),
            "POI_to_Route_m": round(separation_m([coord["lon"], coord["lat"]], source["location"]), 3),
            "Road_Name": source["name"] or "Unnamed mapped access road",
            "OSM_URL": f"https://www.openstreetmap.org/{p['osm_type']}/{p['osm_id']}",
            "Article_Section": p["article_section"], "Attraction_Source": ARTICLE,
            "Access_Note": p["access_note"],
        })
        if len(table["distances"][i]) != n or len(table["durations"][i]) != n:
            raise ValueError("Ragged routing matrix")
        for j in range(n):
            distance, duration = table["distances"][i][j], table["durations"][i][j]
            if any(v is None or not math.isfinite(v) or v < 0 for v in (distance, duration)):
                raise ValueError("Missing, negative, or nonfinite route")
            if (i == j and (distance != 0 or duration != 0)) or (i != j and distance <= 0):
                raise ValueError("Invalid diagonal or distinct-pair cost")
            pairs.append({"From_Node": p["code"], "To_Node": f"V{j}",
                          "Distance_m": f"{distance:.1f}", "Duration_s": f"{duration:.1f}",
                          "Source": "OSRM driving table; data/raw/osrm_table.json"})
            if i == j:
                continue
            response = json.loads((raw / f"route_V{i}_V{j}.json").read_text())
            if response.get("code") != "Ok":
                raise ValueError("Route request failed")
            route = response["routes"][0]
            difference = abs(route["distance"] - distance)
            max_route_difference = max(max_route_difference, difference)
            if difference > 0.11:
                raise ValueError(f"Route/table mismatch V{i}->V{j}: {difference}m")
            points = route["geometry"]["coordinates"]
            if len(points) < 2:
                raise ValueError("Missing road geometry")
            if separation_m(points[0], source["location"]) > 1 or separation_m(points[-1], table["destinations"][j]["location"]) > 1:
                raise ValueError("Route geometry endpoint differs from table")
            segments = route["legs"][0]["annotation"]["distance"]
            if abs(sum(segments) - distance) > 1:
                raise ValueError("Road segment sum differs from table")
            routes.append({"type": "Feature", "properties": {"from": p["code"], "to": f"V{j}",
                           "distance_m": distance}, "geometry": route["geometry"]})
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in (("cdo_tsp_locations.csv", locations), ("cdo_tsp_dataset.csv", pairs)):
        with (output / name).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
    data_output = output / "data"
    data_output.mkdir(exist_ok=True)
    (data_output / "routes.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": routes}) + "\n")
    audit = {"locations": n, "ordered_pairs_including_diagonal": len(pairs),
             "independently_requested_routes": len(routes),
             "max_route_table_difference_m": round(max_route_difference, 6),
             "max_snap_distance_m": max(r["Snap_Distance_m"] for r in locations),
             "osm_base_timestamp": pois["osm3s"]["timestamp_osm_base"],
             "acquired_from_utc": min(v["retrieved_at_utc"] for v in manifest.values()),
             "acquired_to_utc": max(v["retrieved_at_utc"] for v in manifest.values()),
             "osrm_data_version": table.get("data_version", "Not supplied by public server"),
             "attribution": "© OpenStreetMap contributors; ODbL 1.0; https://www.openstreetmap.org/copyright",
             "cost_definition": "Lengths of OSRM recommended driving routes; not shortest-distance road paths or live-traffic measurements",
             "access_status": "Map-derived routing points; no field verification of entrances, parking, permits or current opening"}
    (data_output / "dataset_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT)
    parser.add_argument("--raw", type=Path, default=ROOT / "data/raw")
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.raw), indent=2))
