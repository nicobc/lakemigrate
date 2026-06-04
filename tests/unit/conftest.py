import pytest

from lakemigrate._backend.protocol import Backend


class StubBackend:
    executed: list[str]
    applied: dict[int, str]
    error_sql: str | None

    def __init__(self) -> None:
        self.executed = []
        self.applied = {}
        self.error_sql = None

    def execute(self, sql: str) -> None:
        if self.error_sql is not None and self.error_sql in sql:
            raise RuntimeError(f"execution failed: {sql}")
        self.executed.append(sql)

    def get_applied_migrations(self) -> dict[int, str]:
        return dict(self.applied)

    def record_version(self, version: int, description: str, checksum: str) -> None:
        self.applied[version] = checksum


_: Backend = StubBackend()  # structural subtyping check


@pytest.fixture
def stub_backend() -> StubBackend:
    return StubBackend()
