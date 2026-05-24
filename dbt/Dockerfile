FROM python:3.12-slim

RUN pip install dbt-core dbt-postgres

WORKDIR /usr/app/dbt

COPY . .

CMD ["dbt", "run", "--profiles-dir", "."]
