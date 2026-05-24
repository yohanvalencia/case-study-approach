import csv
import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from error_handlers import ErrorStrategy
from factory import build_error_handler, build_writer
from models import Transaction
from writers import WriterStrategy

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def ingest(csv_path: str, writer: WriterStrategy, on_error: ErrorStrategy) -> None:
    inserted = 0
    skipped = 0

    with open(csv_path, newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            try:
                transaction = Transaction(**row)
            except ValidationError as exc:
                on_error.handle(row, exc)
                skipped += 1
                continue

            try:
                writer.write(transaction)
                inserted += 1
            except Exception as exc:
                on_error.handle(row, exc)
                skipped += 1

    log.info("Finished. inserted=%d  skipped=%d", inserted, skipped)


def main() -> None:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    writer = build_writer(config["writer"])
    on_error = build_error_handler(config["error_handler"])

    with writer, on_error:
        ingest(config["csv_path"], writer, on_error)


if __name__ == "__main__":
    main()
