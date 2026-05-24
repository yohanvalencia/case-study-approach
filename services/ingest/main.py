import csv
import logging
import os
from datetime import date
from decimal import Decimal

import psycopg2
from pydantic import BaseModel, ValidationError, field_validator

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

CSV_PATH = os.getenv("CSV_PATH", "data/customer_transactions.csv")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/pipeline")

INSERT_SQL = """
    INSERT INTO public.customer_transactions
        (transaction_id, customer_id, transaction_date, product_id,
         product_name, quantity, price, tax)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


class Transaction(BaseModel):
    transaction_id: int
    customer_id: int
    transaction_date: date
    product_id: int
    product_name: str
    quantity: int
    price: Decimal
    tax: Decimal

    @field_validator("customer_id", "quantity", mode="before")
    @classmethod
    def coerce_to_int(cls, v: str) -> int:
        return int(float(v))


def main() -> None:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    inserted = skipped = 0

    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            try:
                tx = Transaction(**row)
            except ValidationError as exc:
                log.warning("Validation failed, skipping row %s: %s", row, exc)
                skipped += 1
                continue

            try:
                cur.execute(
                    INSERT_SQL,
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
                conn.commit()
                inserted += 1
            except Exception as exc:
                conn.rollback()
                log.warning(
                    "Insert failed for transaction_id=%s, skipping: %s",
                    row.get("transaction_id"),
                    exc,
                )
                skipped += 1

    cur.close()
    conn.close()
    log.info("Finished. inserted=%d skipped=%d", inserted, skipped)


if __name__ == "__main__":
    main()
