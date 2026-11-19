import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from updater.update_vault import apply_update, _read_release_archive
import zipfile
import io


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class UpdaterTests(unittest.TestCase):
    def test_existing_vault_without_state_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            (vault / "OT").mkdir()
            (vault / "OT" / "Genesis.md").write_bytes(b"my Genesis notes")

            counts = apply_update(
                vault,
                "v1",
                {
                    "OT/Genesis.md": b"starter Genesis note",
                    "OT/Exodus.md": b"starter Exodus note",
                },
            )

            self.assertEqual((vault / "OT" / "Genesis.md").read_bytes(), b"my Genesis notes")
            self.assertEqual(
                (vault / "Updates" / "v1" / "OT" / "Genesis.md").read_bytes(),
                b"starter Genesis note",
            )
            self.assertEqual((vault / "OT" / "Exodus.md").read_bytes(), b"starter Exodus note")
            self.assertTrue((vault / ".bible-vault-state.json").is_file())
            self.assertEqual(counts, {"installed": 1, "updated": 0, "conflicts": 1, "preserved": 0})

    def test_updates_unchanged_files_and_preserves_user_content(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            (vault / "OT").mkdir()
            (vault / "OT" / "unchanged.md").write_bytes(b"old")
            (vault / "OT" / "edited.md").write_bytes(b"my notes")
            (vault / "OT" / "custom.md").write_bytes(b"personal")
            (vault / "personal.md").write_bytes(b"leave alone")
            state = {
                "version": "v1",
                "files": {
                    "OT/unchanged.md": digest(b"old"),
                    "OT/edited.md": digest(b"old edited"),
                    "OT/deleted.md": digest(b"removed by user"),
                },
            }
            (vault / ".bible-vault-state.json").write_text(json.dumps(state))

            counts = apply_update(
                vault,
                "v2",
                {
                    "OT/unchanged.md": b"new",
                    "OT/edited.md": b"upstream changed",
                    "OT/custom.md": b"upstream collides",
                    "OT/deleted.md": b"do not restore",
                    "OT/new.md": b"new note",
                },
            )

            self.assertEqual((vault / "OT" / "unchanged.md").read_bytes(), b"new")
            self.assertEqual((vault / "OT" / "edited.md").read_bytes(), b"my notes")
            self.assertEqual((vault / "OT" / "custom.md").read_bytes(), b"personal")
            self.assertEqual((vault / "OT" / "deleted.md").exists(), False)
            self.assertEqual((vault / "OT" / "new.md").read_bytes(), b"new note")
            self.assertEqual((vault / "personal.md").read_bytes(), b"leave alone")
            self.assertEqual(
                (vault / "Updates" / "v2" / "OT" / "edited.md").read_bytes(),
                b"upstream changed",
            )
            self.assertEqual(
                (vault / "Updates" / "v2" / "OT" / "custom.md").read_bytes(),
                b"upstream collides",
            )
            self.assertEqual(counts, {"installed": 1, "updated": 1, "conflicts": 2, "preserved": 1})

    def test_release_archive_checks_manifest_hashes(self):
        content = b"# starter\n"
        manifest = {
            "version": "v1",
            "files": {"README.md": digest(content)},
        }
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(".bible-vault-manifest.json", json.dumps(manifest))
            archive.writestr("README.md", content)

        version, files = _read_release_archive(buffer.getvalue())

        self.assertEqual(version, "v1")
        self.assertEqual(files, {"README.md": content})


if __name__ == "__main__":
    unittest.main()
