"""Offline tests for the private use-note recorder."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('record.py')
NOTE = {'task': 'demo', 'model': 'test-model', 'strategy': 'solo', 'outcome': 'helped',
        'evidence': 'observed', 'opinion': 'keep', 'elapsed_seconds': None, 'estimated_cost_usd': None}


class RecordTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name) / 'uses'

    def record(self, payload):
        return subprocess.run([sys.executable, str(SCRIPT), '--directory', str(self.dir)],
                              input=payload, capture_output=True, timeout=60)

    def test_saves_one_private_note(self):
        result = self.record(json.dumps(NOTE).encode())
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = Path(result.stdout.decode().strip())
        data = json.loads(saved.read_text(encoding='utf-8'))
        self.assertEqual((data['outcome'], data['schema']), ('helped', 'agent-boost-use.v1'))
        if os.name == 'posix':
            self.assertEqual(saved.stat().st_mode & 0o777, 0o600)

    def test_accepts_a_byte_order_mark(self):
        result = self.record(b'\xef\xbb\xbf' + json.dumps(NOTE).encode())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reads_a_utf8_file_without_losing_characters(self):
        opinion = 'keep café → \U0001F642'
        source = Path(self.temp.name) / 'note.json'
        source.write_text(json.dumps(dict(NOTE, opinion=opinion), ensure_ascii=False), encoding='utf-8-sig')
        result = subprocess.run([sys.executable, str(SCRIPT), '--directory', str(self.dir), '--file', str(source)],
                                capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = json.loads(Path(result.stdout.decode().strip()).read_text(encoding='utf-8'))
        self.assertEqual(saved['opinion'], opinion)

    def test_rejects_blank_fields_and_unknown_outcomes_without_writing(self):
        for bad in (dict(NOTE, opinion=' '), dict(NOTE, outcome='great')):
            result = self.record(json.dumps(bad).encode())
            self.assertEqual(result.returncode, 1)
            self.assertIn(b'record not saved', result.stderr)
        self.assertFalse(self.dir.exists())


if __name__ == '__main__':
    unittest.main()
