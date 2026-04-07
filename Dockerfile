FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VENV_PATH=/opt/venv
ENV PATH="$VENV_PATH/bin:/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y curl build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN python -m venv $VENV_PATH

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN . $VENV_PATH/bin/activate && uv sync

COPY . .

RUN chmod +x /app/scripts/run.sh

EXPOSE 8000

CMD ["/app/scripts/run.sh"]
