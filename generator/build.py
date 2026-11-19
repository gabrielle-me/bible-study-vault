"""Build a distributable, updateable Obsidian starter vault."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_NAME = ".bible-vault-manifest.json"
STATE_NAME = ".bible-vault-state.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_release(output_dir: Path, version: str, books: list[dict]) -> Path:
    updater = PROJECT_ROOT / "updater" / "update_vault.py"
    shutil.copy2(updater, output_dir / "update_vault.py")

    relative_paths = [
        Path("README.md"),
        Path("MOCs/Books MOC.md"),
        Path("MOCs/Themes MOC.md"),
        Path("MOCs/Characters MOC.md"),
        Path("MOCs/Places MOC.md"),
        Path("MOCs/Events MOC.md"),
    ]
    try:
        from .loaders import load_seed
    except ImportError:
        from loaders import load_seed

    for book in books:
        testament = book["testament"]
        title = book["title"]
        relative_paths.append(Path(testament) / title / f"{title}.md")
        seed = load_seed(title)
        relative_paths.extend(
            Path(testament) / title / f"{title} {chapter}.md"
            for chapter in range(1, seed["chapters"] + 1)
        )
    relative_paths.append(Path("update_vault.py"))
    managed_files = [output_dir / path for path in relative_paths]
    missing = [path for path in managed_files if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Cannot package an incomplete starter vault: "
            + ", ".join(str(path) for path in missing)
        )
    hashes = {
        path.relative_to(output_dir).as_posix(): _sha256(path)
        for path in managed_files
    }
    manifest = {"version": version, "files": hashes}
    (output_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / STATE_NAME).write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    archive_path = output_dir.parent / "starter-vault.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for relative_path in sorted(hashes):
            archive.write(output_dir / relative_path, relative_path)
        archive.write(output_dir / MANIFEST_NAME, MANIFEST_NAME)
        archive.write(output_dir / STATE_NAME, STATE_NAME)
    print(f"Release archive created at {archive_path}")
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="dist/starter-vault",
        help="Generated vault directory (default: dist/starter-vault)",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Also create dist/starter-vault.zip for a GitHub Release",
    )
    parser.add_argument(
        "--version",
        default="development",
        help="Release tag to embed in the manifest (for example v0.2.0)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output).expanduser().resolve()
    os.environ["BIBLE_VAULT_OUTPUT"] = str(output_dir)

    try:
        from .builders import build_starter_vault
    except ImportError:
        from builders import build_starter_vault

    books = build_starter_vault()
    if args.zip:
        package_release(output_dir, args.version, books)


if __name__ == "__main__":
    main()