import hashlib
import logging
import re
from pathlib import Path

from lakemigrate._backend.delta import DEFAULT_HISTORY_TABLE, DeltaBackend
from lakemigrate._backend.protocol import Backend
from lakemigrate._errors import ChecksumMismatchError, DuplicateVersionError, InvalidFilenameError
from lakemigrate._migration import Migration

logger = logging.getLogger(__name__)

_PATTERN = re.compile(r"^(\d{3})__(.+)\.sql$")


def discover_migrations(directory: Path) -> list[Migration]:
    """Load and validate all SQL migration files in *directory*.

    Scans for ``.sql`` files, enforces the ``NNN__description.sql`` naming
    convention, rejects duplicate version numbers, and returns migrations
    sorted by version ascending.

    Args:
        directory: Directory to scan for ``.sql`` migration files.

    Returns:
        Migration objects sorted by version number, ascending.

    Raises:
        InvalidFilenameError: A file does not match the expected naming convention.
        DuplicateVersionError: Two files share the same version number.
    """
    migrations: list[Migration] = []
    seen: set[int] = set()

    for path in directory.iterdir():
        if path.suffix != ".sql":
            continue
        match = _PATTERN.match(path.name)
        if not match:
            raise InvalidFilenameError(
                f"migration file does not match naming convention 001__description.sql: {path.name}"
            )
        version = int(match.group(1))
        if version in seen:
            raise DuplicateVersionError(f"duplicate migration version: {version}")
        seen.add(version)
        raw = path.read_bytes()
        migrations.append(
            Migration(
                version=version,
                description=match.group(2),
                sql=raw.decode("utf-8"),
                checksum=hashlib.sha256(raw).hexdigest(),
            )
        )

    return sorted(migrations, key=lambda m: m.version)


def run_migrations(backend: Backend, migrations: list[Migration]) -> None:
    """Apply pending migrations through *backend*, validating applied ones first.

    Verifies checksums for all previously applied migrations before applying
    any new ones. Applies pending migrations in version order, recording each
    to the history table immediately after execution.

    Args:
        backend: Storage backend that executes SQL and tracks migration history.
        migrations: Ordered list of migrations to process, typically sourced
            from :func:`discover_migrations`.

    Raises:
        ChecksumMismatchError: A previously applied migration file has been modified.
    """
    applied = backend.get_applied_migrations()

    for migration in migrations:
        if migration.version not in applied:
            continue
        if migration.checksum != applied[migration.version]:
            raise ChecksumMismatchError(
                f"checksum mismatch for migration {migration.version}: "
                f"file has changed since it was applied"
            )

    for migration in migrations:
        if migration.version in applied:
            continue
        logger.info(f"applying migration {migration.version}: {migration.description}")
        backend.execute(migration.sql)
        backend.record_version(migration.version, migration.description, migration.checksum)


def migrate(migrations_dir: str | Path, history_table: str = DEFAULT_HISTORY_TABLE) -> None:
    """Apply all pending SQL migrations in *migrations_dir* to the Delta lakehouse.

    Discovers migration files matching the ``NNN__description.sql`` naming
    convention, validates checksums for previously applied migrations, and
    applies any that are new — in version order. A ``SparkSession`` must be
    active before calling this function.

    Args:
        migrations_dir: Path to the directory containing ``.sql`` migration files.
        history_table: Delta table used to record applied migrations.
            Defaults to ``default.lakemigrate_history``.

    Raises:
        InvalidFilenameError: A migration file does not match the
            ``NNN__description.sql`` naming convention.
        DuplicateVersionError: Two migration files share the same version number.
        ChecksumMismatchError: A previously applied migration file has been modified.
        RuntimeError: No active SparkSession was found.

    Example:
        >>> from lakemigrate import migrate
        >>> migrate("migrations/")
        >>> migrate("migrations/", history_table="mydb.schema_history")
    """
    logger.debug(f"migrating from {migrations_dir} using history table {history_table}")
    backend = DeltaBackend(history_table=history_table)
    migrations = discover_migrations(Path(migrations_dir))
    run_migrations(backend, migrations)
