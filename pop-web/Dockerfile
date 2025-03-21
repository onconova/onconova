FROM node:22-alpine

ARG HTTPS_PROXY_URL
ARG HTTP_PROXY_URL
ARG PROXY_SSL_CERT_BUNDLE

# Install SSL certificates
COPY --from=project-root ${PROXY_SSL_CERT_BUNDLE} $CA_BUNDLE_CERT
ENV CA_BUNDLE_CERT=/etc/ssl/certs/ca-cert-bundle.crt

# Setup workspace
WORKDIR usr/src/app

# Copy all source files
COPY . .

# Setup NPM proxy configuration
RUN npm config set proxy ${HTTPS_PROXY_URL} \
    && npm config set https-proxy ${HTTP_PROXY_URL}
# Install the Angular CLI
RUN npm install -g @angular/cli
RUN npm install --force

ENV WDS_SOCKET_PORT=443

EXPOSE 4200