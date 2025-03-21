# Dockerfile

FROM python:3.11.0rc2-bullseye

###############################
# ENVIRONMENT 
###############################

# Get arguments from .yml file
ARG HTTP_PROXY_URL
ARG HTTPS_PROXY_URL
ARG PROXY_SSL_CERT_BUNDLE
ARG ENV

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV environment=${ENV}
ENV https_proxy=${HTTPS_PROXY_URL}
ENV http_proxy=${HTTP_PROXY_URL}
ENV POETRY_VERSION=1.0.0
ENV CA_BUNDLE_CERT=${PROXY_SSL_CERT_BUNDLE:+/etc/ssl/certs/ca-cert-bundle.crt}

# Install SSL certificates
COPY --from=project-root ${PROXY_SSL_CERT_BUNDLE:+$PROXY_SSL_CERT_BUNDLE} $CA_BUNDLE_CERT
RUN update-ca-certificates

# Conditionally set REQUESTS_CA_BUNDLE (setting for Poetry install)
ENV REQUESTS_CA_BUNDLE=${PROXY_SSL_CERT_BUNDLE:+$CA_BUNDLE_CERT}


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
