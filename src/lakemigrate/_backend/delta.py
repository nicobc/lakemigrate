import logging
from datetime import datetime, timezone

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType, TimestampType

logger = logging.getLogger(__name__)

DEFAULT_HISTORY_TABLE = "default.lakemigrate_history"

_HISTORY_TABLE_SCHEMA = StructType(
    [
        StructField("version", IntegerType(), nullable=False),
        StructField("description", StringType(), nullable=False),
        StructField("checksum", StringType(), nullable=False),
        StructField("applied_at", TimestampType(), nullable=False),
    ]
)


class DeltaBackend:
    def __init__(
        self,
        history_table: str = DEFAULT_HISTORY_TABLE,
    ) -> None:
        session = SparkSession.getActiveSession()
        if session is None:
            raise RuntimeError("No active SparkSession — start one before using DeltaBackend")
        self._session = session
        self._history_table = history_table
        self._ensure_history_table()

    def _ensure_history_table(self) -> None:
        logger.debug(f"ensuring history table exists: {self._history_table}")
        (
            DeltaTable.createIfNotExists(self._session)
            .tableName(self._history_table)
            .addColumn("version", IntegerType(), nullable=False)
            .addColumn("description", StringType(), nullable=False)
            .addColumn("checksum", StringType(), nullable=False)
            .addColumn("applied_at", TimestampType(), nullable=False)
            .execute()
        )

    def execute(self, sql: str) -> None:
        self._session.sql(sql)  # type: ignore[reportUnknownMemberType]

    def get_applied_migrations(self) -> dict[int, str]:
        rows = self._session.read.table(self._history_table).select("version", "checksum").collect()
        return {int(row["version"]): str(row["checksum"]) for row in rows}

    def record_version(self, version: int, description: str, checksum: str) -> None:
        logger.debug(f"recording migration {version} in {self._history_table}")
        self._session.createDataFrame(  # type: ignore[reportUnknownMemberType]
            [(version, description, checksum, datetime.now(timezone.utc))],
            schema=_HISTORY_TABLE_SCHEMA,
        ).write.format("delta").mode("append").saveAsTable(self._history_table)
