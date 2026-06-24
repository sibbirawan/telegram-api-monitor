import unittest
import subprocess
import sys

class MonitorTests(unittest.TestCase):
    def test_selftest_runs(self):
        # Run monitor.py --test and expect exit code 0
        result = subprocess.run([sys.executable, 'monitor.py', '--test'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('All tests passed.', result.stdout)

if __name__ == '__main__':
    unittest.main()
