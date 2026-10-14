#!/usr/bin/env python3
"""Freeze local two-arm packets and check artifacts; never launch a model."""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from checks import CASES, ROOT, SMOKE, grade_directory, load_json, require

BASELINE = "4b4a3d987ec2a556581ffd55bfd9dfa5c9449838"
SKILL_PATH = "skills/boost"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


def snapshot_ref(repo, ref):
    commit = git(repo, "rev-parse", "--verify", ref + "^{commit}").decode().strip()
    listing = git(repo, "ls-tree", "-rz", commit, "--", SKILL_PATH).split(b"\0")
    files = {}
    for entry in filter(None, listing):
        mode_info, name = entry.split(b"\t", 1)
        require(mode_info.split()[0] in (b"100644", b"100755"), "nonregular skill file")
        relative = Path(name.decode()).relative_to(SKILL_PATH).as_posix()
        files[relative] = git(repo, "show", commit + ":" + name.decode())
    require("SKILL.md" in files, "snapshot has no SKILL.md")
    return files, {"kind": "git", "commit": commit, "path": SKILL_PATH}


def snapshot_directory(directory):
    directory = directory.resolve()
    require(directory.is_dir(), "revised directory is missing")
    files = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), "snapshot symlinks are not accepted")
        if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store":
            files[path.relative_to(directory).as_posix()] = path.read_bytes()
    require("SKILL.md" in files, "snapshot has no SKILL.md")
    return files, {"kind": "directory", "path": str(directory)}


def tree_files(directory):
    files = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), "source symlink is not accepted")
        if path.is_file() and "__pycache__" not in path.parts:
            files[path.relative_to(directory).as_posix()] = path.read_bytes()
    return files


def file_manifest(files):
    return {name: {"sha256": sha(data), "bytes": len(data)} for name, data in sorted(files.items())}


def select_cases(value):
    if value == "all":
        return list(CASES)
    if value == "smoke":
        return list(SMOKE)
    names = value.split(",")
    require(names and len(set(names)) == len(names), "duplicate or empty case selection")
    require(all(name in CASES for name in names), "unknown case selection")
    return names


def worker_prompt(names, tool_limit, seconds, retrieval):
    source_note = "No external retrieval is available."
    if retrieval:
        source_note = "The identical frozen sources/ directory is available to both conditions."
    return f"""Complete the independent investigations in this workspace, in this order:
{', '.join(names)}. Read FORMAT.md and each cases/NAME/REQUEST.md. Use the Boost
skill at boost/SKILL.md. Read its applicable references as needed.

You may read and write only this packet workspace. Use local shell and standard
library Python; no network, external skills, other repositories, session stores,
helpers, or delegation. {source_note}

The common limit is {tool_limit} tool invocations and {seconds} elapsed seconds,
including initial skill/task reads, exploration, code execution, and checking.
These are limits, not targets. Finish within them. Do not ask for confirmation.
Leave the requested artifacts even when incomplete. In your final response give
paths, commands actually run, known costs, and limitations. Do not remove failed
experiments. Keep all supplied inputs and the skill unchanged.
"""


def packet_files(names, skill, args, retrieval):
    files = {"FORMAT.md": (ROOT / "FORMAT.md").read_bytes()}
    files["WORKER.md"] = worker_prompt(names, args.tool_limit, args.seconds, bool(retrieval)).encode()
    files.update(("boost/" + name, data) for name, data in skill.items())
    files.update(("sources/" + name, data) for name, data in retrieval.items())
    for case in names:
        files.update((f"cases/{case}/" + name, data) for name, data in tree_files(ROOT / "cases" / case).items())
    return files


def materialize(directory, files):
    for name, data in files.items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def run_record():
    return {"state": "not_run", "started_at": None, "ended_at": None,
            "tool_calls": None, "input_tokens": None, "output_tokens": None,
            "skill_read_tokens": None, "elapsed_seconds": None,
            "model_actual": None, "effort_actual": None, "failure": None,
            "transcript_path": None, "budget_deviations": []}


def prepare(args):
    names = select_cases(args.cases)
    require(not args.out.exists(), "output already exists; keep prior runs immutable")
    require(not args.out.resolve().is_relative_to(ROOT), "output must be outside evaluator sources")
    require(args.tool_limit > 0 and args.seconds > 0, "budgets must be positive")
    original, original_source = snapshot_ref(args.repo, args.original_ref)
    if args.revised_ref:
        revised, revised_source = snapshot_ref(args.repo, args.revised_ref)
    if args.revised_dir:
        revised, revised_source = snapshot_directory(args.revised_dir)
    retrieval = {}
    if args.retrieval_dir:
        require(args.retrieval_dir.is_dir(), "retrieval directory is missing")
        retrieval = tree_files(args.retrieval_dir)
        require(retrieval, "retrieval pack is empty")
    coordinator = args.out / "coordinator"
    coordinator.mkdir(parents=True)
    sources = {"original": original_source, "revised": revised_source}
    manifest = {"schema": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
                "cases": names, "families": {name: CASES[name] for name in names},
                "model": args.model, "effort": args.effort, "tool_limit": args.tool_limit,
                "elapsed_seconds_limit": args.seconds, "pair_id": args.pair_id,
                "retrieval_stratum": "closed", "arms": {}}
    if retrieval:
        manifest["retrieval_stratum"] = "frozen-pack"
    for arm, skill in (("original", original), ("revised", revised)):
        files = packet_files(names, skill, args, retrieval)
        materialize(args.out / "packets" / arm, files)
        manifest["arms"][arm] = {"source": sources[arm], "files": file_manifest(files),
                                  "skill_bytes": sum(len(data) for data in skill.values())}
        write_json(coordinator / (arm + "-run.json"), run_record())
    evaluator = tree_files(ROOT)
    materialize(coordinator / "evaluator", evaluator)
    manifest["evaluator_files"] = file_manifest(evaluator)
    write_json(coordinator / "FREEZE.json", manifest)
    return {"run": str(args.out.resolve()), "cases": names,
            "freeze_sha256": sha((coordinator / "FREEZE.json").read_bytes()),
            "worker_packets": [str((args.out / "packets" / arm).resolve())
                               for arm in ("original", "revised")]}


def integrity_errors(directory, manifest):
    errors = []
    for name, identity in manifest.items():
        path = directory / name
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes()) != identity["sha256"]:
            errors.append("protected file changed or missing: " + name)
    return errors


def grade(args):
    freeze = load_json(args.run / "coordinator/FREEZE.json")
    packet = args.run / "packets" / args.arm
    integrity = integrity_errors(packet, freeze["arms"][args.arm]["files"])
    evaluator_errors = integrity_errors(ROOT, freeze["evaluator_files"])
    record = load_json(args.run / "coordinator" / (args.arm + "-run.json"))
    results = [grade_directory(case, packet / "cases" / case) for case in freeze["cases"]]
    return {"arm": args.arm, "pair_id": freeze["pair_id"], "run_record": record,
            "input_integrity_errors": integrity, "evaluator_integrity_errors": evaluator_errors,
            "results": results, "human_review_required": True,
            "artifact_checks_pass": not integrity and not evaluator_errors and
                                    all(result["artifact_valid"] for result in results)}


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--repo", type=Path, default=ROOT.parents[1])
    prepare_parser.add_argument("--original-ref", default=BASELINE)
    revised = prepare_parser.add_mutually_exclusive_group(required=True)
    revised.add_argument("--revised-dir", type=Path)
    revised.add_argument("--revised-ref")
    prepare_parser.add_argument("--out", type=Path, required=True)
    prepare_parser.add_argument("--cases", default="smoke")
    prepare_parser.add_argument("--model", required=True)
    prepare_parser.add_argument("--effort", required=True)
    prepare_parser.add_argument("--pair-id", required=True)
    prepare_parser.add_argument("--tool-limit", type=int, default=24)
    prepare_parser.add_argument("--seconds", type=int, default=600)
    prepare_parser.add_argument("--retrieval-dir", type=Path)
    grade_parser = commands.add_parser("grade")
    grade_parser.add_argument("--run", type=Path, required=True)
    grade_parser.add_argument("--arm", choices=("original", "revised"), required=True)
    return result


def main():
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            print(json.dumps(prepare(args), indent=2))
            return 0
        result = grade(args)
        print(json.dumps(result, indent=2))
        return int(not result["artifact_checks_pass"])
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
