
################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
FROM python:3.11-slim as python-base

# Python
ENV PYTHONUNBUFFERED=1 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # Poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.0.0 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # never create virtual environment automaticly, only use env prepared by us
    POETRY_VIRTUALENVS_CREATE=false \
    \
    # this is where our requirements + virtual environment will live
    VIRTUAL_ENV="/venv"


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

# prepare virtual env
RUN python -m venv $VIRTUAL_ENV

# Install pstcopg2 Linux dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup work directory
WORKDIR /app/src
ENV PYTHONPATH="/app/src:$PYTHONPATH"

################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################
FROM python-base as builder-base

# Install essential Linux packages
RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
	python3-dev \
	iputils-ping \
	curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python dependencies 
RUN --mount=type=cache,target=/root/.cache \
	curl -sSL https://install.python-poetry.org | python -

WORKDIR /app/src		

# Copy dependencies
COPY ./pyproject.toml .
RUN --mount=type=cache,target=/root/.cache \
	poetry install --no-root --no-interaction --no-ansi


################################
# DEVELOPMENT
# Image used during development / testing
################################
FROM builder-base as development

ENV ENVIRONMENT=development
# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --no-interaction --no-ansi

# copy in our built venv
COPY --from=builder-base $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /app/src

# Copy only necessary source files
COPY . .

EXPOSE 8000
CMD ["python", "manage.py",  "runserver_plus", "0.0.0.0:8000"]


################################
# PRODUCTION
# Final image used for runtime
################################
FROM python-base as production

ENV ENVIRONMENT=production
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates && \
    apt-get clean

# copy in our built venv
COPY --from=builder-base $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /app/src
# Copy only necessary source files
COPY . .
CMD ["python", "-m", "gunicorn", "pop.wsgi", "--bind", "0.0.0.0:8000", "--workers=5", "--threads=3"]
