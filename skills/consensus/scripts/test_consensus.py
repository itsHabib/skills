"""Concrete failure checks; no model calls or third-party dependencies."""
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import consensus


ANSWER = {"recommendation": "Use one script", "reason": "Few moving parts", "objections": []}
PROPOSAL = {"proposal": "Use one script", "tradeoffs": ["Providers can fail"]}
APPROVE = {"vote": "approve", "reason": "Adequate for the workload"}


def ok(value):
    return {"ok": True, "value": value}


def codex_stream(text, terminal="turn.completed"):
    events = [{"type": "item.completed", "item": {"id": "1", "type": "agent_message", "text": text}}]
    events.append({"type": terminal, "error": {"message": "Provider unavailable"}})
    return "\n".join(json.dumps(event) for event in events)


class ConsensusTests(unittest.TestCase):
    def tearDown(self):
        consensus.CANCELLED.clear()

    def test_invalid_payload_cannot_become_an_answer_or_vote(self):
        invalid = [(None, "answer"), ({**ANSWER, "recommendation": " "}, "answer"),
                   ({**ANSWER, "objections": "none"}, "answer"),
                   ({**ANSWER, "objections": [7]}, "answer"),
                   ({"proposal": "", "tradeoffs": []}, "proposal"),
                   ({"vote": "yes", "reason": "Agreed"}, "vote"),
                   ({"vote": "approve", "reason": ""}, "vote")]
        for value, phase in invalid:
            with self.subTest(value=value, phase=phase), self.assertRaises(ValueError):
                consensus.validate_payload(value, phase)

    def test_all_members_must_finish_and_approve_the_same_proposal(self):
        members = ["claude", "codex"]
        answers = {member: ok(ANSWER) for member in members}
        votes = {member: ok(APPROVE) for member in members}
        self.assertEqual(consensus.status_for(members, answers, ok(PROPOSAL), votes), "agreed")
        votes["codex"] = ok({"vote": "object", "reason": "Requires durable recovery"})
        self.assertEqual(consensus.status_for(members, answers, ok(PROPOSAL), votes), "disagreed")
        for broken_answers, proposal, broken_votes in [
            ({"claude": ok(ANSWER)}, ok(PROPOSAL), votes),
            (answers, {"ok": False, "error": "Timed out"}, votes),
            (answers, ok(PROPOSAL), {"claude": ok(APPROVE)}),
            (answers, ok(PROPOSAL), {**votes, "codex": {"ok": False, "error": "Failed"}}),
        ]:
            self.assertEqual(consensus.status_for(members, broken_answers, proposal, broken_votes), "incomplete")

    def test_provider_reports_cannot_hide_failures_or_missing_completion(self):
        failures = [("claude", json.dumps({"type": "result", "subtype": "success",
                                           "is_error": True, "result": json.dumps(ANSWER)})),
                    ("claude", json.dumps({"type": "result", "subtype": "error_max_turns",
                                           "is_error": False, "result": json.dumps(ANSWER)})),
                    ("claude", ""), ("claude", "not json"),
                    ("codex", codex_stream(json.dumps(ANSWER), "turn.failed")),
                    ("codex", json.dumps({"type": "error", "message": "Unauthorized"})),
                    ("codex", codex_stream(json.dumps(ANSWER)).splitlines()[0]),
                    ("codex", json.dumps({"type": "turn.completed"})),
                    ("codex", codex_stream(""))]
        for provider, output in failures:
            with self.subTest(provider=provider, output=output), self.assertRaises(ValueError):
                consensus.parse_response(provider, output)
        claude = json.dumps({"type": "result", "subtype": "success", "is_error": False,
                             "result": json.dumps(ANSWER)})
        self.assertEqual(consensus.parse_response("claude", claude), json.dumps(ANSWER))
        self.assertEqual(consensus.parse_response("codex", codex_stream(json.dumps(ANSWER))), json.dumps(ANSWER))

    def test_success_cache_reuses_only_the_same_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            response = {"ok": True, "text": json.dumps(ANSWER)}
            with patch.object(consensus, "call_model", return_value=response) as call:
                first = consensus.run_step("claude", "answer", "original", 2, run_dir)
                again = consensus.run_step("claude", "answer", "original", 2, run_dir)
                self.assertTrue(first["ok"])
                self.assertEqual(again["value"], ANSWER)
                self.assertEqual(call.call_count, 1)
                consensus.run_step("claude", "answer", "changed context", 2, run_dir)
                self.assertEqual(call.call_count, 2)

    def test_command_changes_invalidate_cache_and_empty_models_are_rejected(self):
        with self.assertRaises(ValueError):
            consensus.invocation("claude:")
        with tempfile.TemporaryDirectory() as directory:
            response = {"ok": True, "text": json.dumps(ANSWER)}
            with patch.object(consensus, "call_model", return_value=response) as call:
                with patch.object(consensus, "invocation", return_value=["claude", "old"]):
                    consensus.run_step("claude", "answer", "question", 2, Path(directory))
                with patch.object(consensus, "invocation", return_value=["claude", "new"]):
                    consensus.run_step("claude", "answer", "question", 2, Path(directory))
                self.assertEqual(call.call_count, 2)

    def test_failed_and_malformed_answers_retry_on_resume(self):
        for failed in [{"ok": False, "error": "Provider unavailable", "text": ""},
                       {"ok": True, "text": ""}, {"ok": True, "text": "not json"},
                       {"ok": True, "text": json.dumps({"recommendation": "Incomplete"})}]:
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as directory:
                good = {"ok": True, "text": json.dumps(ANSWER)}
                with patch.object(consensus, "call_model", side_effect=[failed, good]) as call:
                    result = consensus.run_step("codex", "answer", "question", 2, Path(directory))
                    self.assertFalse(result["ok"])
                    retried = consensus.run_step("codex", "answer", "question", 2, Path(directory))
                    self.assertTrue(retried["ok"])
                    self.assertEqual(call.call_count, 2)

    def test_resume_refuses_a_run_locked_by_another_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            with (Path(directory) / ".lock").open("w") as lock:
                consensus.fcntl.flock(lock, consensus.fcntl.LOCK_EX | consensus.fcntl.LOCK_NB)
                original_umask = os.umask(0o077)
                try:
                    with patch.object(sys, "argv", ["consensus.py", "--resume", directory]):
                        with patch.object(consensus.signal, "signal"), patch.object(consensus, "conduct") as conduct:
                            with self.assertRaises(SystemExit) as refused:
                                consensus.main()
                            self.assertEqual(refused.exception.code, 2)
                            conduct.assert_not_called()
                finally:
                    os.umask(original_umask)

    @unittest.skipUnless(os.name == "posix", "Process group semantics require POSIX")
    def test_timeout_stops_descendants_that_inherit_output_pipes(self):
        with tempfile.TemporaryDirectory() as directory:
            workdir = Path(directory)
            marker, pidfile = workdir / "escaped", workdir / "child.pid"
            child = "import pathlib,time; time.sleep(0.8); pathlib.Path('escaped').write_text('alive'); time.sleep(10)"
            parent = ("import pathlib,subprocess,sys,time; "
                      f"p=subprocess.Popen([sys.executable,'-c',{child!r}]); "
                      "pathlib.Path('child.pid').write_text(str(p.pid)); time.sleep(10)")
            started = time.monotonic()
            try:
                with patch.object(consensus, "invocation", return_value=[sys.executable, "-c", parent]):
                    result = consensus.call_model("codex", "question", 0.3, workdir)
                self.assertFalse(result["ok"])
                self.assertLess(time.monotonic() - started, 2)
                self.assertTrue(pidfile.exists(), "Fixture must have started a descendant")
                time.sleep(0.8)
                self.assertFalse(marker.exists(), "Descendant survived the timeout")
            finally:
                if pidfile.exists():
                    try:
                        os.kill(int(pidfile.read_text()), signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    @unittest.skipUnless(os.name == "posix", "Process group semantics require POSIX")
    def test_interrupt_during_spawn_kills_child_and_prevents_further_launches(self):
        real_popen, children, results = consensus.subprocess.Popen, [], []

        def launch(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            children.append(process)
            consensus.interrupt(signal.SIGINT, None)
            return process

        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, "-c", "import time; time.sleep(10)"]
            worker = threading.Thread(target=lambda: results.append(
                consensus.call_model("codex", "question", 2, directory)), daemon=True)
            try:
                with patch.object(consensus, "invocation", return_value=command):
                    with patch.object(consensus.subprocess, "Popen", side_effect=launch) as spawn:
                        worker.start()
                        worker.join(2)
                        self.assertFalse(worker.is_alive(), "Interrupt deadlocked inside process launch")
                        self.assertFalse(results[0]["ok"])
                        self.assertFalse(consensus.call_model("codex", "again", 2, directory)["ok"])
                        self.assertEqual(spawn.call_count, 1)
                self.assertTrue(children)
                self.assertIsNotNone(children[0].poll(), "Interrupted process is still alive")
                self.assertFalse(consensus.ACTIVE)
            finally:
                for process in children:
                    consensus.stop_process(process)
                    process.wait(timeout=2)


if __name__ == "__main__":
    unittest.main()
