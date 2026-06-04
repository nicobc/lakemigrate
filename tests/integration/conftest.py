from __future__ import annotations

import uuid
from collections.abc import Callable, Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

    from lakemigrate._backend.delta import DeltaBackend


@pytest.fixture(scope="session")
def spark() -> Generator[SparkSession, None, None]:
    pytest.importorskip("pyspark")
    pytest.importorskip("delta")
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession as _SparkSession

    builder = (  # type: ignore[reportUnknownVariableType]
        _SparkSession.builder.master("local")  # type: ignore[reportUnknownMemberType]
        .appName("lakemigrate-integration-test")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )
    session = configure_spark_with_delta_pip(builder).getOrCreate()  # type: ignore[reportUnknownArgumentType,reportUnknownMemberType]
    yield session
    session.stop()


@pytest.fixture
def history_table(spark: SparkSession) -> Generator[str, None, None]:
    name = f"test_history_{uuid.uuid4().hex[:8]}"
    yield name
    spark.sql(f"DROP TABLE IF EXISTS {name}")  # type: ignore[reportUnknownMemberType]


@pytest.fixture
def backend(history_table: str) -> DeltaBackend:
    from lakemigrate._backend.delta import DeltaBackend as _DeltaBackend

    return _DeltaBackend(history_table=history_table)


@pytest.fixture
def write_migration(tmp_path: Path) -> Callable[[int, str, str], None]:
    def _write(version: int, description: str, sql: str) -> None:
        (tmp_path / f"{version:03d}__{description}.sql").write_text(sql)

    return _write
