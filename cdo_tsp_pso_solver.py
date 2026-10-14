"""Discrete swap PSO for a Cagayan de Oro tourist driving tour.

Input costs are integer decimetres internally (OSRM reports tenths of metres).
The algorithm is a documented adaptation, not an exact reproduction of a paper.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import random
import statistics
import time
from decimal import Decimal

ROOT = Path(__file__).resolve().parent


def validate_matrix(matrix):
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("Distance matrix must be nonempty and square")
    if any(type(v) is not int or v < 0 for row in matrix for v in row):
        raise ValueError("Costs must be nonnegative integer decimetres")
    if any(matrix[i][i] != 0 for i in range(n)):
        raise ValueError("Diagonal costs must be zero")
    if any(matrix[i][j] <= 0 for i in range(n) for j in range(n) if i != j):
        raise ValueError("Every distinct pair must have a positive reachable cost")


def load_dataset(directory=ROOT):
    directory = Path(directory)
    with (directory / "cdo_tsp_locations.csv").open(newline="") as f:
        locations = list(csv.DictReader(f))
    codes = [r["Node_ID"] for r in locations]
    if len(codes) < 1 or codes != [f"V{i}" for i in range(len(codes))]:
        raise ValueError("Location IDs must be unique and ordered V0, V1, ...")
    for r in locations:
        for key in ("Latitude", "Longitude", "Route_Latitude", "Route_Longitude"):
            r[key] = float(r[key])
            bound = 90 if "Latitude" in key else 180
            if not math.isfinite(r[key]) or abs(r[key]) > bound:
                raise ValueError(f"Invalid coordinate: {key}")
    index = {code: i for i, code in enumerate(codes)}
    matrix = [[None] * len(codes) for _ in codes]
    with (directory / "cdo_tsp_dataset.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            if row["From_Node"] not in index or row["To_Node"] not in index:
                raise ValueError("Unknown location in distance table")
            i, j = index[row["From_Node"]], index[row["To_Node"]]
            if matrix[i][j] is not None:
                raise ValueError("Duplicate ordered pair in distance table")
            value = Decimal(row["Distance_m"]) * 10
            if not value.is_finite() or value != value.to_integral_value():
                raise ValueError("Distances must be finite multiples of 0.1 metre")
            matrix[i][j] = int(value)
    validate_matrix(matrix)
    return locations, matrix


def calculate_tour_distance(tour, matrix):
    """Closed-tour cost in integer decimetres; return leg is implicit."""
    if not tour:
        raise ValueError("A tour cannot be empty")
    return sum(matrix[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def verify_tour(tour, matrix):
    if len(tour) != len(matrix) or set(tour) != set(range(len(matrix))):
        raise ValueError("Tour must contain every location exactly once")
    if tour[0] != 0:
        raise ValueError("Tour must start at V0")
    return calculate_tour_distance(tour, matrix)


def standardize_tour(tour, start_node=0):
    i = tour.index(start_node)
    return list(tour[i:]) + list(tour[:i])


def attract(position, target, probability, rng):
    """Apply valid swaps immediately, updating indices after each accepted swap.

    At probability 1 the resulting permutation equals target. V0 stays fixed.
    Returns the actual applied swaps for the next iteration's inertia.
    """
    indices = {city: i for i, city in enumerate(position)}
    swaps = []
    for i in range(1, len(position)):
        if position[i] != target[i] and rng.random() < probability:
            j = indices[target[i]]
            position[i], position[j] = position[j], position[i]
            indices[position[i]], indices[position[j]] = i, j
            swaps.append((i, j))
    return swaps


def pso_tsp(matrix, num_particles=40, max_iterations=120,
            w=0.5, c1=0.8, c2=0.8, mutation=0.2, seed=123):
    """Return best tour, cost, and history (initial swarm plus T updates).

    w retains each previous swap with probability w. c1/c2 are probabilities
    for sequential personal/global alignment swaps, not continuous-PSO gains.
    mutation independently introduces one random non-depot swap. Historical
    velocity retains at most 2n swaps so its size cannot grow without bound.
    All random state is local. Every updated population is evaluated.
    """
    validate_matrix(matrix)
    if type(num_particles) is not int or num_particles < 1:
        raise ValueError("num_particles must be a positive integer")
    if type(max_iterations) is not int or max_iterations < 0:
        raise ValueError("max_iterations must be a nonnegative integer")
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in (w, c1, c2, mutation)):
        raise ValueError("Swap probabilities must be in [0, 1]")
    rng = random.Random(seed)
    n = len(matrix)
    positions = [[0] + rng.sample(range(1, n), n - 1) for _ in range(num_particles)]
    velocities = [[] for _ in positions]
    personal = [p.copy() for p in positions]
    costs = [calculate_tour_distance(p, matrix) for p in positions]
    best_idx = min(range(num_particles), key=costs.__getitem__)
    best, best_cost = personal[best_idx].copy(), costs[best_idx]
    history = [best_cost]
    for _ in range(max_iterations):
        target = best.copy()  # One shared snapshot per generation.
        for k, position in enumerate(positions):
            swaps = []
            for i, j in velocities[k]:
                if rng.random() < w:
                    position[i], position[j] = position[j], position[i]
                    swaps.append((i, j))
            swaps.extend(attract(position, personal[k], c1, rng))
            swaps.extend(attract(position, target, c2, rng))
            if n > 2 and rng.random() < mutation:
                i, j = rng.sample(range(1, n), 2)
                position[i], position[j] = position[j], position[i]
                swaps.append((i, j))
            velocities[k] = swaps[-2 * n:]
            cost = calculate_tour_distance(position, matrix)
            if cost < costs[k]:
                personal[k], costs[k] = position.copy(), cost
        k = min(range(num_particles), key=costs.__getitem__)
        if costs[k] < best_cost:
            best, best_cost = personal[k].copy(), costs[k]
        history.append(best_cost)
    verify_tour(best, matrix)
    return best, best_cost, history


def brute_force_tsp(matrix):
    validate_matrix(matrix)
    if len(matrix) > 10:
        raise ValueError("Brute force is limited to at most 10 locations")
    best, best_cost = None, math.inf
    for order in itertools.permutations(range(1, len(matrix))):
        tour = [0, *order]
        cost = calculate_tour_distance(tour, matrix)
        if cost < best_cost:
            best, best_cost = tour, cost
    return best, best_cost


def nearest_neighbor_tsp(matrix):
    validate_matrix(matrix)
    tour, unseen = [0], set(range(1, len(matrix)))
    while unseen:
        nxt = min(unseen, key=lambda v: (matrix[tour[-1]][v], v))
        tour.append(nxt)
        unseen.remove(nxt)
    return tour, calculate_tour_distance(tour, matrix)


def fingerprint(directory):
    return {name: hashlib.sha256((Path(directory) / name).read_bytes()).hexdigest()
            for name in ("cdo_tsp_dataset.csv", "cdo_tsp_locations.csv")}


def run_experiment(directory=ROOT, output=ROOT / "results", seed=123, runs=30):
    if type(runs) is not int or runs < 1:
        raise ValueError("runs must be positive")
    directory, output = Path(directory), Path(output)
    locations, matrix = load_dataset(directory)
    output.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    exact_tour, exact_cost = brute_force_tsp(matrix)
    exact_time = time.perf_counter() - t0
    t0 = time.perf_counter()
    tour, cost, history = pso_tsp(matrix, seed=seed)
    elapsed = time.perf_counter() - t0
    nn_tour, nn_cost = nearest_neighbor_tsp(matrix)
    repetitions = []
    for run_seed in range(runs):
        route, value, values = pso_tsp(matrix, seed=run_seed)
        verify_tour(route, matrix)
        repetitions.append({"seed": run_seed, "distance_m": value / 10,
                            "optimal": value == exact_cost,
                            "first_optimum_iteration": next((i for i, c in enumerate(values) if c == exact_cost), None)})
    summary = {
        "problem": "Eight-stop CDO tourist driving tour",
        "objective": "Minimize the sum of stored OSRM recommended driving-route distances",
        "input_sha256": fingerprint(directory),
        "python_version": platform.python_version(),
        "parameters": {"num_particles": 40, "max_iterations": 120, "w": 0.5,
                       "c1": 0.8, "c2": 0.8, "mutation": 0.2, "seed": seed},
        "pso_tour": tour, "pso_distance_m": cost / 10,
        "exact_tour": exact_tour, "exact_distance_m": exact_cost / 10,
        "exact_tours_evaluated": math.factorial(len(matrix) - 1),
        "nearest_neighbor_tour": nn_tour, "nearest_neighbor_distance_m": nn_cost / 10,
        "optimality_gap_percent": 100 * (cost - exact_cost) / exact_cost if exact_cost else 0.0,
        "matches_exact": cost == exact_cost,
        "first_optimum_iteration": next((i for i, c in enumerate(history) if c == exact_cost), None),
        "initial_best_m": history[0] / 10,
        "pso_seconds": elapsed, "brute_force_seconds": exact_time,
        "repeated_runs": {"count": runs, "seed_range": [0, runs - 1],
                          "optimal_count": sum(r["optimal"] for r in repetitions),
                          "mean_distance_m": statistics.mean(r["distance_m"] for r in repetitions),
                          "min_distance_m": min(r["distance_m"] for r in repetitions),
                          "max_distance_m": max(r["distance_m"] for r in repetitions)},
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for name, fields, rows in [
        ("convergence.csv", ["iteration", "best_distance_m"],
         [{"iteration": i, "best_distance_m": value / 10} for i, value in enumerate(history)]),
        ("repeated_runs.csv", list(repetitions[0]), repetitions),
        ("tour_legs.csv", ["leg", "from_node", "to_node", "distance_m"],
         [{"leg": k + 1, "from_node": f"V{u}", "to_node": f"V{tour[(k + 1) % len(tour)]}",
           "distance_m": matrix[u][tour[(k + 1) % len(tour)]] / 10} for k, u in enumerate(tour)]),
    ]:
        with (output / name).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
    return summary, locations, matrix, history


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    summary, locations, matrix, history = run_experiment(args.data_dir, args.output_dir, args.seed, args.runs)
    print("CDO tourist driving tour: " + " -> ".join(f"V{i}" for i in summary["pso_tour"] + [0]))
    print(f"PSO: {summary['pso_distance_m'] / 1000:.4f} km | Exact: {summary['exact_distance_m'] / 1000:.4f} km")
    print(f"Gap: {summary['optimality_gap_percent']:.4f}% | First optimum iteration: {summary['first_optimum_iteration']}")
    repeat = summary["repeated_runs"]
    print(f"Repeated seeds: {repeat['optimal_count']}/{repeat['count']} matched the exact matrix optimum")
    print("Model costs exclude site walking, sightseeing, opening hours, parking and live traffic.")
    if not args.no_plots:
        from cdo_tsp_plots import generate_visualizations
        generate_visualizations(locations, matrix, summary, history, args.data_dir, args.output_dir)
    print(f"Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
