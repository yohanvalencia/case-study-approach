import os
from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

HOST_PATH = os.environ.get("PIPELINE_HOST_PATH", "")

with DAG(
    dag_id="pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    ingest = DockerOperator(
        task_id="ingest",
        image="pipeline-ingest:latest",
        network_mode="pipeline",
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mounts=[
            Mount(source=f"{HOST_PATH}/data", target="/app/data", type="bind"),
            Mount(source=f"{HOST_PATH}/services/config.yaml", target="/app/config.yaml", type="bind"),
        ],
    )

    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="pipeline-dbt:latest",
        network_mode="pipeline",
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        environment={"DBT_HOST": "postgres"},
    )

    ingest >> dbt_run
