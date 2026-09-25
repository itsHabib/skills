"""Offline tests for the use-note summary."""
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('report.py')
SPEC = importlib.util.spec_from_file_location('boost_report', SCRIPT)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def note(outcome, days_ago, strategy, opinion='Keep it. Second sentence.'):
    when = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {'task': f'{outcome} task', 'model': 'test-model', 'strategy': strategy, 'outcome': outcome,
            'evidence': 'observed', 'opinion': opinion, 'schema': 'agent-boost-use.v1', 'recorded_at': when.isoformat()}


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name) / 'uses'
        self.dir.mkdir()
        for index, value in enumerate([note('helped', 1, 'exact oracle'), note('hurt', 2, 'generic critic'),
                                       note('helped', 30, 'old boundary probe')]):
            self.put(f'{index}.json', value)
        (self.dir / 'broken.json').write_text('{not json')

    def put(self, name, value):
        (self.dir / name).write_text(json.dumps(value), encoding='utf-8')

    def run_main(self, *args):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = REPORT.main(['--directory', str(self.dir), *args])
        return code, out.getvalue()

    def assert_usage_error(self, *args):
        with self.assertRaises(SystemExit) as caught:
            self.run_main(*args)
        self.assertEqual(caught.exception.code, 2, args)

    def test_counts_skip_unreadable_and_sort_newest_first(self):
        notes, unreadable = REPORT.load(self.dir)
        self.assertEqual(unreadable, 1)
        self.assertEqual([n['strategy'] for n in notes], ['exact oracle', 'generic critic', 'old boundary probe'])
        self.assertEqual(REPORT.counts(notes), {'helped': 2, 'no_change': 0, 'hurt': 1, 'unclear': 0, 'other': 0})

    def test_since_filters_by_recorded_time(self):
        notes, _ = REPORT.load(self.dir, since_days=7)
        self.assertEqual(len(notes), 2)

    def test_brief_separates_what_helped_from_what_did_not(self):
        code, text = self.run_main('--brief')
        self.assertEqual(code, 0)
        self.assertIn('3 use notes, outcomes self-reported: 2 helped, 0 no_change, 1 hurt, 0 unclear', text)
        self.assertNotIn('other', text.splitlines()[0])
        helped, _, rest = text.partition('What did not help:')
        self.assertIn('exact oracle -> Keep it.', helped)
        self.assertNotIn('Second sentence', text)
        self.assertIn('generic critic', rest)

    def test_json_and_markdown_outputs(self):
        _, raw = self.run_main('--json', '--since', '7')
        data = json.loads(raw)
        self.assertEqual(data['counts']['helped'], 1)
        self.assertEqual(data['unreadable'], 1)
        _, text = self.run_main()
        self.assertIn('## All notes, newest first', text)
        self.assertIn('- **Strategy:** generic critic', text)

    def test_missing_directory_still_renders_valid_json(self):
        self.dir = self.dir / 'absent'
        code, raw = self.run_main('--json')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(raw)['counts'], {'helped': 0, 'no_change': 0, 'hurt': 0, 'unclear': 0, 'other': 0})

    def test_hand_edited_and_foreign_notes_never_crash(self):
        recent = datetime.now(timezone.utc) - timedelta(days=1)
        self.put('naive.json', dict(note('helped', 0, 'naive time'), recorded_at=recent.replace(tzinfo=None).isoformat()))
        self.put('zulu.json', dict(note('no_change', 0, 'zulu time'), recorded_at=recent.strftime('%Y-%m-%dT%H:%M:%SZ')))
        self.put('list-outcome.json', dict(note('helped', 0, 'odd outcome'), outcome=['helped']))
        self.put('caps.json', dict(note('no_change', 0, 'caps outcome'), outcome=' Helped '))
        self.put('array.json', [1, 2])
        self.put('number-time.json', dict(note('helped', 0, 'numeric time'), recorded_at=123))
        (self.dir / 'deep.json').write_text('[' * 100000 + ']' * 100000)
        notes, unreadable = REPORT.load(self.dir, since_days=7)
        self.assertEqual(unreadable, 4)
        self.assertTrue({'naive time', 'zulu time', 'odd outcome'} <= {n['strategy'] for n in notes})
        code, text = self.run_main('--brief', '--since', '7')
        self.assertEqual(code, 0)
        self.assertIn('zulu time', text)
        self.assertIn('3 helped, 1 no_change, 1 hurt, 0 unclear, 1 other', text)

    def test_notes_saved_with_a_byte_order_mark_are_read(self):
        (self.dir / 'bom.json').write_bytes(b'\xef\xbb\xbf' + json.dumps(note('helped', 0, 'bom save')).encode())
        notes, unreadable = REPORT.load(self.dir)
        self.assertIn('bom save', [n['strategy'] for n in notes])
        self.assertEqual(unreadable, 1)

    def test_sorts_by_time_not_by_text(self):
        self.put('utc.json', dict(note('helped', 0, 'utc ten'), recorded_at='2026-09-20T10:00:00+00:00'))
        self.put('plus5.json', dict(note('helped', 0, 'plus five'), recorded_at='2026-09-20T12:00:00+05:00'))
        order = [n['strategy'] for n in REPORT.load(self.dir)[0]]
        self.assertLess(order.index('utc ten'), order.index('plus five'))

    def test_since_rejects_non_positive_and_non_finite_days(self):
        for bad in ('0', '-1', 'nan', 'inf', 'soon'):
            self.assert_usage_error('--since', bad)
        code, _ = self.run_main('--since', '1e12')
        self.assertEqual(code, 0)

    def test_output_file_is_utf8(self):
        self.put('unicode.json', dict(note('helped', 0, 'arrows → and \U0001F642')))
        target = Path(self.temp.name) / 'feedback.md'
        self.assertEqual(self.run_main('--output', str(target)), (0, ''))
        self.assertIn('arrows → and \U0001F642', target.read_text(encoding='utf-8'))

    def test_narrow_console_encoding_does_not_crash(self):
        self.put('unicode.json', dict(note('helped', 0, 'emoji \U0001F642 strategy')))
        env = dict(os.environ, PYTHONIOENCODING='cp1252')
        result = subprocess.run([sys.executable, str(SCRIPT), '--directory', str(self.dir), '--brief'],
                                capture_output=True, env=env, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        self.assertIn(b'emoji ? strategy', result.stdout)


if __name__ == '__main__':
    unittest.main()
