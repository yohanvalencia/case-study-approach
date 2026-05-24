import os

from ingest.strategies.error_handlers import CsvErrorStrategy, ErrorStrategy, LogErrorStrategy
from ingest.strategies.writers import PostgresWriter, WriterStrategy


def build_writer(config: dict) -> WriterStrategy:
    writer_type = config["type"]
    if writer_type == "postgres":
        dsn = os.getenv("DATABASE_URL") or config["dsn"]
        return PostgresWriter(dsn)
    raise ValueError(f"Unknown writer type: '{writer_type}'")


def build_error_handler(config: dict) -> ErrorStrategy:
    handler_type = config["type"]
    if handler_type == "log":
        return LogErrorStrategy()
    if handler_type == "csv":
        return CsvErrorStrategy(config["path"])
    raise ValueError(f"Unknown error handler type: '{handler_type}'")
