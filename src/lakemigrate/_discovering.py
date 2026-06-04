import hashlib
import re
from pathlib import Path

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
