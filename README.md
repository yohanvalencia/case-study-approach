# Solution thoughts

The approach starts with a shift-left mindset. It's cheaper to fix errors at the source than downstream, so I used Pydantic to model and validate events at ingestion time.

For the writer I went with a factory pattern and a `config.yaml` to switch outputs (log, CSV) without touching business logic. It's a "poor man's" ports and adapters pattern.

The database schema follows a medallion architecture (bronze, silver, gold) and the dbt folder structure is `domain/privacy/quality/table_name`, which keeps things ready for a data mesh setup where each domain owns its models.

I used Claude Sonnet 4.6 to help implement the solution in these steps:

1. Write `storage/init.sql` with the tables and relationships needed
2. Build the ingest service with Pydantic validation and a strategy/factory pattern to support multiple writers
3. Build the dbt models following the folder structure above
4. Wire up standalone Airflow to tie ingest and dbt together, accounting for materialization and incremental strategies

You can find the `CLAUDE.md` in this repo.

# How to test it:

ErrorHandler to Log:

1. `docker compose up --build`
2. Open `localhost:8080`
3. Run pipeline dag

Changing ErrorHandler to CSVOutput:

1. Go to `services/config.yaml`, comment line 8 and uncomment line 9-10 you will set the ErrorHandler to csv output.
2. Run `docker compose --profile tools build`
3. Run pipeline dag
4. Check `data` directory for the new csv file.

Cleanup:
`docker compose down -v`

# Improvements

 Here is what I would've liked to implement. Happy to discuss it in more detail. The whole architecture is meant to run on a Kubernetes cluster, and each piece was chosen with open source projects in mind.

![image](architecture-data-platform.png)
