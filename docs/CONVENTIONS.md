# Bible Study Vault – Project Conventions

This document defines the conventions used throughout the project. Every data file, generator, and contribution should follow these rules.

---

# 1. General Philosophy

The repository follows a **data-first architecture**.

The generator should contain as little biblical knowledge as possible. Instead, all biblical information is stored in structured JSON files.

Python is responsible for:

* reading data
* validating data
* generating Markdown

The JSON files are responsible for:

* biblical metadata
* narrative structure
* theological themes
* translations
* ontology

---

# 2. Folder Responsibilities

## `data/books`

Book metadata only.

Contains information that describes the book itself.

Examples:

* title
* author
* testament
* chapter count
* summary
* major themes
* major people
* major places
* key events

Do **not** store chapter-specific information here.

---

## `data/seeds`

Narrative anchors.

Defines:

* people
* places
* narrative events

Seeds describe **what happens** in a chapter.

---

## `data/rules`

Theological overlays.

Defines:

* themes
* theological events
* future cross-reference suggestions

Rules describe **what a passage is about**, not who appears in it.

---

## `data/ontology`

Global knowledge base.

Each entity exists exactly once.

Examples:

* people
* places
* themes
* events

Ontology files should never contain duplicated information.

---

## `data/locales`

Translations.

Contains language-specific display names.

The generator uses these files to render:

* English
* German
* Bilingual

---

# 3. Book IDs

Every biblical book has exactly one canonical ID.

Examples:

```
GEN
EXO
LEV
NUM
DEU
JOS
...
MAT
MRK
LUK
JHN
ACT
ROM
REV
```

Book IDs are used internally everywhere.

Never reference books by name.

Correct:

```json
{
    "book": "GEN"
}
```

Incorrect:

```json
{
    "book": "Genesis"
}
```

---

# 4. File Naming

Repository filenames remain human-readable.

Examples:

```
genesis.json

genesis_seed.json

genesis_rules.json
```

Do **not** rename files to `GEN.json`.

The ID belongs inside the file.

---

# 5. Ontology IDs

Ontology entities use lowercase snake_case.

Examples:

```
creation

call_of_abraham

tower_of_babel

mount_sinai

red_sea

abraham

holy_spirit
```

These IDs never change.

---

# 6. Translation Strategy

The project stores IDs, not translated text.

Example:

Instead of

```
Creation - Schöpfung
```

store

```
creation
```

The generator resolves the ID using the locale files.

---

# 7. People

Person names are **never translated**.

Examples:

```
Paul
Peter
Moses
Abraham
Mary
```

The ontology uses lowercase IDs.

```
abraham

moses

paul
```

The display name remains unchanged.

---

# 8. Places

Place names are also stored as canonical names.

Examples:

```
Egypt

Jerusalem

Bethlehem

Canaan
```

The ontology uses snake_case IDs.

```
mount_sinai

red_sea

garden_of_eden
```

---

# 9. Themes and Events

Themes and events always use ontology IDs.

Correct:

```json
{
    "themes": [
        "faith",
        "covenant"
    ]
}
```

Incorrect:

```json
{
    "themes": [
        "Faith - Glaube"
    ]
}
```

---

# 10. No Duplicate Data

Every fact should have exactly one source of truth.

Examples:

Book title

→ `books`

Chapter count

→ `books`

Narrative flow

→ `seeds`

Theological themes

→ `rules`

Translations

→ `locales`

Entity definitions

→ `ontology`

If a value appears in multiple places, the architecture should be reconsidered.

---

# 11. Generator Philosophy

The generator should not contain biblical knowledge.

Its responsibility is limited to:

1. Load data
2. Validate data
3. Resolve translations
4. Apply rules
5. Generate Markdown

Adding a new biblical book should require **only** new JSON files, without modifying the generator.

---

# 12. Future Goals

The architecture is designed to support:

* all 66 books of the Bible
* multiple output languages
* different Bible translations
* public contributions
* automatic validation
* Obsidian graph generation
* reusable ontology for future tools
