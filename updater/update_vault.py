#!/usr/bin/env python3
"""Safely update a Bible Study Vault from the latest GitHub Release."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile


REPOSITORY = "gabrielle-me/bible-study-vault"
ASSET_NAME = "starter-vault.zip"
MANIFEST_NAME = ".bible-vault-manifest.json"
STATE_NAME = ".bible-vault-state.json"
MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str):
        raise ValueError(f"Release paths must be strings, got {type(value).__name__}.")
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or path.as_posix() != value
        or "\\" in value
        or ":" in value
        or any(part in ("", ".", "..") for part in path.parts)
        or not (value == "update_vault.py" or path.suffix.lower() == ".md")
    ):
        raise ValueError(f"Unsafe or unsupported release path: {value!r}")
    return path


def _safe_target(vault: Path, relative_path: str) -> Path:
    path = _validate_relative_path(relative_path)
    target = vault.joinpath(*path.parts)
    current = vault
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Refusing to update through symlink: {current}")
    if not target.resolve().is_relative_to(vault.resolve()):
        raise ValueError(f"Release path escapes the vault: {relative_path}")
    return target


def _read_state(vault: Path) -> dict:
    state_path = vault / STATE_NAME
    if state_path.is_symlink():
        raise ValueError(f"Refusing to read updater state through symlink: {state_path}")
    if not state_path.is_file():
        return {"version": "legacy", "files": {}}
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if (
        not isinstance(state, dict)
        or not isinstance(state.get("files"), dict)
        or not isinstance(state.get("version"), str)
    ):
        raise ValueError(f"{STATE_NAME} has an invalid format.")
    for name, digest in state["files"].items():
        _validate_relative_path(name)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Invalid file hash in {STATE_NAME}: {name}")
    return state


def apply_update(vault: Path, version: str, files: dict[str, bytes]) -> dict[str, int]:
    vault = vault.expanduser().resolve()
    if not vault.is_dir():
        raise ValueError(f"Vault folder does not exist: {vault}")

    state = _read_state(vault)
    previous_files = state["files"]
    planned: list[tuple[str, Path, bytes, bool]] = []
    counts = {"installed": 0, "updated": 0, "conflicts": 0, "preserved": 0}

    for name, content in files.items():
        _validate_relative_path(name)
        if not isinstance(content, bytes):
            raise ValueError(f"Invalid release content for {name}")

        target = _safe_target(vault, name)
        previous_hash = previous_files.get(name)
        incoming_hash = _sha256(content)

        if not target.exists():
            if previous_hash is None:
                planned.append((name, target, content, False))
                counts["installed"] += 1
            else:
                counts["preserved"] += 1
            continue

        if not target.is_file():
            raise ValueError(f"Expected a file at {target}")
        local_hash = _sha256(target.read_bytes())

        if local_hash == incoming_hash:
            continue
        if previous_hash is not None and local_hash == previous_hash:
            planned.append((name, target, content, False))
            counts["updated"] += 1
        elif previous_hash is None or incoming_hash != previous_hash:
            planned.append((name, target, content, True))
            counts["conflicts"] += 1

    safe_version = re.sub(r"[^A-Za-z0-9._-]+", "-", version).strip(".-") or "release"
    for name, target, content, conflict in planned:
        destination = target
        if conflict:
            relative = _validate_relative_path(name)
            destination = _safe_target(
                vault,
                f"Updates/{safe_version}/{relative.as_posix()}",
            )
            suffix = 2
            while destination.exists():
                if destination.is_file() and _sha256(destination.read_bytes()) == _sha256(content):
                    break
                relative_dest = PurePosixPath(destination.relative_to(vault).as_posix())
                candidate_name = (
                    f"{relative_dest.stem} ({suffix}){relative_dest.suffix}"
                )
                destination = _safe_target(
                    vault,
                    (relative_dest.parent / candidate_name).as_posix(),
                )
                suffix += 1
        if not destination.exists() or _sha256(destination.read_bytes()) != _sha256(content):
            destination.parent.mkdir(parents=True, exist_ok=True)
            _safe_target(vault, destination.relative_to(vault).as_posix())
            destination.write_bytes(content)

    new_state = {"version": version, "files": {name: _sha256(data) for name, data in files.items()}}
    state_path = vault / STATE_NAME
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=vault,
        delete=False,
    ) as handle:
        json.dump(new_state, handle, indent=2)
        handle.write("\n")
        temporary_path = Path(handle.name)
    os.replace(temporary_path, state_path)
    return counts


def _read_release_archive(archive_bytes: bytes) -> tuple[str, dict[str, bytes]]:
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError("Release ZIP contains duplicate paths.")
            if MANIFEST_NAME not in names:
                raise ValueError(f"Release ZIP is missing {MANIFEST_NAME}.")

            for info in archive.infolist():
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise ValueError(f"Release ZIP contains a symlink: {info.filename}")

            manifest = json.loads(archive.read(MANIFEST_NAME))
            if not isinstance(manifest, dict):
                raise ValueError("Release manifest has an invalid format.")
            version = manifest.get("version")
            hashes = manifest.get("files")
            if not isinstance(version, str) or not version or not isinstance(hashes, dict):
                raise ValueError("Release manifest has an invalid format.")

            files = {}
            for name, expected_hash in hashes.items():
                _validate_relative_path(name)
                if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                    raise ValueError(f"Invalid hash in release manifest: {name}")
                if name not in names:
                    raise ValueError(f"Release ZIP is missing {name}.")
                content = archive.read(name)
                if _sha256(content) != expected_hash:
                    raise ValueError(f"Hash mismatch for release file: {name}")
                files[name] = content
            return version, files
    except zipfile.BadZipFile as exc:
        raise ValueError("The downloaded release is not a valid ZIP file.") from exc


def _download(url: str, accept: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Bible-Study-Vault-Updater/1.0", "Accept": accept},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError("Download exceeds the 100 MB safety limit.")
    return data


def get_latest_release() -> tuple[str, dict[str, bytes]]:
    api_url = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
    release_data = json.loads(_download(api_url, "application/vnd.github+json"))
    if not isinstance(release_data, dict):
        raise ValueError("GitHub returned an invalid release response.")
    assets = release_data.get("assets", [])
    if not isinstance(assets, list):
        raise ValueError("GitHub returned an invalid release response.")
    asset = next(
        (
            item
            for item in assets
            if isinstance(item, dict) and item.get("name") == ASSET_NAME
        ),
        None,
    )
    if asset is None:
        raise ValueError(
            f"The latest GitHub Release does not contain {ASSET_NAME}."
        )
    download_url = asset.get("browser_download_url")
    if not isinstance(download_url, str):
        raise ValueError("The starter ZIP release asset has no download URL.")
    archive = _download(download_url, "application/octet-stream")
    return _read_release_archive(archive)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Path to the local Obsidian vault (default: this script's folder)",
    )
    args = parser.parse_args()

    try:
        state_path = args.vault.expanduser() / STATE_NAME
        if not state_path.exists():
            print(
                "No previous release state found. Existing files will be preserved; "
                "upstream versions of colliding files will be saved under Updates/."
            )
        version, files = get_latest_release()
        counts = apply_update(args.vault, version, files)
    except (
        OSError,
        urllib.error.URLError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
    ) as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1

    print(f"Updated to {version}.")
    print(
        f"Installed: {counts['installed']}; updated: {counts['updated']}; "
        f"customized files needing review: {counts['conflicts']}; "
        f"user-removed files preserved: {counts['preserved']}."
    )
    if counts["conflicts"]:
        print(f"Review upstream versions under {args.vault / 'Updates' / version}.")
    print("No files were deleted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
