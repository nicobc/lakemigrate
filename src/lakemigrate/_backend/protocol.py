from typing import Protocol


class Backend(Protocol):
    def execute(self, sql: str) -> None:
        """Execute a SQL statement against the lakehouse."""
        ...

    def get_applied_migrations(self) -> dict[int, str]:
        """Return a mapping of applied migration version to its recorded checksum."""
        ...

    def record_version(self, version: int, description: str, checksum: str) -> None:
        """Record a successfully applied migration in the history table."""
        ...
