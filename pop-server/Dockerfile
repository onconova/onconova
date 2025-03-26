
################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
FROM python:3.11-slim as python-base

# Python layer environment variables
ENV PYTHONUNBUFFERED=1 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # Poetry
    POETRY_VERSION=2.1.0 \
    # Do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # Never create virtual environment automaticly, only use env prepared by this file
    POETRY_VIRTUALENVS_CREATE=false \
    # Root CA certificates bundle for Poetry (if needed)
    REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/root-ca-cert.crt; \
    \
    # Path to the Python virtual environment 
    VIRTUAL_ENV="/venv"
    
# Optional: Install a root CA TLS certificate
ARG ROOT_CA_CERTIFICATES=""
COPY ${ROOT_CA_CERTIFICATES} $REQUESTS_CA_BUNDLE
RUN if [ -n "$ROOT_CA_CERTIFICATES" ]; then \
        update-ca-certificates; \
    fi

# Add venv to path
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Prepare virtual environment
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

# Install essential Linux dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
	python3-dev \
	iputils-ping \
	curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN $VIRTUAL_ENV/bin/pip install poetry==$POETRY_VERSION --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Install Python dependencies
WORKDIR /app/src		
COPY ./pyproject.toml .
RUN --mount=type=cache,target=/root/.cache \
    $VIRTUAL_ENV/bin/poetry install --no-root --no-interaction --no-ansi --no-cache --compile


################################
# DEVELOPMENT
# Image used during development / testing
################################
FROM builder-base as development

# Set environment flag
ENV ENVIRONMENT=development

# Quicker install as runtime dependencies are already installed
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --no-interaction --no-ansi --no-cache

WORKDIR /app/src

# Copy only necessary source files
COPY . .

# Start the devlopment live-server
EXPOSE 8000
CMD ["python", "manage.py",  "runserver_plus", "0.0.0.0:8000"]

################################
# PRODUCTION
# Final image used for production
################################
FROM python-base as production

# Set environment flag
ENV ENVIRONMENT=production

# Copy the pre-built virtual environment without its runtime dependencies 
COPY --from=builder-base $VIRTUAL_ENV $VIRTUAL_ENV

# Copy only necessary source files
WORKDIR /app/src
COPY . .

# Start the production-ready Gunicon webserver
EXPOSE 8000
CMD ["python", "-m", "gunicorn", "pop.wsgi", "--bind", "0.0.0.0:8000", "--workers=5", "--threads=3"]
