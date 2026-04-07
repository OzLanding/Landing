FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

RUN apt-get update && apt-get install -y curl build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --all-packages

COPY . .

COPY ./scripts /scripts
RUN chmod +x /scripts/run.sh

EXPOSE 8000

CMD ["/scripts/run.sh"]
