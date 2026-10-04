import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from smoke_windows import run_package


class PackageSmokeTests(unittest.TestCase):
    def test_failed_process_preserves_native_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            report = directory / 'result.json'
            report.write_text(json.dumps({'ok': False, 'error': 'native failure'}), encoding='utf-8')
            with mock.patch('subprocess.run', return_value=subprocess.CompletedProcess([], 1)):
                evidence = run_package(directory / 'app.exe', directory / 'fixture.mp4', report)
            self.assertEqual(evidence, {'ok': False, 'error': 'native failure', 'exitCode': 1})

    def test_nonzero_exit_cannot_pass_with_a_success_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            report = directory / 'result.json'
            report.write_text('{"ok": true}', encoding='utf-8')
            with mock.patch('subprocess.run', return_value=subprocess.CompletedProcess([], 1)):
                evidence = run_package(directory / 'app.exe', directory / 'fixture.mp4', report)
            self.assertFalse(evidence['ok'])

    def test_timeout_produces_failure_evidence(self):
        directory = Path('unused')
        with mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('app.exe', 90)):
            evidence = run_package(directory / 'app.exe', directory / 'fixture.mp4', directory / 'result.json')
        self.assertFalse(evidence['ok'])
        self.assertIn('timed out', evidence['error'])


if __name__ == '__main__':
    unittest.main()
