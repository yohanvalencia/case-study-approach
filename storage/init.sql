CREATE DATABASE pipeline;
CREATE DATABASE airflow;

\connect pipeline

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS bronze.customer_transactions (
    transaction_id   INTEGER PRIMARY KEY,
    customer_id      INTEGER,
    transaction_date DATE,
    product_id       INTEGER,
    product_name     TEXT,
    quantity         INTEGER,
    price            NUMERIC(10,2),
    tax              NUMERIC(10,2)
);

CREATE TABLE silver.dim_table (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL
);

CREATE TABLE silver.fact_table (
    transaction_id        INTEGER PRIMARY KEY,
    customer_id           INTEGER,
    transaction_date      DATE    NOT NULL,
    month                 DATE,
    product_id            INTEGER REFERENCES silver.dim_table(product_id),
    quantity              INTEGER,
    price                 NUMERIC(10,2),
    tax                   NUMERIC(10,2),
    total_amount          NUMERIC(10,2),
    monthly_total_revenue NUMERIC(12,2),
    customer_total_spend  NUMERIC(12,2)
);
