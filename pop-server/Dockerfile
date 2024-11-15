# Dockerfile

FROM python:3.11.0rc2-bullseye

###############################
# ENVIRONMENT 
###############################

# Get arguments from .yml file
ARG PROXY_HTTP
ARG PROXY_HTTPS
ARG SSL_CERT_BUNDLE
ARG ENV

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV environment=${ENV}
ENV https_proxy=${PROXY_HTTPS}
ENV http_proxy=${PROXY_HTTP}
ENV POETRY_VERSION=1.0.0
ENV CA_BUNDLE_CERT=/etc/ssl/certs/ca-cert-bundle.crt
ENV REQUESTS_CA_BUNDLE=$CA_BUNDLE_CERT

# Install SSL certificates
COPY --from=certificates ${SSL_CERT_BUNDLE} $CA_BUNDLE_CERT
RUN update-ca-certificates

# Set work directory
WORKDIR /app/code

# Install essential Linux packages
RUN apt-get clean
RUN apt-get -y update && apt-get install -y \
		cron \
		openssh-server \ 
		nano \
		tree \
		iputils-ping \
		traceroute \ 
		net-tools \
		rsyslog
RUN apt install -y curl

# Setup rsyslog
RUN sed -i '/imklog/s/^/#/' /etc/rsyslog.conf

# Install python dependencies 
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org "poetry==$POETRY_VERSION"
COPY ./pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

# Copy source files
COPY . .
