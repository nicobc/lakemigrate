import argparse
import logging
import sys

from lakemigrate._backend.delta import DEFAULT_HISTORY_TABLE
from lakemigrate._engine import migrate

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(
        prog="lakemigrate",
        description="Run pending SQL migrations against a Delta lakehouse.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate_cmd = subparsers.add_parser("migrate", help="Apply all pending migrations.")
    migrate_cmd.add_argument(
        "--migrations-dir",
        required=True,
        metavar="DIR",
        help="Directory containing migration SQL files.",
    )
    migrate_cmd.add_argument(
        "--history-table",
        default=DEFAULT_HISTORY_TABLE,
        metavar="TABLE",
        help=f"History table name (default: {DEFAULT_HISTORY_TABLE}).",
    )

    args = parser.parse_args()

    try:
        migrate(args.migrations_dir, args.history_table)
    except Exception as exc:
        logger.error(str(exc))
        sys.exit(1)
