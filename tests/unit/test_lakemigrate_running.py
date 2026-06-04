import hashlib

import pytest

from lakemigrate._migration import Migration
from lakemigrate._running import run_migrations
from tests.unit.conftest import StubBackend


def _migration(version: int, sql: str, description: str = "desc") -> Migration:
    checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
    return Migration(version=version, description=description, sql=sql, checksum=checksum)


def test_run_migrations_fresh_run(stub_backend: StubBackend) -> None:
    migrations = [
        _migration(1, "CREATE TABLE foo (id INT)"),
        _migration(2, "CREATE TABLE bar (id INT)"),
    ]

    run_migrations(stub_backend, migrations)

    assert stub_backend.executed == ["CREATE TABLE foo (id INT)", "CREATE TABLE bar (id INT)"]
    assert set(stub_backend.applied.keys()) == {1, 2}


def test_run_migrations_up_to_date(stub_backend: StubBackend) -> None:
    m = _migration(1, "CREATE TABLE foo (id INT)")
    stub_backend.applied[1] = m.checksum

    run_migrations(stub_backend, [m])

    assert stub_backend.executed == []


def test_run_migrations_partial_run(stub_backend: StubBackend) -> None:
    m1 = _migration(1, "CREATE TABLE foo (id INT)")
    m2 = _migration(2, "CREATE TABLE bar (id INT)")
    stub_backend.applied[1] = m1.checksum

    run_migrations(stub_backend, [m1, m2])

    assert stub_backend.executed == ["CREATE TABLE bar (id INT)"]
    assert 2 in stub_backend.applied


def test_run_migrations_failure_halts_and_does_not_record(stub_backend: StubBackend) -> None:
    m1 = _migration(1, "CREATE TABLE foo (id INT)")
    m2 = _migration(2, "CREATE TABLE bar (id INT)")
    m3 = _migration(3, "CREATE TABLE baz (id INT)")
    stub_backend.error_sql = "CREATE TABLE bar"

    with pytest.raises(RuntimeError):
        run_migrations(stub_backend, [m1, m2, m3])

    assert stub_backend.executed == ["CREATE TABLE foo (id INT)"]
    assert 1 in stub_backend.applied
    assert 2 not in stub_backend.applied
    assert 3 not in stub_backend.applied


def test_run_migrations_checksum_mismatch_errors_before_execution(
    stub_backend: StubBackend,
) -> None:
    m = _migration(1, "CREATE TABLE foo (id INT)")
    stub_backend.applied[1] = "wrong_checksum"

    with pytest.raises(ValueError, match="checksum mismatch"):
        run_migrations(stub_backend, [m])

    assert stub_backend.executed == []
