"""Positive controls, deliberately invalid artifacts, and packet isolation."""

import argparse
import copy
import itertools
import json
import tempfile
import unittest
from pathlib import Path

from checks import (CASES, ROOT, count_cycle, design_score, grade_directory,
                    grade_result, load_json, polygon_counts, tree_count)
from harness import grade, git, prepare, select_cases, sha, snapshot_ref


def controls():
    """Fixed witnesses, separate from the computations being tested."""
    polygon_rows = zip(("P1", "P2", "P3", "P4", "P5"),
                       ((12, 8, 3), (12, 10, 2), (14, 16, 0), (27, 5, 12), (5, 3, 2)))
    return {
        "cycle-count": {"counts": [dict(n=n, count=v) for n, v in
                                      enumerate((4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843), 3)]},
        "lattice-area": {"polygons": [dict(id=name, twice_area=v[0], boundary=v[1], interior=v[2])
                                       for name, v in polygon_rows]},
        "tree-collision": {"n": 5,
                           "edges_a": [[0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4]],
                           "edges_b": [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4], [0, 2]],
                           "trees_a": 12, "trees_b": 11},
        "moment-tail": {"p": [0, "1/2", 0, "1/2", 0],
                        "q": ["1/8", 0, "3/4", 0, "1/8"],
                        "mean": 0, "variance": 1, "tail_p": 0, "tail_q": "1/8"},
        "grid-packing": {"points": [[0, 0], [0, 3], [2, 5], [3, 0], [5, 2], [5, 5]],
                         "min_distance_squared": 8},
        "quadratic-design": {"xs": [-3, -3, 0, 0, 3, 3], "determinant": 23328},
    }


def result(case, evidence=None):
    status = "bounded"
    if CASES[case] == "false-conjecture":
        status = "refuted"
    if evidence is None:
        evidence = controls()[case]
    return {"case_id": case, "status": status, "claim": "Control only; no proof supplied.",
            "evidence": evidence, "limitations": ["Finite control"],
            "reproduction": ["Coordinator tests reproduce these quantities"]}


def permutation_determinant(matrix):
    """Independent Leibniz oracle, used only for small test matrices."""
    total = 0
    for permutation in itertools.permutations(range(len(matrix))):
        inversions = sum(a > b for i, a in enumerate(permutation) for b in permutation[i + 1:])
        product = (-1)**inversions
        for i, j in enumerate(permutation):
            product *= matrix[i][j]
        total += product
    return total


class ExactChecks(unittest.TestCase):
    def test_positive_controls(self):
        for case in CASES:
            with self.subTest(case=case):
                self.assertTrue(grade_result(case, result(case))["artifact_valid"])

    def test_deliberately_wrong_numbers_fail_every_checker(self):
        invalid = controls()
        invalid["cycle-count"]["counts"][0]["count"] += 1
        invalid["lattice-area"]["polygons"][0]["interior"] += 1
        invalid["tree-collision"]["trees_b"] += 1
        invalid["moment-tail"]["tail_q"] = "1/9"
        invalid["grid-packing"]["min_distance_squared"] += 1
        invalid["quadratic-design"]["determinant"] += 1
        for case, evidence in invalid.items():
            with self.subTest(case=case):
                self.assertFalse(grade_result(case, result(case, evidence))["artifact_valid"])

    def test_cycle_against_direct_binary_enumeration(self):
        for n in range(3, 15):
            valid = sum(not any(bits[i] == bits[(i + 1) % n] == 1 for i in range(n))
                        for bits in itertools.product((0, 1), repeat=n))
            self.assertEqual(count_cycle(n), valid)

    def test_tree_enumerator_against_laplacian_determinant(self):
        fixture = controls()["tree-collision"]
        for key in ("edges_a", "edges_b"):
            edges = fixture[key]
            matrix = [[-int([i, j] in edges or [j, i] in edges) for j in range(5)] for i in range(5)]
            for i in range(5):
                matrix[i][i] = sum(i in edge for edge in edges)
            self.assertEqual(tree_count(5, edges), permutation_determinant([row[:4] for row in matrix[:4]]))

    def test_design_scores_against_cauchy_binet(self):
        for xs in itertools.combinations_with_replacement(range(-3, 4), 6):
            score = sum(((b - a) * (c - a) * (c - b))**2
                        for a, b, c in itertools.combinations(xs, 3))
            self.assertEqual(design_score(xs), score)

    def test_polygon_orientation_and_translation(self):
        inputs = load_json(ROOT / "cases/lattice-area/input.json")
        for vertices in inputs.values():
            expected = polygon_counts(vertices)
            self.assertEqual(expected, polygon_counts(vertices[::-1]))
            self.assertEqual(expected, polygon_counts([[x - 7, y + 3] for x, y in vertices]))

    def test_invalid_probability_mass_and_near_miss_rejected(self):
        data = controls()["moment-tail"]
        data["q"][2] = "749999/1000000"
        self.assertFalse(grade_result("moment-tail", result("moment-tail", data))["artifact_valid"])
        data = controls()["moment-tail"]
        data["tail_q"] = "124999/1000000"
        self.assertFalse(grade_result("moment-tail", result("moment-tail", data))["artifact_valid"])

    def test_valid_large_denominator_witness_is_accepted(self):
        data = controls()["moment-tail"]
        data["q"] = ["1/1000001", "999993/2000002", "6/1000001",
                     "999993/2000002", "1/1000001"]
        data["tail_q"] = "1/1000001"
        self.assertTrue(grade_result("moment-tail", result("moment-tail", data))["artifact_valid"])

    def test_rational_exponents_rejected_before_conversion(self):
        data = controls()["moment-tail"]
        data["tail_q"] = "1e9999999999"
        checked = grade_result("moment-tail", result("moment-tail", data))
        self.assertFalse(checked["artifact_valid"])
        self.assertIn("rational syntax", checked["errors"][0])

    def test_equal_graphs_and_duplicate_edges_rejected(self):
        data = controls()["tree-collision"]
        data["edges_b"] = copy.deepcopy(data["edges_a"])
        data["trees_b"] = 12
        self.assertFalse(grade_result("tree-collision", result("tree-collision", data))["artifact_valid"])
        data["edges_a"].append([2, 0])
        self.assertFalse(grade_result("tree-collision", result("tree-collision", data))["artifact_valid"])

    def test_false_acceptance_and_unresolved_are_retained(self):
        data = result("tree-collision")
        data["status"] = "proved"
        checked = grade_result("tree-collision", data)
        self.assertTrue(checked["declared_false_conjecture_acceptance"])
        self.assertTrue(checked["human_review_required"])
        data["status"] = "unresolved"
        data["evidence"] = {"search_boundary": "Only cycles examined"}
        checked = grade_result("tree-collision", data)
        self.assertEqual(checked["declared_status"], "unresolved")
        self.assertFalse(checked["artifact_valid"])

    def test_feasible_suboptimal_is_valid_but_has_gap(self):
        data = {"xs": [-3, -2, -1, 1, 2, 3], "determinant": 10976}
        checked = grade_result("quadratic-design", result("quadratic-design", data))
        self.assertTrue(checked["artifact_valid"])
        self.assertGreater(checked["computed"]["gap"], 0)

    def test_json_rejects_ambiguous_or_nonfinite_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                         '{"a":1e9999999999}', '{"a":' + "9" * 65 + '}'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    load_json(path)

    def test_missing_artifacts_fail_without_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "investigate.py").write_text("raise RuntimeError('must not execute')")
            self.assertFalse(grade_directory("cycle-count", root)["artifact_valid"])


class PacketChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        revised = self.root / "source"
        revised.mkdir()
        (revised / "SKILL.md").write_text("Synthetic revision used only for packet isolation tests.\n")
        # Unit tests also run in shallow CI checkouts; trials keep their historical baseline.
        self.original_ref = git(ROOT.parents[1], "rev-parse", "HEAD").decode().strip()
        self.args = argparse.Namespace(repo=ROOT.parents[1], original_ref=self.original_ref,
                                       revised_ref=None, revised_dir=revised, out=self.root / "run",
                                       cases="smoke", model="test-model", effort="test-effort",
                                       pair_id="test-pair", tool_limit=24, seconds=600, retrieval_dir=None)

    def test_actual_snapshots_and_no_answer_key_in_packets(self):
        prepared = prepare(self.args)
        freeze = load_json(self.args.out / "coordinator/FREEZE.json")
        original, source = snapshot_ref(self.args.repo, self.original_ref)
        self.assertEqual(source["commit"], self.original_ref)
        self.assertEqual(freeze["arms"]["original"]["files"]["boost/SKILL.md"]["sha256"], sha(original["SKILL.md"]))
        self.assertTrue(prepared["freeze_sha256"])
        for arm in ("original", "revised"):
            packet = self.args.out / "packets" / arm
            self.assertEqual({p.name for p in packet.iterdir()}, {"boost", "cases", "WORKER.md", "FORMAT.md"})
            self.assertFalse((packet / "checks.py").exists())
            self.assertEqual({p.name for p in (packet / "cases").iterdir()}, set(select_cases("smoke")))
        original_packet = self.args.out / "packets/original"
        revised_packet = self.args.out / "packets/revised"
        self.assertEqual((original_packet / "WORKER.md").read_bytes(), (revised_packet / "WORKER.md").read_bytes())
        self.assertEqual((revised_packet / "boost/SKILL.md").read_bytes(), (self.args.revised_dir / "SKILL.md").read_bytes())
        with self.assertRaises(ValueError):
            prepare(self.args)

    def test_missing_timeout_and_input_changes_remain_visible(self):
        prepare(self.args)
        args = argparse.Namespace(run=self.args.out, arm="original")
        checked = grade(args)
        self.assertFalse(checked["artifact_checks_pass"])
        self.assertEqual(len(checked["results"]), 3)
        record_path = self.args.out / "coordinator/original-run.json"
        record = load_json(record_path)
        record.update(state="timeout", failure="Control timeout")
        record_path.write_text(json.dumps(record))
        (self.args.out / "packets/original/cases/cycle-count/REQUEST.md").write_text("Changed input")
        checked = grade(args)
        self.assertEqual(checked["run_record"]["state"], "timeout")
        self.assertEqual(len(checked["input_integrity_errors"]), 1)

    def test_invalid_selection_writes_nothing(self):
        self.args.cases = "cycle-count,missing"
        with self.assertRaises(ValueError):
            prepare(self.args)
        self.assertFalse(self.args.out.exists())


if __name__ == "__main__":
    unittest.main()
