FROM python:3.14-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock .
RUN poetry install --only main --no-root

COPY incident_lens/ incident_lens/

EXPOSE 8000

CMD ["uvicorn", "incident_lens.main:app", "--host", "0.0.0.0", "--port", "8000"]
