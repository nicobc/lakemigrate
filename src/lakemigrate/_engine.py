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
    migrations: list[Migration] = []
    seen: set[int] = set()

    for path in directory.iterdir():
        if path.suffix != ".sql":
            continue
        match = _PATTERN.match(path.name)
        if not match:
            raise InvalidFilenameError(
                f"migration file does not match naming convention "
                f"001__description.sql: {path.name}"
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
    logger.debug(f"migrating from {migrations_dir} using history table {history_table}")
    backend = DeltaBackend(history_table=history_table)
    migrations = discover_migrations(Path(migrations_dir))
    run_migrations(backend, migrations)
