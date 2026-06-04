# lakemigrate

[![PyPI](https://img.shields.io/pypi/v/lakemigrate)](https://pypi.org/project/lakemigrate/)
[![Python](https://img.shields.io/pypi/pyversions/lakemigrate)](https://pypi.org/project/lakemigrate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/nicobc/lakemigrate/actions/workflows/test.yml/badge.svg)](https://github.com/nicobc/lakemigrate/actions/workflows/test.yml)

Ordered SQL migrations with a version table for Delta lakehouse storage.

lakemigrate discovers SQL files in a directory, applies any that have not yet run — in version order — and records each in a Delta history table. Checksums guard against silent edits after a migration has been applied.

## Installation

**Managed Spark environment** (Databricks, EMR, GCP Dataproc — Spark is already present):

```bash
pip install lakemigrate
```

**Local development** (installs PySpark and delta-spark):

```bash
pip install "lakemigrate[spark]"
```

## Migration files

Name each file `NNN__description.sql` where `NNN` is a zero-padded three-digit version number:

```
migrations/
  001__create_events_table.sql
  002__add_user_id_column.sql
  003__backfill_legacy_data.sql
```

Files are applied in version order. Once applied, the file content is checksummed — modifying a file after it runs raises `ChecksumMismatchError`.

## CLI

```bash
# apply all pending migrations
lakemigrate migrate --migrations-dir migrations/

# custom history table
lakemigrate migrate --migrations-dir migrations/ --history-table mydb.schema_history
```

## Python API

```python
from lakemigrate import migrate

# uses default history table: default.lakemigrate_history
migrate("migrations/")

# custom history table
migrate("migrations/", history_table="mydb.schema_history")
```

A `SparkSession` must be active before calling `migrate`. The history table is created automatically on first run.

## Error handling

| Exception | When |
|-----------|------|
| `InvalidFilenameError` | A file does not match `NNN__description.sql` |
| `DuplicateVersionError` | Two files share the same version number |
| `ChecksumMismatchError` | An applied migration file has been modified |

All exceptions inherit from `LakeMigrateError`.

## Links

- [PyPI](https://pypi.org/project/lakemigrate/)
- [Source](https://github.com/nicobc/lakemigrate)
- [Issues](https://github.com/nicobc/lakemigrate/issues)
