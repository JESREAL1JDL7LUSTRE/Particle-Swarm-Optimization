"""Figures from the loaded dataset and measured experiment, without basemap tiles."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.ticker import ScalarFormatter

ATTRIBUTION = "Map data © OpenStreetMap contributors (ODbL) · Routing: OSRM"


def generate_visualizations(locations, matrix, summary, history, directory, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    features = json.loads((Path(directory) / "data/routes.geojson").read_text())["features"]
    routes = {(f["properties"]["from"], f["properties"]["to"]): f for f in features}
    tour = summary["pso_tour"]
    legs = [(u, tour[(i + 1) % len(tour)]) for i, u in enumerate(tour)]
    for u, v in legs:
        feature = routes[(f"V{u}", f"V{v}")]
        if abs(feature["properties"]["distance_m"] * 10 - matrix[u][v]) > 0.01:
            raise ValueError("Road geometry does not match edited costs; rebuild data or use --no-plots")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False})
    codes = [p["Node_ID"] for p in locations]
    n = len(codes)
    km = [[v / 10000 for v in row] for row in matrix]
    fig, ax = plt.subplots(figsize=(11, 8), layout="constrained")
    heat = ax.imshow(km, cmap="Blues", vmin=0, vmax=max(map(max, km)))
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{km[i][j]:.2f}", ha="center", va="center",
                    color="white" if km[i][j] > max(map(max, km)) * 0.6 else "#15304a")
    ax.set_xticks(range(n), codes)
    ax.set_yticks(range(n), [f"{p['Node_ID']}  {p['Location_Name']}" for p in locations], fontsize=9)
    ax.set_xlabel("Destination")
    ax.set_ylabel("Origin")
    ax.set_title("CDO tourist travel-cost graph\nDirected driving distances (km); 8 vertices, 56 arcs", pad=18)
    fig.colorbar(heat, ax=ax, label="Route length (km)", shrink=0.8)
    fig.supxlabel("Cells are lengths of OSRM recommended car routes. Opposite directions may differ.\n" + ATTRIBUTION, fontsize=9)
    fig.savefig(output / "figure1_cdo_graph_network.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6), layout="constrained")
    ax.step(range(len(history)), [v / 10000 for v in history], where="post", color="#007f8b", lw=2,
            label=f"PSO best so far (seed {summary['parameters']['seed']})")
    exact_km = summary["exact_distance_m"] / 1000
    ax.axhline(exact_km, color="#a84436", ls="--", label=f"Exact matrix optimum: {exact_km:.4f} km")
    first = summary["first_optimum_iteration"]
    text = f"First match: iteration {first}" if first is not None else f"Final optimality gap: {summary['optimality_gap_percent']:.3f}%"
    ax.text(0.97, 0.58, text, transform=ax.transAxes, ha="right",
            bbox={"facecolor": "#eef5f5", "edgecolor": "none", "pad": 9})
    ax.set(xlabel="Completed position-update iterations (0 = initial swarm)", ylabel="Closed-tour length (km)",
           title="PSO convergence on the saved tourist distance matrix")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper right")
    ax.margins(y=0.17)
    fig.supxlabel("One seeded run. Repeated-run outcomes are reported separately in results/repeated_runs.csv.", fontsize=9)
    fig.savefig(output / "figure2_pso_convergence.png", dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(14, 10), layout="constrained")
    gs = fig.add_gridspec(2, 2, width_ratios=[1.7, 1], height_ratios=[1, 1])
    ax = fig.add_subplot(gs[:, 0])
    inset = fig.add_subplot(gs[0, 1])
    key = fig.add_subplot(gs[1, 1]); key.axis("off")
    colors = [colormaps["tab10"](i) for i in range(n)]
    for k, (u, v) in enumerate(legs):
        points = routes[(f"V{u}", f"V{v}")]["geometry"]["coordinates"]
        xs, ys = zip(*points)
        for area in (ax, inset):
            area.plot(xs, ys, color=colors[k], lw=2.2, alpha=0.8)
        mid = len(points) // 2
        if mid > 0:
            ax.annotate("", xy=points[min(mid + 2, len(points) - 1)], xytext=points[max(0, mid - 2)],
                        arrowprops={"arrowstyle": "->", "color": colors[k], "lw": 2})
    for area in (ax, inset):
        for p in locations:
            x, y = p["Route_Longitude"], p["Route_Latitude"]
            area.scatter(x, y, color="#b33b53" if p["Node_ID"] == "V0" else "#17344b",
                         edgecolors="white", s=90, zorder=4)
            # Tight downtown labels appear only in the detail panel.
            if area is inset or int(p["Node_ID"][1:]) >= 4:
                offsets = {"V0": (8, 9), "V1": (8, 8), "V2": (-22, -17), "V3": (8, -17)}
                area.annotate(p["Node_ID"], (x, y), xytext=offsets.get(p["Node_ID"], (8, 8)),
                              textcoords="offset points", weight="bold", fontsize=10,
                              bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1})
        area.grid(alpha=0.2)
        area.set_aspect(1 / math.cos(math.radians(8.46)))
        area.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        area.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        area.tick_params(labelsize=8)
        area.set_xlabel("Longitude (°E)", fontsize=9)
        area.set_ylabel("Latitude (°N)", fontsize=9)
    inset.set_xlim(124.6406, 124.6466); inset.set_ylim(8.4745, 8.4785)
    inset.set_title("Downtown detail: V0–V3", fontsize=11)
    ax.set_title("Saved road-route geometry", fontsize=12)
    ax.margins(0.09)
    key.text(0, 0.99, "VISITING ORDER AND LEG LENGTHS", weight="bold", fontsize=10, va="top")
    y = 0.91
    for k, (u, v) in enumerate(legs):
        key.text(0, y, f"{k+1}. V{u} → V{v}     {matrix[u][v] / 10000:.4f} km", color=colors[k], fontsize=10)
        y -= 0.058
    y -= 0.03
    for p in locations:
        key.text(0, y, f"{p['Node_ID']}  {p['Location_Name']}", fontsize=9)
        y -= 0.045
    status = "matches exact matrix optimum" if summary["matches_exact"] else f"{summary['optimality_gap_percent']:.2f}% gap to exact optimum"
    fig.suptitle(f"Cagayan de Oro tourist driving tour\nPSO: {summary['pso_distance_m']/1000:.4f} km — {status}", fontsize=16, weight="bold")
    fig.supxlabel("Routes join modeled car-network points. On-site walking and parking are excluded.\n" + ATTRIBUTION, fontsize=10)
    fig.savefig(output / "figure3_cdo_tour.png", dpi=180)
    plt.close(fig)
