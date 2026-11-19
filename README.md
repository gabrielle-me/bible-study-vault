# Bible Study Vault source project

This repository contains the source data and Python generator for the downloadable Obsidian starter vault. The generated release is separate from the source project: builds go to the Git-ignored `dist/starter-vault/` by default, not to the existing `vault/` folder.

## Build a starter

From the repository root, activate your environment and install the dependencies:

```bash
python3 -m venv .venv  # first time only
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Build the starter and its GitHub Release ZIP:

```bash
python -m generator.build --version v0.1.0 --zip
```

The generated vault is in `dist/starter-vault/`, and the release asset is `dist/starter-vault.zip`. Only books with book metadata, a seed, and rules are included. Generated notes are arranged under `OT/`, `NT/`, and `MOCs/`; MOCs index people, places, themes, and events without generating separate entity notes.

Create a GitHub Release with the same version and upload the ZIP:

```bash
gh release create v0.1.0 dist/starter-vault.zip \
  --title "Bible Study Vault v0.1.0" \
  --notes "Starter vault release"
```

Use a new version tag for each release. The release must include an asset named exactly `starter-vault.zip`; the command above uses that name.

## User updates

Users open the downloaded ZIP contents as an Obsidian vault. To update later, they run `python3 update_vault.py` from that vault. The updater downloads the latest GitHub Release, updates files that are still unchanged from the previous release, preserves edited and personal files, and saves conflicting upstream versions under `Updates/<release>/`. It never deletes vault files. If a vault has no previous release state (for example, an older hand-built vault), it treats every existing file as user-owned and only adds new paths or review copies.

`vault/` is the pre-existing working vault and may contain personal changes. The generator no longer writes there by default. Keep the starter build and any personalized Obsidian copy separate.

## Project folders

- `data/`: catalog, book metadata, seeds, rules, ontology, and translations.
- `generator/`: Python data loading, chapter assembly, and build entry point.
- `templates/`: Jinja templates for generated notes and MOCs.
- `updater/`: standalone updater bundled in each release ZIP.
- `docs/`: data format and project conventions.
