"""Coordinator-only exact checks. Never import or execute participant code."""

import itertools
import json
import math
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = {
    "cycle-count": "rediscovery",
    "lattice-area": "rediscovery",
    "tree-collision": "false-conjecture",
    "moment-tail": "false-conjecture",
    "grid-packing": "exploration",
    "quadratic-design": "exploration",
}
SMOKE = ("cycle-count", "tree-collision", "quadratic-design")
STATUSES = {"proved", "refuted", "bounded", "empirical", "unresolved"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    require(type(value) is int and low <= value <= high, "invalid bounded integer")
    return value


def fraction(value):
    require(type(value) in (int, str), "rational must be an integer or string")
    require(len(str(value)) <= 64, "rational too long")
    require(re.fullmatch(r"[+-]?[0-9]+(?:/[0-9]+)?", str(value)), "use integer or a/b rational syntax")
    return Fraction(value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("nonfinite JSON number: " + value)


def json_integer(token):
    require(len(token) <= 64, "JSON number token too long")
    return int(token)


def json_float(token):
    require(len(token) <= 64, "JSON number token too long")
    value = float(token)
    require(math.isfinite(value), "nonfinite JSON number")
    return value


def load_json(path):
    require(not path.is_symlink(), "JSON symlinks are not accepted")
    require(path.stat().st_size <= 1024 * 1024, "JSON exceeds one MiB")
    return json.loads(path.read_text(), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant, parse_int=json_integer,
                      parse_float=json_float)


def count_cycle(n):
    """Count closed walks via a two-state transfer recurrence."""
    matrix = ((1, 1), (1, 0))
    power = ((1, 0), (0, 1))
    for _ in range(n):
        power = tuple(tuple(sum(power[i][k] * matrix[k][j] for k in range(2))
                            for j in range(2)) for i in range(2))
    return power[0][0] + power[1][1]


def check_cycle(evidence):
    rows = evidence["counts"]
    require(type(rows) is list and len(rows) == 12, "need exactly n=3..14")
    actual = {}
    for row in rows:
        n = integer(row["n"], 3, 14)
        require(n not in actual, "duplicate n")
        actual[n] = integer(row["count"], 0, 2**n)
    expected = {n: count_cycle(n) for n in range(3, 15)}
    require(actual == expected, "incorrect circular configuration counts")
    return {"checked_counts": 12, "general_proof_checked": False}


def cross(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def on_segment(a, b, p):
    return (cross(a, b, p) == 0 and
            min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and
            min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def winding_step(a, b, p):
    if a[1] <= p[1] < b[1] and cross(a, b, p) > 0:
        return 1
    if b[1] <= p[1] < a[1] and cross(a, b, p) < 0:
        return -1
    return 0


def inside(point, edges):
    if any(on_segment(a, b, point) for a, b in edges):
        return False
    return sum(winding_step(a, b, point) for a, b in edges) != 0


def polygon_counts(vertices):
    edges = list(zip(vertices, vertices[1:] + vertices[:1]))
    area2 = abs(sum(a[0] * b[1] - a[1] * b[0] for a, b in edges))
    boundary = sum(math.gcd(abs(b[0] - a[0]), abs(b[1] - a[1])) for a, b in edges)
    xs, ys = zip(*vertices)
    grid = itertools.product(range(min(xs), max(xs) + 1), range(min(ys), max(ys) + 1))
    interior = sum(inside(p, edges) for p in grid)
    return {"twice_area": area2, "boundary": boundary, "interior": interior}


def check_lattice(evidence):
    inputs = load_json(ROOT / "cases/lattice-area/input.json")
    rows = evidence["polygons"]
    require(type(rows) is list and len(rows) == len(inputs), "need all five polygons")
    seen = set()
    for row in rows:
        name = row["id"]
        require(name in inputs and name not in seen, "unknown or duplicate polygon")
        seen.add(name)
        expected = polygon_counts(inputs[name])
        actual = {key: integer(row[key], 0, 1000) for key in expected}
        require(actual == expected, "incorrect polygon counts: " + name)
    return {"checked_polygons": len(seen), "general_proof_checked": False}


def edges_checked(raw, n):
    require(type(raw) is list and len(raw) <= 15, "invalid edge list")
    result = set()
    for edge in raw:
        require(type(edge) is list and len(edge) == 2, "invalid edge")
        a, b = sorted(integer(x, 0, n - 1) for x in edge)
        require(a != b and (a, b) not in result, "loop or duplicate edge")
        result.add((a, b))
    return sorted(result)


def connected(n, edges):
    reached = {0}
    for _ in range(n):
        adjacent = {b for a, b in edges if a in reached}
        adjacent.update(a for a, b in edges if b in reached)
        reached.update(adjacent)
    return len(reached) == n


def tree_count(n, edges):
    return sum(connected(n, subset) for subset in itertools.combinations(edges, n - 1))


def degrees(n, edges):
    return sorted(sum(v in edge for edge in edges) for v in range(n))


def check_trees(evidence):
    n = integer(evidence["n"], 3, 6)
    a = edges_checked(evidence["edges_a"], n)
    b = edges_checked(evidence["edges_b"], n)
    require(connected(n, a) and connected(n, b), "graphs must be connected")
    require(degrees(n, a) == degrees(n, b), "degree multisets differ")
    ta, tb = tree_count(n, a), tree_count(n, b)
    require(integer(evidence["trees_a"], 1, 6**4) == ta, "incorrect trees_a")
    require(integer(evidence["trees_b"], 1, 6**4) == tb, "incorrect trees_b")
    require(ta != tb, "no tree-count separation")
    return {"trees_a": ta, "trees_b": tb, "witness_refutes_conjecture": True}


def distribution(raw):
    require(type(raw) is list and len(raw) == 5, "need five probabilities")
    values = [fraction(v) for v in raw]
    require(all(v >= 0 for v in values) and sum(values) == 1, "invalid probability mass")
    require(values == values[::-1], "distribution must be symmetric")
    mean = sum(x * p for x, p in zip(range(-2, 3), values))
    variance = sum(x * x * p for x, p in zip(range(-2, 3), values)) - mean * mean
    return mean, variance, values[-1]


def check_moments(evidence):
    mp, vp, tp = distribution(evidence["p"])
    mq, vq, tq = distribution(evidence["q"])
    require((mp, vp) == (mq, vq) and tp != tq, "no same-moment tail separation")
    actual = tuple(fraction(evidence[k]) for k in ("mean", "variance", "tail_p", "tail_q"))
    require(actual == (mp, vp, tp, tq), "incorrect claimed moments or tails")
    return {"tail_difference": str(abs(tp - tq)), "witness_refutes_conjecture": True}


def distance2(a, b):
    return sum((x - y)**2 for x, y in zip(a, b))


def check_packing(evidence):
    raw = evidence["points"]
    require(type(raw) is list and len(raw) == 6, "need six points")
    require(all(type(p) is list and len(p) == 2 for p in raw), "invalid coordinates")
    points = [tuple(integer(v, 0, 5) for v in p) for p in raw]
    require(len(set(points)) == 6, "points must be distinct")
    score = min(distance2(a, b) for a, b in itertools.combinations(points, 2))
    require(integer(evidence["min_distance_squared"], 0, 50) == score, "incorrect distance")
    return {"objective": score, "baseline": 4, "improvement": score - 4,
            "optimality_checked": False}


def determinant3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def design_score(xs):
    return determinant3([[sum(x**(i + j) for x in xs) for j in range(3)] for i in range(3)])


def check_design(evidence):
    raw = evidence["xs"]
    require(type(raw) is list and len(raw) == 6, "need six measurements")
    xs = [integer(v, -3, 3) for v in raw]
    score = design_score(xs)
    require(integer(evidence["determinant"], 0, 10**9) == score, "incorrect determinant")
    optimum = max(design_score(x) for x in itertools.combinations_with_replacement(range(-3, 4), 6))
    baseline = design_score([-3, -2, -1, 1, 2, 3])
    return {"objective": score, "baseline": baseline, "improvement": score - baseline,
            "finite_optimum": optimum, "gap": optimum - score,
            "participant_optimality_argument_checked": False}


CHECKERS = {"cycle-count": check_cycle, "lattice-area": check_lattice,
            "tree-collision": check_trees, "moment-tail": check_moments,
            "grid-packing": check_packing, "quadratic-design": check_design}


def validate_schema(case, result):
    require(type(result) is dict, "result must be an object")
    require(result.get("case_id") == case, "case_id mismatch")
    require(result.get("status") in STATUSES, "invalid status")
    require(type(result.get("claim")) is str and result["claim"].strip(), "missing claim")
    require(type(result.get("evidence")) is dict, "evidence must be an object")
    for key in ("limitations", "reproduction"):
        require(type(result.get(key)) is list, key + " must be a list")
        require(all(type(v) is str and v.strip() for v in result[key]), "invalid " + key)
    require(result["reproduction"], "missing reproduction instructions")


def grade_result(case, result):
    output = {"case_id": case, "artifact_valid": False, "errors": [],
              "human_review_required": True, "computed": {}}
    try:
        validate_schema(case, result)
        output["declared_status"] = result["status"]
        if CASES[case] == "false-conjecture":
            output["declared_false_conjecture_acceptance"] = result["status"] == "proved"
        output["computed"] = CHECKERS[case](result["evidence"])
        output["artifact_valid"] = True
    except (ValueError, KeyError, TypeError, ZeroDivisionError, OverflowError) as error:
        output["errors"].append(str(error))
    return output


def grade_directory(case, directory):
    result = {"case_id": case, "artifact_valid": False, "errors": [],
              "human_review_required": True, "computed": {}}
    try:
        result = grade_result(case, load_json(directory / "result.json"))
        report = directory / "report.md"
        require(report.is_file() and not report.is_symlink() and report.stat().st_size,
                "missing or empty report.md")
        return result
    except (OSError, ValueError, RecursionError) as error:
        result["artifact_valid"] = False
        result["errors"].append(str(error))
        return result
