from lakemigrate._migration import Migration
from lakemigrate._protocol import Backend


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
