import logging
from typing import Literal

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

logger = logging.getLogger(__name__)

TableFormat = Literal["delta", "iceberg"]

_DEFAULT_VERSION_TABLE = "default.lakemigrate_history"
_DEFAULT_TABLE_FORMAT: TableFormat = "delta"

_RECORD_SCHEMA = StructType([
    StructField("version", IntegerType(), nullable=False),
    StructField("description", StringType(), nullable=False),
    StructField("checksum", StringType(), nullable=False),
])


class SparkBackend:
    def __init__(
        self,
        version_table: str = _DEFAULT_VERSION_TABLE,
        table_format: TableFormat = _DEFAULT_TABLE_FORMAT,
    ) -> None:
        session = SparkSession.getActiveSession()
        if session is None:
            raise RuntimeError("No active SparkSession — start one before using SparkBackend")
        self._session = session
        self._version_table = version_table
        self._table_format = table_format
        self._ensure_history_table()

    def _ensure_history_table(self) -> None:
        self._session.sql(  # type: ignore[reportUnknownMemberType]
            f"CREATE TABLE IF NOT EXISTS {self._version_table} "
            f"(version INT, description STRING, checksum STRING, applied_at TIMESTAMP) "
            f"USING {self._table_format}"
        )

    def execute(self, sql: str) -> None:
        self._session.sql(sql)  # type: ignore[reportUnknownMemberType]

    def get_applied_migrations(self) -> dict[int, str]:
        rows = (
            self._session.read.table(self._version_table)
            .select("version", "checksum")
            .collect()
        )
        return {int(row["version"]): str(row["checksum"]) for row in rows}

    def record_version(self, version: int, description: str, checksum: str) -> None:
        self._session.createDataFrame(  # type: ignore[reportUnknownMemberType]
            [(version, description, checksum)], schema=_RECORD_SCHEMA
        ).withColumn("applied_at", F.current_timestamp()).write.format(
            self._table_format
        ).mode("append").saveAsTable(self._version_table)
