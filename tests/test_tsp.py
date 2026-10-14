import csv
import itertools
import json
from pathlib import Path
import random
import shutil
import tempfile
import unittest

import cdo_tsp_pso_solver as solver
from scripts.build_dataset import build

ROOT = Path(__file__).resolve().parents[1]
# Directed instance: unique optimal depot-fixed cycle 0->1->2->3->0, cost 4.
DIRECTED = [[0, 1, 9, 9], [9, 0, 1, 9], [9, 9, 0, 1], [1, 9, 9, 0]]


class AlgorithmTests(unittest.TestCase):
    def test_return_leg_and_direction(self):
        self.assertEqual(solver.calculate_tour_distance([0, 1, 2, 3], DIRECTED), 4)
        self.assertEqual(solver.calculate_tour_distance([0, 3, 2, 1], DIRECTED), 36)

    def test_exact_against_independent_enumeration(self):
        rng = random.Random(94)
        matrix = [[0 if i == j else rng.randrange(1, 100) for j in range(6)] for i in range(6)]
        all_costs = []
        for perm in itertools.permutations(range(1, 6)):
            closed = [0, *perm, 0]
            all_costs.append(sum(matrix[a][b] for a, b in zip(closed, closed[1:])))
        tour, cost = solver.brute_force_tsp(matrix)
        self.assertEqual(cost, min(all_costs))
        self.assertEqual(solver.verify_tour(tour, matrix), cost)

    def test_swaps_reach_target_and_preserve_depot(self):
        # Exercises swaps that would cancel if computed using stale indices.
        for target_tail in itertools.permutations([1, 2, 3, 4]):
            position, target = [0, 4, 3, 2, 1], [0, *target_tail]
            before = position.copy()
            swaps = solver.attract(position, target, 1.0, random.Random(3))
            for a, b in swaps:
                self.assertNotIn(0, (a, b))
                before[a], before[b] = before[b], before[a]
            self.assertEqual(position, target)
            self.assertEqual(before, target)

    def test_zero_attraction(self):
        position = [0, 3, 2, 1]
        self.assertEqual(solver.attract(position, [0, 1, 2, 3], 0, random.Random(1)), [])
        self.assertEqual(position, [0, 3, 2, 1])

    def test_pso_determinism_and_local_random_state(self):
        state = random.getstate()
        a = solver.pso_tsp(DIRECTED, seed=7)
        self.assertEqual(a, solver.pso_tsp(DIRECTED, seed=7))
        self.assertEqual(state, random.getstate())
        self.assertEqual(a[1], 4)

    def test_all_updated_positions_are_evaluated(self):
        # One particle starts with a bad tour under seed 0. A mutation improves it
        # on the only update. The final evaluation must include that update.
        found = False
        for seed in range(20):
            initial = solver.pso_tsp(DIRECTED, num_particles=1, max_iterations=0, seed=seed)
            updated = solver.pso_tsp(DIRECTED, num_particles=1, max_iterations=1,
                                     w=0, c1=0, c2=0, mutation=1, seed=seed)
            self.assertEqual(len(updated[2]), 2)
            if updated[1] < initial[1]:
                found = True
        self.assertTrue(found)

    def test_history_and_valid_tours(self):
        for seed in range(10):
            route, cost, history = solver.pso_tsp(DIRECTED, seed=seed, max_iterations=20)
            self.assertEqual(solver.verify_tour(route, DIRECTED), cost)
            self.assertEqual(history[-1], cost)
            self.assertEqual(len(history), 21)
            self.assertTrue(all(a >= b for a, b in zip(history, history[1:])))

    def test_small_instances(self):
        for matrix, expected in [([[0]], 0), ([[0, 2], [5, 0]], 7)]:
            self.assertEqual(solver.pso_tsp(matrix)[1], expected)
            self.assertEqual(solver.brute_force_tsp(matrix)[1], expected)

    def test_invalid_parameters(self):
        for kw in [{"c1": 1.5}, {"c2": -1}, {"w": float("nan")},
                   {"mutation": 2}, {"num_particles": 0}, {"max_iterations": -1}]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                solver.pso_tsp(DIRECTED, **kw)

    def test_invalid_tours(self):
        for tour in [[], [0, 1, 1, 3], [1, 2, 3, 0], [0, 1, 2, 4]]:
            with self.subTest(tour=tour), self.assertRaises(ValueError):
                solver.verify_tour(tour, DIRECTED)

    def test_invalid_matrices(self):
        for matrix in [[], [[0, 1]], [[0, None], [2, 0]], [[0, -2], [2, 0]], [[1]], [[0, 0], [2, 0]]]:
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                solver.pso_tsp(matrix)


class DatasetTests(unittest.TestCase):
    def test_full_source_to_csv_rebuild(self):
        with tempfile.TemporaryDirectory() as temp:
            audit = build(Path(temp))
            self.assertEqual(audit["independently_requested_routes"], 56)
            for name in ["cdo_tsp_dataset.csv", "cdo_tsp_locations.csv", "data/routes.geojson", "data/dataset_audit.json"]:
                self.assertEqual((ROOT / name).read_bytes(), (Path(temp) / name).read_bytes(), name)

    def test_real_dataset_and_exact_match(self):
        locations, matrix = solver.load_dataset(ROOT)
        self.assertEqual(len(locations), 8)
        self.assertTrue(any(matrix[i][j] != matrix[j][i] for i in range(8) for j in range(8)))
        route, cost, _ = solver.pso_tsp(matrix, seed=123)
        self.assertEqual(solver.verify_tour(route, matrix), cost)
        self.assertGreaterEqual(cost, solver.brute_force_tsp(matrix)[1])

    def test_csv_edits_are_loaded_and_bad_pairs_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            shutil.copy(ROOT / "cdo_tsp_locations.csv", folder)
            with (ROOT / "cdo_tsp_dataset.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
            def write(data):
                with (folder / "cdo_tsp_dataset.csv").open("w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(data)
            rows[1]["Distance_m"] = "12345.6"
            write(rows)
            self.assertEqual(solver.load_dataset(folder)[1][0][1], 123456)
            for invalid in [rows[:-1], rows + [rows[1]], [dict(rows[0], Distance_m="NaN")] + rows[1:]]:
                write(invalid)
                with self.assertRaises(ValueError):
                    solver.load_dataset(folder)

    def test_saved_results_and_audit(self):
        _, matrix = solver.load_dataset(ROOT)
        s = json.loads((ROOT / "results/summary.json").read_text())
        self.assertEqual(s["input_sha256"], solver.fingerprint(ROOT))
        self.assertEqual(s["pso_distance_m"] * 10, solver.verify_tour(s["pso_tour"], matrix))
        self.assertEqual(s["exact_distance_m"] * 10, solver.brute_force_tsp(matrix)[1])
        with (ROOT / "results/tour_legs.csv").open() as f:
            legs = list(csv.DictReader(f))
        self.assertAlmostEqual(sum(float(r["distance_m"]) for r in legs), s["pso_distance_m"])
        with (ROOT / "results/repeated_runs.csv").open() as f:
            runs = list(csv.DictReader(f))
        self.assertEqual(sum(r["optimal"] == "True" for r in runs), s["repeated_runs"]["optimal_count"])


if __name__ == "__main__":
    unittest.main()
