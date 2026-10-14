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

    # Figure 1: Labeled Topological Graph (left) and Asymmetric Weight Matrix Heatmap (right)
    fig, (ax_graph, ax_mat) = plt.subplots(1, 2, figsize=(18.5, 9), gridspec_kw={'width_ratios': [1.15, 1]}, layout="constrained")
    angles = [math.pi / 2 - 2 * math.pi * i / n for i in range(n)]
    radius = 1.0
    coords = {i: (radius * math.cos(angles[i]), radius * math.sin(angles[i])) for i in range(n)}

    # Faint background directed arcs
    for i in range(n):
        for j in range(n):
            if i != j and (i, j) not in legs:
                x1, y1 = coords[i]
                x2, y2 = coords[j]
                ax_graph.annotate("", xy=(x2, y2), xytext=(x1, y1),
                                  arrowprops=dict(arrowstyle="->", color="#c5d3df", lw=0.7, alpha=0.35,
                                                  shrinkA=18, shrinkB=18, connectionstyle="arc3,rad=0.08"))

    # Highlighted PSO tour legs with arc weights
    for k, (u, v) in enumerate(legs):
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        ax_graph.annotate("", xy=(x2, y2), xytext=(x1, y1),
                          arrowprops=dict(arrowstyle="-|>", color="#026d75", lw=2.5,
                                          shrinkA=18, shrinkB=18, connectionstyle="arc3,rad=0.12"))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        lx, ly = (mx - 0.08 * (dy / dist), my + 0.08 * (dx / dist)) if dist > 0 else (mx, my)
        leg_km = matrix[u][v] / 10000
        ax_graph.text(lx, ly, f"{leg_km:.2f} km", fontsize=8.5, weight="bold", color="#014f55",
                      bbox=dict(boxstyle="round,pad=0.2", facecolor="#eef7f7", edgecolor="#026d75", alpha=0.9),
                      ha="center", va="center", zorder=7)

    # Vertices
    for i in range(n):
        x, y = coords[i]
        is_depot = (i == 0)
        color = "#b33b53" if is_depot else "#17344b"
        ax_graph.scatter(x, y, s=500 if is_depot else 400, color=color, edgecolors="white", linewidths=2.5, zorder=5)
        ax_graph.text(x, y, f"V{i}", color="white", weight="bold", fontsize=10, ha="center", va="center", zorder=6)
        label_dist = 1.30
        lx = label_dist * math.cos(angles[i])
        ly = label_dist * math.sin(angles[i])
        name = locations[i]["Location_Name"]
        if is_depot:
            name += " (Start/Depot)"
        ha = "left" if lx > 0.25 else ("right" if lx < -0.25 else "center")
        ax_graph.text(lx, ly, name, weight="bold" if is_depot else "normal", fontsize=9.5,
                      color="#b33b53" if is_depot else "#17344b", ha=ha, va="center")

    ax_graph.set_xlim(-1.95, 1.85)
    ax_graph.set_ylim(-1.55, 1.55)
    ax_graph.axis("off")
    ax_graph.set_title("Labeled Weighted Graph $G = (V, A, D)$\n8 vertices, 56 directed arcs; PSO tour highlighted in teal",
                       fontsize=12, pad=15, weight="bold")

    # Asymmetric Weight Matrix Heatmap
    heat = ax_mat.imshow(km, cmap="Blues", vmin=0, vmax=max(map(max, km)))
    for i in range(n):
        for j in range(n):
            ax_mat.text(j, i, f"{km[i][j]:.2f}", ha="center", va="center",
                        color="white" if km[i][j] > max(map(max, km)) * 0.6 else "#15304a", fontsize=8.5)
    ax_mat.set_xticks(range(n), codes)
    ax_mat.set_yticks(range(n), [f"{p['Node_ID']}  {p['Location_Name']}" for p in locations], fontsize=8.5)
    ax_mat.set_xlabel("Destination", fontsize=10)
    ax_mat.set_ylabel("Origin", fontsize=10)
    ax_mat.set_title("Asymmetric Travel-Cost Matrix $D$\nDirected OSRM car-route lengths in km", fontsize=12, pad=15, weight="bold")
    fig.colorbar(heat, ax=ax_mat, label="Route distance (km)", shrink=0.75)
    fig.suptitle("Cagayan de Oro Tourist Driving Tour: Graph Model & Asymmetric Weight Matrix", fontsize=15, weight="bold")
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

    try:
        from scripts.generate_interactive_map import generate_interactive_map
        generate_interactive_map(directory, output)
    except Exception:
        pass

