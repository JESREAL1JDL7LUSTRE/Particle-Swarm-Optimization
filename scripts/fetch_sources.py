"""Explicit network refresh; normal builds use the committed source snapshot.

Run from any directory: python scripts/fetch_sources.py --output /tmp/new-sources
Review new coordinates/routes before replacing the committed snapshot.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import ssl
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OSRM = "https://router.project-osrm.org"
OVERPASS = "https://overpass-api.de/api/interpreter"


def acquire(url, path, manifest):
    if path.name in manifest:
        entry = manifest[path.name]
        if entry["url"] != url or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Existing cache does not match request: {path}")
        return json.loads(path.read_text())
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    request = Request(url, headers={"User-Agent": "CDO-Tourist-TSP-Academic/1.0"})
    for attempt in range(3):
        try:
            with urlopen(request, context=context, timeout=45) as response:
                body = response.read()
            break
        except Exception:
            if attempt == 2:
                raise
            print(f"Retrying {path.name}", flush=True)
            time.sleep(2)
    payload = json.loads(body)
    if payload.get("code", "Ok") != "Ok" or "remark" in payload:
        raise ValueError(f"Incomplete mapping response: {payload}")
    path.write_bytes(body)
    manifest[path.name] = {
        "url": url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    (path.parent / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Saved {path.name} ({len(body)} bytes)", flush=True)
    time.sleep(1)  # Be considerate to the public demo services.
    return payload


def fetch(output, resume=False):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()) and not resume:
        raise ValueError("Use an empty output directory to preserve existing evidence.")
    selection = json.loads((ROOT / "data/attractions.json").read_text())
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if resume and manifest_path.exists() else {}
    query = "[out:json][timeout:45];(" + "".join(
        f"{p['osm_type']}({p['osm_id']});" for p in selection
    ) + ");out center;"
    acquire(OVERPASS + "?" + urlencode({"data": query}), output / "osm_attractions.json", manifest)
    coords = ";".join(f"{p['request_lon']},{p['request_lat']}" for p in selection)
    table = acquire(
        f"{OSRM}/table/v1/driving/{coords}?annotations=distance,duration",
        output / "osrm_table.json", manifest,
    )
    # Preserve each ordered pair's route geometry and lengths as independent
    # evidence. Reuse table hints so the endpoints match the matrix's snapping.
    for i, source in enumerate(table["sources"]):
        for j, target in enumerate(table["destinations"]):
            if i == j:
                continue
            pair = f"{selection[i]['request_lon']},{selection[i]['request_lat']};{selection[j]['request_lon']},{selection[j]['request_lat']}"
            params = urlencode({
                "overview": "full", "geometries": "geojson", "steps": "false",
                "annotations": "distance", "continue_straight": "false",
                "hints": source["hint"] + ";" + target["hint"],
            })
            acquire(f"{OSRM}/route/v1/driving/{pair}?{params}",
                    output / f"route_V{i}_V{j}.json", manifest)
            (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    fetch(args.output, args.resume)
