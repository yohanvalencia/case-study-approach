# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start core services (Airflow + PostgreSQL)
docker-compose up

# Build images after code changes
docker build -t pipeline-ingest:latest ./services
docker build -t pipeline-dbt:latest ./dbt

# Run ingest locally (Postgres must be reachable on localhost:5432)
# Change DSN in services/config.yaml: @postgres → @localhost first
cd services && uv run python -m ingest.main

# Run dbt locally
cd dbt && dbt run --profiles-dir .
```

Airflow UI: `http://localhost:8080` — no credentials required in dev.

## Architecture

Batch ETL pipeline: CSV → Airflow DAG → Postgres (bronze) → dbt (silver).

```
data/customer_transactions.csv
    ↓
Airflow DAG (dags/pipeline_dag.py) — @daily
    ├── ingest  — Pydantic validation → bronze.customer_transactions (upsert)
    └── dbt_run — bronze → silver.dim_table + silver.fact_table (incremental MERGE)
```

**Ingest** (`services/ingest/`) uses a strategy pattern: `factory.py` builds writer and error handler from `config.yaml`. `PostgresWriter` uses `ON CONFLICT (transaction_id) DO NOTHING RETURNING transaction_id` — the `RETURNING` clause is what makes insert vs. skip detection reliable (not `rowcount`, which is unreliable with `DO NOTHING`).

**dbt** (`dbt/models/sales/green/silver/`):
- `dim_table.sql` — deduplicates products via MERGE on `product_id`. Does NOT use a manual `NOT IN` filter — the merge strategy owns deduplication entirely.
- `fact_table.sql` — enriches transactions with `total_amount`, `monthly_total_revenue`, `customer_total_spend` (window functions). Aggregations only, no cleaning.
- `macros/generate_schema_name.sql` — overrides dbt default so schema names are used as-is (no project prefix).

**DockerOperator** in the DAG has `mount_tmp_dir=False` on both tasks — required on macOS because Airflow tries to bind-mount a `/tmp` path from inside the container, which Docker Desktop cannot resolve.

## Key files

| File | Purpose |
|------|---------|
| `services/config.yaml` | CSV path, writer type (`postgres`), error handler (`log`\|`csv`) |
| `dbt/profiles.yml` | DB connection — uses `DBT_HOST` env var (set to `postgres` in Docker) |
| `storage/init.sql` | Creates databases, schemas, and tables on first run |
| `dags/pipeline_dag.py` | DAG definition — `PIPELINE_HOST_PATH` env var must match the host path where docker-compose runs |

## Target architecture (designed, not yet implemented)

See `README.md` for the full evolution plan. The direction agreed on:

- **Dagster** replaces Airflow — code locations per team for independent release cycles
- **Shift-left data quality** — Pydantic business-rule validators + quarantine table for invalid rows; dbt receives clean data and does aggregations only
- **Outbox pattern** — valid rows write to `bronze.customer_transactions` + outbox table in a single Postgres transaction
- **Arroyo** reads outbox via CDC (Postgres WAL) → publishes to **Redpanda** topic, enforced by **Schema Registry** (Avro schema generated from ODCS contract via CI/CD)
- **Iceberg on S3** — append-only raw events; a Dagster asset resolves latest-state per key (deduplication); dbt runs on the resolved silver layer
- **Data products** — domain-owned Gold Iceberg tables with ODCS contracts, discoverable via a data catalog, queryable via Trino/DuckDB

## Tech stack

- Python 3.12 / uv
- Apache Airflow (slim) with DockerOperator
- PostgreSQL 15
- dbt-core + dbt-postgres
- Pydantic v2
- psycopg2-binary
