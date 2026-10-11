"""Provider-neutral consensus receipts; no model calls or external dependencies."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import topic


SOURCE = "Use the existing local folder. Preserve objections and missing votes.\n"
MEMBERS = ["codex", "claude", "gemini", "browser"]


class TopicTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "design.txt"
        self.source.write_text(SOURCE)
        self.folder = self.base / "decision"
        self.manifest = topic.start(self.folder, "Choose the smallest durable workflow", MEMBERS, [self.source])

    def proposal(self, participant="codex", text="One folder per decision"):
        return topic.submit(self.folder, {
            "kind": "proposal", "participant": participant, "provider": "any-provider",
            "model": "unknown", "input_digest": self.manifest["digest"],
            "proposal": text, "tradeoffs": ["You carry prompts between apps"],
        })

    def vote(self, proposal, participant, vote="approve", reason="Adequate for this goal"):
        return {
            "kind": "vote", "participant": participant, "provider": "browser-or-cli",
            "model": "unknown", "input_digest": self.manifest["digest"],
            "proposal_id": proposal["id"], "proposal_digest": proposal["digest"],
            "vote": vote, "reason": reason,
        }

    def view(self, proposal):
        return topic.status(self.folder, proposal["id"])["proposals"][0]

    def saved_votes(self):
        documents = [(path, path.read_text()) for path in self.folder.rglob("*.json")]
        return {str(path): text for path, text in documents if json.loads(text).get("kind") == "vote"}

    def test_start_freezes_goal_roster_and_source(self):
        self.assertEqual(self.manifest["schema"], 1)
        self.assertEqual(self.manifest["participants"], MEMBERS)
        self.assertEqual(json.loads((self.folder / "manifest.json").read_text()), self.manifest)
        self.assertTrue(self.manifest["sources"])
        self.source.write_text("Original has changed after starting.\n")
        prompt = topic.make_prompt(self.folder, "browser")
        self.assertIn(SOURCE.strip(), prompt)
        self.assertIn(self.manifest["digest"], prompt)
        self.assertEqual(topic.status(self.folder)["proposals"], [])
        before = (self.folder / "manifest.json").read_bytes()
        with self.assertRaises((ValueError, FileExistsError)):
            topic.start(self.folder, "Replace the goal", MEMBERS, [])
        self.assertEqual((self.folder / "manifest.json").read_bytes(), before)

    def test_unanimity_requires_explicit_author_vote_and_accepts_any_provider(self):
        proposal = self.proposal()
        for member in MEMBERS[1:]:
            topic.submit(self.folder, self.vote(proposal, member))
        view = self.view(proposal)
        self.assertEqual(view["status"], "incomplete")
        self.assertEqual(view["missing"], ["codex"])
        topic.submit(self.folder, self.vote(proposal, "codex"))
        view = self.view(proposal)
        self.assertEqual(view["status"], "agreed")
        self.assertCountEqual(view["approved"], MEMBERS)
        self.assertEqual(view["missing"], [])

    def test_dissent_remains_visible_alongside_missing_votes(self):
        proposal = self.proposal()
        topic.submit(self.folder, self.vote(proposal, "gemini", "object", "Missing recovery path"))
        view = self.view(proposal)
        self.assertEqual(view["status"], "disagreed")
        self.assertEqual(view["objections"], [{"participant": "gemini", "reason": "Missing recovery path"}])
        self.assertCountEqual(view["missing"], ["codex", "claude", "browser"])

    def test_each_proposal_has_fresh_votes_even_when_text_matches(self):
        first = self.proposal()
        for member in MEMBERS:
            topic.submit(self.folder, self.vote(first, member))
        second = self.proposal()
        self.assertNotEqual(first["id"], second["id"])
        views = {item["id"]: item for item in topic.status(self.folder)["proposals"]}
        self.assertEqual(views[first["id"]]["status"], "agreed")
        self.assertEqual(views[second["id"]]["status"], "incomplete")
        self.assertCountEqual(views[second["id"]]["missing"], MEMBERS)

    def test_wrong_context_proposal_or_actor_cannot_vote(self):
        proposal = self.proposal()
        valid = self.vote(proposal, "claude")
        changes = [{"input_digest": "wrong"}, {"proposal_digest": "wrong"},
                   {"proposal_id": "p-missing"}, {"participant": "uninvited"},
                   {"vote": "maybe"}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                topic.submit(self.folder, {**valid, **change})
        self.assertCountEqual(self.view(proposal)["missing"], MEMBERS)
        with self.assertRaises(ValueError):
            topic.make_prompt(self.folder, "uninvited")
        with self.assertRaises(ValueError):
            self.proposal("uninvited")

    def test_wrong_context_cannot_create_a_proposal(self):
        response = {"kind": "proposal", "participant": "codex", "provider": "openai",
                    "model": "unknown", "input_digest": "wrong", "proposal": "Bad context", "tradeoffs": []}
        with self.assertRaises(ValueError):
            topic.submit(self.folder, response)
        self.assertEqual(topic.status(self.folder)["proposals"], [])

    def test_edited_manifest_is_detected_before_reading_or_writing(self):
        changed = {**self.manifest, "goal": "Sneak in a different goal"}
        (self.folder / "manifest.json").write_text(json.dumps(changed))
        for operation in [lambda: topic.status(self.folder),
                          lambda: topic.make_prompt(self.folder, "codex"), self.proposal]:
            with self.assertRaises(ValueError):
                operation()

    def test_edited_snapshot_is_detected_on_every_read(self):
        snapshots = [path for path in self.folder.rglob("*") if path.is_file() and path.read_text() == SOURCE]
        self.assertEqual(len(snapshots), 1)
        snapshots[0].write_text("Silently changed evidence.\n")
        for operation in [lambda: topic.status(self.folder),
                          lambda: topic.make_prompt(self.folder, "codex"), self.proposal]:
            with self.assertRaises(ValueError):
                operation()

    def test_vote_retries_acknowledge_identical_input_without_overwriting(self):
        proposal = self.proposal()
        vote = self.vote(proposal, "claude")
        topic.submit(self.folder, vote)
        before = self.saved_votes()
        self.assertEqual(len(before), 1)
        topic.submit(self.folder, dict(vote))
        self.assertEqual(self.saved_votes(), before)
        with self.assertRaises(ValueError):
            topic.submit(self.folder, {**vote, "vote": "object", "reason": "Changed my mind"})
        self.assertEqual(self.saved_votes(), before)

    def test_conflicting_parallel_votes_keep_exactly_one_immutable_winner(self):
        proposal = self.proposal()
        candidates = [self.vote(proposal, "claude"), self.vote(proposal, "claude", "object", "Needs recovery")]
        worker = """import json, sys
from pathlib import Path
import topic
print('ready', flush=True)
response = json.loads(sys.stdin.readline())
try:
    topic.submit(Path(sys.argv[1]), response)
    print('saved')
except ValueError:
    print('rejected')
"""
        children = [subprocess.Popen([sys.executable, "-B", "-c", worker, str(self.folder)],
                    cwd=Path(topic.__file__).parent, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True) for _ in candidates]
        try:
            for child in children:
                self.assertEqual(child.stdout.readline().strip(), "ready")
            for child, candidate in zip(children, candidates):
                child.stdin.write(json.dumps(candidate) + "\n")
                child.stdin.flush()
            output = [child.communicate(timeout=5) for child in children]
            self.assertEqual([child.returncode for child in children], [0, 0], output)
            results = [stdout.strip() for stdout, _ in output]
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=5)
        self.assertCountEqual(results, ["saved", "rejected"])
        saved = self.saved_votes()
        self.assertEqual(len(saved), 1)
        record = json.loads(next(iter(saved.values())))
        winner = next(vote for vote in candidates if vote["reason"] == record["reason"])
        topic.submit(self.folder, winner)
        self.assertEqual(self.saved_votes(), saved)

    def test_prompts_target_one_proposal_and_require_selection_for_multiple(self):
        first = self.proposal()
        prompt = topic.make_prompt(self.folder, "browser")
        self.assertIn(first["id"], prompt)
        self.assertIn(first["digest"], prompt)
        self.assertIn(SOURCE.strip(), prompt)
        second = self.proposal(text="An alternative folder layout")
        with self.assertRaises(ValueError):
            topic.make_prompt(self.folder, "browser")
        prompt = topic.make_prompt(self.folder, "browser", second["id"])
        self.assertIn(second["id"], prompt)
        self.assertIn(second["proposal"], prompt)

    def test_revision_prompt_retains_objection_and_creates_fresh_vote_roster(self):
        first = self.proposal()
        topic.submit(self.folder, self.vote(first, "claude", "object", "Needs recovery"))
        prompt = topic.make_prompt(self.folder, "codex", first["id"], revise=True)
        packet_text, template_text = prompt.split("Packet:\n", 1)[1].split("\n\nReply template:\n", 1)
        packet, template = json.loads(packet_text), json.loads(template_text)
        self.assertEqual(template["kind"], "proposal")
        self.assertEqual(packet["proposals"][0]["objections"],
                         [{"participant": "claude", "reason": "Needs recovery"}])
        revised = topic.submit(self.folder, {**template, "provider": "openai", "model": "unknown",
                               "proposal": "One folder with recoverable replies", "tradeoffs": ["Extra storage"]})
        self.assertNotEqual(first["id"], revised["id"])
        self.assertCountEqual(self.view(revised)["missing"], MEMBERS)
        self.assertEqual(self.view(revised)["status"], "incomplete")
        rendered = topic.render(topic.status(self.folder))
        self.assertIn(first["tradeoffs"][0], rendered)
        self.assertIn("Extra storage", rendered)


if __name__ == "__main__":
    unittest.main()
