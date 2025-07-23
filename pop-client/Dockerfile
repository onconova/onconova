########################################
# ANGULAR-BASE
# Sets up Node and Angular
########################################
FROM node:22-bullseye  AS angular-base

ARG ROOT_CA_CERTIFICATES=

# Setup workspace
WORKDIR /app

# Optional: Install a root CA TLS certificate
COPY ${ROOT_CA_CERTIFICATES} /usr/local/share/ca-certificates/corporate-ca.crt
# Update the system's CA certificates bundle
RUN update-ca-certificates

# Install the Angular CLI
RUN npm install -g @angular/cli

# Install project dependencies
COPY package.json ./
RUN npm install --force

# Install Debian packages
RUN apt-get update && apt-get install -y \
    # Dependencies for entrypoint.sh
    gettext=0.21-* \
    # Dependencies for OpenAPI Generator 
    default-jre=2:1.* \
    curl=7.74.* 

# Generate the POP API client package
COPY openapi.json generate-api-client.sh ./
RUN npm run generate:api:client java

# Copy all source files
COPY . ./

# Copy the plugins source files if exist
COPY --from=plugins . /app/src/plugins/

# Clean up local files
RUN  apt-get clean && rm -rf /var/lib/apt/lists/* && npm cache clean --force

RUN chmod +x /app/entrypoint.sh

# Create a non-root user and switch to it
RUN useradd -m appuser && chown appuser /app /app/src
USER appuser


########################################
# DEVLEOPMENT
# Serve application for development
########################################
FROM angular-base AS development
USER root
RUN apt-get update && apt-get install -y \
    # Dependencies for headless Chromium browser
    libxkbcommon-x11-0=1.0.* \ 
    libgbm-dev=20.3.* \ 
    chromium=120.0.* \
    chromium-driver=120.0.*
USER appuser
# Serve angular application
ENTRYPOINT ["/app/entrypoint.sh", "--files", "/app/src/environments/env.js", "--files", "/app/src/plugins/plugins.env.js"]
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "80", "--disable-host-check", "--configuration", "development"]

########################################
# BUILDER
# Build the production-ready application
########################################
FROM angular-base AS builder
# Creating angular build
RUN ng build --output-path dist/client --configuration production

########################################
# PRODUCTION
# Nginx for serving built app files
########################################
FROM nginx:1.23.3-alpine AS production

# Prepare the Nginx webserver files
COPY --from=builder /app/dist/client /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./entrypoint.sh /app/entrypoint.sh

# Set permissions and use non-root user
RUN adduser -D appuser && chown -R appuser /usr/share/nginx/html /app
USER appuser

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh", "--files", "/usr/share/nginx/html/assets/env.js", "--files", "/usr/share/nginx/html/assets/plugins.env.js"]
CMD ["nginx", "-g", "daemon off;"]
EXPOSE 80