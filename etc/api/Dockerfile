ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL}/base/python:3.12.11-slim AS python-base

ENV PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_PATH=/opt/poetry \
    VENV_PATH=/app/.venv \
    PYTHONPATH="$PYTHONPATH:/app" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"
ENV PATH="$VENV_PATH/bin:$POETRY_PATH/bin:$PATH"

FROM python-base AS base

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    curl \
    # deps for building python deps
    build-essential \
    libcurl4-openssl-dev libssl-dev && \
    pip install pip==23.0 && \
    # Install Poetry
    curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_PATH python3 - \
    && poetry --version \
    && poetry config virtualenvs.in-project true \
    # cleanup
    && rm -rf /var/lib/apt/lists/*

FROM base AS build-iam

WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./src/pyproject.toml ./src/poetry.lock* /app/

# Allow installing dev dependencies to run tests
COPY ./vendors /vendors

RUN poetry install --no-interaction --no-ansi --no-root --only main

FROM build-iam AS develop

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./src /app

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE

CMD ["python", "deps_iam", "serve"]


FROM python-base AS runtime

WORKDIR /app

COPY --from=build-iam $VENV_PATH $VENV_PATH
COPY ./vendors /vendors
COPY ./src /app
COPY ./src/certs/epam_root_cert.crt /usr/local/share/ca-certificates
COPY ./src/certs/epam_intermediate_cert.crt /usr/local/share/ca-certificates
RUN apt-get update && apt-get install --no-install-recommends -y postgresql-client && update-ca-certificates && rm -rf /var/lib/apt/lists/*

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE

RUN useradd -Ms /bin/bash deps
USER deps

CMD ["python", "deps_iam", "serve"]
