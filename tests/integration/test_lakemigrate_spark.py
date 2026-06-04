from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from lakemigrate._discovering import discover_migrations
from lakemigrate._running import run_migrations

if TYPE_CHECKING:
    from lakemigrate._spark import SparkBackend

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "input_pre_applied, input_total, expected_versions",
    [
        (0, 2, {1, 2}),
        (2, 2, {1, 2}),
        (2, 3, {1, 2, 3}),
    ],
    ids=["fresh_run", "idempotent_run", "partial_run"],
)
def test_run_migrations(
    backend: SparkBackend,
    write_migration: Callable[[int, str, str], None],
    tmp_path: Path,
    input_pre_applied: int,
    input_total: int,
    expected_versions: set[int],
) -> None:
    for v in range(1, input_total + 1):
        write_migration(v, f"init_{v}", f"CREATE OR REPLACE TEMP VIEW mig_v{v} AS SELECT {v} AS id")
    all_migrations = discover_migrations(tmp_path)
    run_migrations(backend, all_migrations[:input_pre_applied])
    run_migrations(backend, all_migrations)
    assert set(backend.get_applied_migrations().keys()) == expected_versions


def test_checksum_mismatch(
    backend: SparkBackend,
    write_migration: Callable[[int, str, str], None],
    tmp_path: Path,
) -> None:
    write_migration(1, "init_a", "CREATE OR REPLACE TEMP VIEW mig_v1 AS SELECT 1 AS id")
    run_migrations(backend, discover_migrations(tmp_path))
    (tmp_path / "001__init_a.sql").write_text("-- modified")
    with pytest.raises(ValueError, match="checksum mismatch"):
        run_migrations(backend, discover_migrations(tmp_path))
