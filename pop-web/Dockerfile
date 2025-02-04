FROM node:22-alpine

ARG PROXY_HTTPS
ARG PROXY_HTTP
ARG CA_SSL_CERT_BUNDLE

# Install SSL certificates
COPY --from=project-root ${CA_SSL_CERT_BUNDLE} $CA_BUNDLE_CERT
ENV CA_BUNDLE_CERT=/etc/ssl/certs/ca-cert-bundle.crt

# Setup workspace
WORKDIR usr/src/app

# Copy all source files
COPY . .

# Setup NPM proxy configuration
RUN npm config set proxy ${PROXY_HTTPS} \
    && npm config set https-proxy ${PROXY_HTTP}
# Install the Angular CLI
RUN npm install -g @angular/cli
RUN npm install --force

ENV WDS_SOCKET_PORT=443

EXPOSE 4200