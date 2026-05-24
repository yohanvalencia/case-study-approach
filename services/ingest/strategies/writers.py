from abc import ABC, abstractmethod

import psycopg2

from ingest.models import Transaction

_INSERT_SQL = """
    INSERT INTO bronze.customer_transactions
        (transaction_id, customer_id, transaction_date, product_id,
         product_name, quantity, price, tax)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (transaction_id) DO NOTHING
"""


class WriterStrategy(ABC):
    def __enter__(self) -> "WriterStrategy":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        pass

    @abstractmethod
    def write(self, tx: Transaction) -> bool: ...


class PostgresWriter(WriterStrategy):
    def __init__(self, dsn: str) -> None:
        self._conn = psycopg2.connect(dsn)
        self._cursor = self._conn.cursor()

    def write(self, tx: Transaction) -> bool:
        self._cursor.execute(
            _INSERT_SQL,
            (
                tx.transaction_id,
                tx.customer_id,
                tx.transaction_date,
                tx.product_id,
                tx.product_name,
                tx.quantity,
                tx.price,
                tx.tax,
            ),
        )
        self._conn.commit()
        return self._cursor.rowcount > 0

    def close(self) -> None:
        self._cursor.close()
        self._conn.close()
