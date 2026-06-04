from pathlib import Path

from lakemigrate._delta import DEFAULT_HISTORY_TABLE, DeltaBackend
from lakemigrate._discovering import discover_migrations
from lakemigrate._running import run_migrations


def migrate(migrations_dir: str | Path, history_table: str = DEFAULT_HISTORY_TABLE) -> None:
    backend = DeltaBackend(history_table=history_table)
    migrations = discover_migrations(Path(migrations_dir))
    run_migrations(backend, migrations)
