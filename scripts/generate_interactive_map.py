"""Generate a rich, interactive HTML map with real street tiles (Google Maps & CartoDB).

Uses Leaflet.js to plot the 8 tourist destinations and the actual road network geometry
on an authentic interactive Google Maps & OpenStreetMap basemap of Cagayan de Oro.
Never blocked by 403 rate limits on file:// protocol.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cagayan de Oro Tourist Driving Tour - Interactive Route Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html { margin: 0; padding: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        #map { width: 100%; height: 100%; }
        .legend-card {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(5px);
            padding: 16px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.18);
            max-width: 330px;
            line-height: 1.45;
        }
        .legend-card h3 {
            margin: 0 0 6px 0;
            font-size: 16px;
            color: #17344b;
        }
        .legend-card .subtitle {
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }
        .metric-badge {
            display: inline-block;
            background: #eef5f5;
            color: #007f8b;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .leg-list {
            max-height: 220px;
            overflow-y: auto;
            border-top: 1px solid #eee;
            padding-top: 8px;
            margin-top: 8px;
        }
        .leg-item {
            font-size: 12px;
            padding: 2px 0;
        }
        .leaflet-popup-content {
            font-size: 13px;
            line-height: 1.4;
        }
    </style>
</head>
<body>
<div id="map"></div>
<div class="legend-card">
    <h3>Cagayan de Oro Tourist Tour</h3>
    <div class="subtitle">Graph Theory PIT &bull; Section 2.4 PSO</div>
    <div><span class="metric-badge">PSO Tour: __PSO_KM__ km</span></div>
    <div style="font-size: 12px; color: #444; margin-bottom: 6px;">
        Exact Matrix Optimum: <b>__EXACT_KM__ km</b><br>
        Optimality Gap: <b>__GAP__%</b> (Approximate)
    </div>
    <div class="leg-list">
        __LEGS_LIST__
    </div>
    <div style="font-size: 11px; color: #777; margin-top: 10px; border-top: 1px solid #eee; padding-top: 6px;">
        Basemap: Google Maps &bull; Routing: OSRM
    </div>
</div>

<script>
    var map = L.map('map').setView([8.455, 124.665], 13);

    // Google Maps Roads (Default)
    var googleRoads = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        attribution: '&copy; Google Maps'
    }).addTo(map);

    // Google Maps Satellite / Hybrid
    var googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        attribution: '&copy; Google Maps (Satellite)'
    });

    // CartoDB Voyager (Never blocked on file://)
    var cartoVoyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    });

    var baseLayers = {
        "Google Maps (Roads)": googleRoads,
        "Google Maps (Satellite)": googleHybrid,
        "CartoDB Street Map": cartoVoyager
    };
    L.control.layers(baseLayers).addTo(map);

    // Road Polylines
    __POLYLINES_JS__

    // POI Markers
    __MARKERS_JS__
</script>
</body>
</html>
"""

def generate_interactive_map(directory=ROOT, output=ROOT / "results"):
    directory = Path(directory)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    
    with (directory / "cdo_tsp_locations.csv").open(newline="") as f:
        locations = list(csv.DictReader(f))
    
    summary = json.loads((output / "summary.json").read_text())
    tour = summary["pso_tour"]
    legs = [(u, tour[(i + 1) % len(tour)]) for i, u in enumerate(tour)]
    
    routes_data = json.loads((directory / "data/routes.geojson").read_text())["features"]
    route_map = {(f["properties"]["from"], f["properties"]["to"]): f for f in routes_data}
    
    leg_colors = [
        "#0072b2", "#e69f00", "#009e73", "#d55e00",
        "#cc79a7", "#56b4e9", "#e51e1e", "#026d75"
    ]
    
    # Prepare markers JS
    markers_js = []
    for p in locations:
        nid = p["Node_ID"]
        name = p["Location_Name"]
        lat = float(p["Route_Latitude"])
        lon = float(p["Route_Longitude"])
        is_depot = (nid == "V0")
        color = "#b33b53" if is_depot else "#17344b"
        gmaps_url = p.get("Google_Maps_URL", f"https://maps.google.com/?q={lat},{lon}")
        
        popup_html = f"<b>{nid}: {name}</b><br>{p['Role']}<br><a href='{gmaps_url}' target='_blank'>View on Google Maps</a>"
        markers_js.append(f"""
        L.circleMarker([{lat}, {lon}], {{
            radius: {11 if is_depot else 8},
            fillColor: '{color}',
            color: '#fff',
            weight: 2.5,
            opacity: 1,
            fillOpacity: 0.95
        }}).addTo(map).bindPopup("{popup_html}").bindTooltip("<b>{nid}</b>: {name}", {{permanent: false, direction: 'top'}});
        """)
        
    # Prepare polylines JS
    polylines_js = []
    legs_html = []
    for idx, (u, v) in enumerate(legs):
        feature = route_map[(f"V{u}", f"V{v}")]
        dist_km = feature["properties"]["distance_m"] / 1000
        coords = [[pt[1], pt[0]] for pt in feature["geometry"]["coordinates"]]
        col = leg_colors[idx % len(leg_colors)]
        
        polylines_js.append(f"""
        L.polyline({json.dumps(coords)}, {{
            color: '{col}',
            weight: 5,
            opacity: 0.9
        }}).addTo(map).bindPopup("<b>Leg {idx+1}: V{u} &rarr; V{v}</b><br>Distance: {dist_km:.4f} km");
        """)
        
        legs_html.append(f"<div class='leg-item' style='color:{col};'><b>{idx+1}. V{u} &rarr; V{v}</b>: {dist_km:.2f} km</div>")

    pso_km = summary["pso_distance_m"] / 1000
    exact_km = summary["exact_distance_m"] / 1000
    gap = summary["optimality_gap_percent"]
    
    html = (TEMPLATE
            .replace("__PSO_KM__", f"{pso_km:.4f}")
            .replace("__EXACT_KM__", f"{exact_km:.4f}")
            .replace("__GAP__", f"{gap:.2f}")
            .replace("__LEGS_LIST__", "\n".join(legs_html))
            .replace("__POLYLINES_JS__", "\n".join(polylines_js))
            .replace("__MARKERS_JS__", "\n".join(markers_js)))
            
    output_path = output / "cdo_tour_interactive_map.html"
    output_path.write_text(html)
    print(f"Interactive map written to {output_path}")

if __name__ == "__main__":
    generate_interactive_map()
