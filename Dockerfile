FROM mcr.microsoft.com/playwright/python:v1.41.2-jammy

RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,mode=0777,target=$POETRY_CACHE_DIR \
    poetry install --without dev --without deployer --no-root
RUN playwright install chromium

COPY . .

ENV HEADLESS=true \
    STORE_VIDEOS=true

#ENV DEBUG=pw:api

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log_conf.yaml"]
