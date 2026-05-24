import csv
import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

_CSV_FIELDS = [
    "transaction_id", "customer_id", "transaction_date", "product_id",
    "product_name", "quantity", "price", "tax", "error",
]


class ErrorStrategy(ABC):
    def __enter__(self) -> "ErrorStrategy":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        pass

    @abstractmethod
    def handle(self, row: dict, error: Exception) -> None: ...


class LogErrorStrategy(ErrorStrategy):
    def handle(self, row: dict, error: Exception) -> None:
        log.warning("Skipping row %s: %s", row, error)


class CsvErrorStrategy(ErrorStrategy):
    def __init__(self, path: str) -> None:
        self._file = open(path, "w", newline="")
        self._writer = csv.DictWriter(self._file, fieldnames=_CSV_FIELDS)
        self._writer.writeheader()

    def handle(self, row: dict, error: Exception) -> None:
        self._writer.writerow({**row, "error": str(error)})

    def close(self) -> None:
        self._file.close()
