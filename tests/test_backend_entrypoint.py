import unittest
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[1]


class BackendEntrypointTest(unittest.TestCase):
    def test_backend_main_can_run_as_script_like_module(self):
        module_path = ROOT / "backend" / "app" / "main.py"
        result = runpy.run_path(str(module_path))
        self.assertIn("app", result)
        self.assertEqual(result["app"].title, "College Chatbot API")


if __name__ == "__main__":
    unittest.main()
