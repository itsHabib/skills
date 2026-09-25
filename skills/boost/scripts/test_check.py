"""Offline behavior tests for the host check recorder."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('boost_check', Path(__file__).with_name('check.py'))
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.source = self.repo / 'solver.py'
        self.source.write_bytes(b'# original\n')
        self.output = self.root / 'receipts'

    def run_check(self, source, **kwargs):
        return CHECK.run(self.repo, ['solver.py'], [sys.executable, '-c', source],
                         self.output, **kwargs)

    def test_snapshots_exact_input_and_outputs_and_preserves_history(self):
        handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
        out, result = self.run_check('import sys; print("answer"); print("diagnostic", file=sys.stderr)')
        self.assertEqual(handlers, {sig: signal.getsignal(sig) for sig in handlers})
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['exit_code'], 0)
        self.assertGreaterEqual(result['elapsed_seconds'], 0)
        self.assertFalse(result['sources_changed'])
        self.assertEqual((out / 'source/solver.py').read_bytes(), b'# original\n')
        self.assertEqual((out / 'stdout.log').read_text(), 'answer\n')
        self.assertEqual((out / 'stderr.log').read_text(), 'diagnostic\n')
        start = json.loads((out / 'started.json').read_text())
        self.assertEqual(start['sources_before']['solver.py']['sha256'],
                         hashlib.sha256(b'# original\n').hexdigest())
        saved = (out / 'result.json').read_bytes()
        other, _ = self.run_check('print("second")')
        self.assertNotEqual(out, other)
        self.assertEqual((out / 'result.json').read_bytes(), saved)
        with self.assertRaises(FileExistsError):
            CHECK.json_write(out / 'result.json', {})
        if os.name == 'posix':
            self.assertEqual(out.stat().st_mode & 0o777, 0o700)
            self.assertEqual((out / 'stdout.log').stat().st_mode & 0o777, 0o600)
            self.assertEqual((out / 'source/solver.py').stat().st_mode & 0o777, 0o600)

    def test_records_failure_and_changed_source(self):
        out, result = self.run_check('from pathlib import Path; Path("solver.py").write_text("changed"); raise SystemExit(7)')
        self.assertEqual(result['exit_code'], 7)
        self.assertTrue(result['sources_changed'])
        self.assertEqual((out / 'source/solver.py').read_text(), '# original\n')
        self.assertEqual(self.source.read_text(), 'changed')

    def test_records_deleted_source_and_launch_failure(self):
        _, result = self.run_check('from pathlib import Path; Path("solver.py").unlink()')
        self.assertTrue(result['sources_changed'])
        self.assertIn('error', result['sources_after']['solver.py'])
        self.source.write_text('restored')
        out, result = CHECK.run(self.repo, ['solver.py'], [str(self.root / 'absent-command')], self.output)
        self.assertEqual(result['status'], 'launch_error')
        self.assertIsNone(result['exit_code'])
        self.assertTrue((out / 'result.json').exists())

    def test_rejects_outside_source_before_running_command(self):
        outside = self.root / 'outside.txt'
        outside.write_text('outside')
        marker = self.repo / 'ran'
        command = [sys.executable, '-c', 'from pathlib import Path; Path("ran").touch()']
        for name in ['../outside.txt', str(outside), 'missing.py']:
            with self.subTest(name=name), self.assertRaises((ValueError, OSError)):
                CHECK.run(self.repo, [name], command, self.output)
        if hasattr(os, 'symlink'):
            (self.repo / 'link').symlink_to(outside)
            with self.assertRaises(ValueError):
                CHECK.run(self.repo, ['link'], command, self.output)
        self.assertFalse(marker.exists())
        self.assertFalse(self.output.exists())

    def test_timeout_is_recorded_with_logs(self):
        out, result = self.run_check('import time; print("started", flush=True); time.sleep(10)', timeout=.2)
        self.assertEqual(result['status'], 'timeout')
        self.assertIsNotNone(result['exit_code'])
        self.assertIn('started', (out / 'stdout.log').read_text())
        self.assertLess(result['elapsed_seconds'], 5)

    def test_rejects_windows_drive_and_root_qualified_sources(self):
        # Exercise Windows parsing on every CI host without touching another drive.
        for name in ['C:solver.py', r'\solver.py', r'C:\solver.py', r'\\server\share\solver.py']:
            with self.subTest(path=name), patch.object(CHECK, 'Path', PureWindowsPath):
                with self.assertRaises(ValueError):
                    CHECK.selected_files(self.repo, [name])

    @unittest.skipUnless(os.name == 'posix', 'POSIX process groups')
    def test_timeout_cleans_child_after_parent_exits_on_term(self):
        delayed = ('import signal,time,pathlib; signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                   'time.sleep(.8); pathlib.Path("escaped").write_text("late")')
        command = ('import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",' +
                   repr(delayed) + ']); time.sleep(10)')
        _, result = self.run_check(command, timeout=.3)
        self.assertEqual(result['status'], 'timeout')
        time.sleep(.7)
        self.assertFalse((self.repo / 'escaped').exists())

    def test_cli_preserves_return_code_and_command_arguments(self):
        run = subprocess.run([sys.executable, str(Path(CHECK.__file__)), '--cwd', str(self.repo),
                              '--file', 'solver.py', '--directory', str(self.output), '--',
                              sys.executable, '-c', 'import sys; print(sys.argv[1]); raise SystemExit(9)',
                              'literal space; $not_shell'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 9)
        out = Path(run.stdout.strip())
        self.assertEqual((out / 'stdout.log').read_text(), 'literal space; $not_shell\n')

    @unittest.skipUnless(os.name == 'posix', 'POSIX signals and process groups')
    def test_signal_records_interruption_cleans_group_and_restores_handlers(self):
        for sig in (signal.SIGTERM, signal.SIGINT):
            with self.subTest(signal=sig):
                self.check_signal_cleanup(sig)

    def check_signal_cleanup(self, sig):
        marker = self.repo / f'late-{sig}'
        ready = self.repo / f'ready-{sig}'
        restored = self.repo / f'restored-{sig}'
        child = ('import signal,time,pathlib; signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                 f'pathlib.Path({str(ready)!r}).touch(); time.sleep(.8); '
                 f'pathlib.Path({str(marker)!r}).touch()')
        command = ('import subprocess,sys,time; '
                   f'subprocess.Popen([sys.executable,"-c",{child!r}]); time.sleep(10)')
        wrapper = (
            'import importlib.util,signal,sys,pathlib; '
            f'spec=importlib.util.spec_from_file_location("check",{str(Path(CHECK.__file__))!r}); '
            'm=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); '
            'prior={s:signal.getsignal(s) for s in (signal.SIGTERM,signal.SIGINT)}; '
            f'out,result=m.run({str(self.repo)!r},["solver.py"],'
            f'[sys.executable,"-c",{command!r}],{str(self.output)!r}); '
            'assert prior=={s:signal.getsignal(s) for s in prior}; '
            f'pathlib.Path({str(restored)!r}).touch(); print(out); '
            'sys.exit(128+result["interruption_signal"])')
        process = subprocess.Popen([sys.executable, '-c', wrapper],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue(ready.exists(), 'check child did not start')
            process.send_signal(sig)
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 128 + sig, stderr)
            receipt = json.loads((Path(stdout.strip()) / 'result.json').read_text())
            self.assertEqual(receipt['status'], 'interrupted')
            self.assertEqual(receipt['interruption_signal'], sig)
            self.assertTrue(restored.exists())
            time.sleep(.85)
            self.assertFalse(marker.exists(), 'launched child survived recorder signal')
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()


if __name__ == '__main__':
    unittest.main()
