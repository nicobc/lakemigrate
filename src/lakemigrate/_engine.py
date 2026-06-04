import hashlib
import re
from pathlib import Path

from lakemigrate._backend.delta import DEFAULT_HISTORY_TABLE, DeltaBackend
from lakemigrate._backend.protocol import Backend
from lakemigrate._migration import Migration

_PATTERN = re.compile(r"^(\d+)__(.+)\.sql$")


def discover_migrations(directory: Path) -> list[Migration]:
    migrations: list[Migration] = []
    seen: set[int] = set()

    for path in directory.iterdir():
        if path.suffix != ".sql":
            continue
        match = _PATTERN.match(path.name)
        if not match:
            raise ValueError(
                f"migration file does not match naming convention NNN__description.sql: {path.name}"
            )
        version = int(match.group(1))
        if version in seen:
            raise ValueError(f"duplicate migration version: {version}")
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
            raise ValueError(
                f"checksum mismatch for migration {migration.version}: "
                f"file has changed since it was applied"
            )

    for migration in migrations:
        if migration.version in applied:
            continue
        backend.execute(migration.sql)
        backend.record_version(migration.version, migration.description, migration.checksum)


def migrate(migrations_dir: str | Path, history_table: str = DEFAULT_HISTORY_TABLE) -> None:
    backend = DeltaBackend(history_table=history_table)
    migrations = discover_migrations(Path(migrations_dir))
    run_migrations(backend, migrations)
