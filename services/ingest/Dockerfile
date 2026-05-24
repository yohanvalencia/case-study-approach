FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev --no-install-project

COPY *.py .
COPY config.yaml .

CMD ["uv", "run", "python", "main.py"]
