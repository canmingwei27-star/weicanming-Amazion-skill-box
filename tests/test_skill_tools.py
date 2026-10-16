from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


render = load_module("render_skill_catalog", ROOT / "scripts" / "render_skill_catalog.py")
sync = load_module("sync_skills", ROOT / "scripts" / "sync_skills.py")


class ManifestTests(unittest.TestCase):
    def test_generated_catalog_is_current(self):
        manifest = render.load_manifest()
        self.assertEqual(
            (ROOT / "amazon-skill-router" / "references" / "skill-catalog.md").read_text(encoding="utf-8"),
            render.render_catalog(manifest),
        )

    def test_duplicate_skill_names_are_rejected(self):
        manifest_path = ROOT / "skills-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["skills"].append(dict(manifest["skills"][0]))
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            (temp_root / "skills-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            # The renderer always reads from ROOT, so exercise the shared sync validation here.
        with self.assertRaisesRegex(RuntimeError, "Duplicate skill name"):
            sync.manifest_entries(manifest)

    def test_force_replaces_stale_files_and_keeps_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            target_root = root / "skills"
            source = repo / "skill库" / "测试" / "example-skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("new skill", encoding="utf-8")
            target = target_root / "example-skill"
            target.mkdir(parents=True)
            (target / "stale.md").write_text("old local file", encoding="utf-8")
            entry = {
                "name": "example-skill",
                "path": "skill库/测试/example-skill",
                "include": ["SKILL.md"],
            }

            status = sync.sync_skill(repo, entry, target_root, True, target_root / ".skill-backups")

            self.assertEqual(status, "SYNCED: example-skill")
            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "new skill")
            self.assertFalse((target / "stale.md").exists())
            backups = list((target_root / ".skill-backups").rglob("stale.md"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "old local file")

    def test_without_force_skips_existing_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            target_root = root / "skills"
            target = target_root / "example-skill"
            target.mkdir(parents=True)
            (target / "keep.txt").write_text("keep", encoding="utf-8")
            entry = {
                "name": "example-skill",
                "path": "skill库/测试/example-skill",
                "include": ["SKILL.md"],
            }
            self.assertTrue(sync.sync_skill(repo, entry, target_root, False, target_root / ".skill-backups").startswith("SKIP"))
            self.assertTrue((target / "keep.txt").exists())


if __name__ == "__main__":
    unittest.main()
