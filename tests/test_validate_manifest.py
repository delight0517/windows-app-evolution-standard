import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_manifest import validate


class ManifestValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "modules").mkdir()
        (self.root / "modules" / "core.py").write_text("# synthetic\n", encoding="utf-8")
        (self.root / "modules" / "theme.py").write_text("# synthetic\n", encoding="utf-8")
        self.manifest = {
            "api_version": 1,
            "watch_allowlist": ["theme-policy"],
            "modules": [
                {"id": "core", "path": "modules/core.py", "version": "1.0.0",
                 "api_version": 1, "dependencies": [], "reloadable": True,
                 "restart_required": False, "auto_watch": False,
                 "lifecycle": {"initialize": "initialize", "dispose": "shutdown"}},
                {"id": "theme-policy", "path": "modules/theme.py", "version": "1.0.0",
                 "api_version": 1, "dependencies": ["core"], "reloadable": True,
                 "restart_required": False, "auto_watch": True,
                 "lifecycle": {"initialize": "initialize", "dispose": "shutdown",
                               "snapshot_state": "snapshot_state", "restore_state": "restore_state"}}
            ]
        }

    def tearDown(self):
        self.temp.cleanup()

    def write_manifest(self):
        path = self.root / "module-manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        return path

    def test_valid_manifest(self):
        self.assertEqual(validate(self.root, self.write_manifest()), [])

    def test_path_traversal_and_watch_missing_restore_rejected(self):
        self.manifest["modules"][1]["path"] = "modules/../../outside.py"
        self.manifest["modules"][1]["lifecycle"].pop("restore_state")
        errors = validate(self.root, self.write_manifest())
        self.assertIn("theme-policy_path_not_canonical_relative_source", errors)
        self.assertIn("theme-policy_auto_watch_requires_snapshot_restore", errors)

    def test_stale_watch_allowlist_rejected(self):
        self.manifest["modules"][1]["auto_watch"] = False
        errors = validate(self.root, self.write_manifest())
        self.assertIn("watch_allowlist_module_not_opted_in:theme-policy", errors)

    def test_dependency_cycle_rejected(self):
        self.manifest["modules"][0]["dependencies"] = ["theme-policy"]
        errors = validate(self.root, self.write_manifest())
        self.assertTrue(any(error.startswith("dependency_cycle:") for error in errors))


if __name__ == "__main__":
    unittest.main()

