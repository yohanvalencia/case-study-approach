FROM apache/airflow:2.9.1-python3.11

USER airflow
RUN pip install --no-cache-dir uv

RUN uv pip install --system \
    "dbt-postgres>=1.7,<2.0"
