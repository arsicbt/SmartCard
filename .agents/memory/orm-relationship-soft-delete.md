---
name: ORM relationships bypass DBStorage soft-delete filter
description: SQLAlchemy relationships load soft-deleted rows; serialization must filter manually
---

# Relationships ignore the soft-delete convention

`DBStorage` (`get`/`all`/`filter_by`/`count`) excludes soft-deleted rows by
default with `deleted_at IS NULL`. **SQLAlchemy relationships do NOT** — accessing
`question.answers` or `theme.questions` loads every row, including soft-deleted.

**Why:** This project soft-deletes by setting `deleted_at`. Any code that reads
children through a relationship (e.g. enriched `to_dict()`) will silently include
deleted children, contradicting every repository query.

**How to apply:** When serializing or iterating a relationship for output, filter
`[x for x in rel if x.deleted_at is None]` to stay consistent with DBStorage.
This is exactly why `Question.to_dict()` / `Theme.to_dict()` filter manually.
