########################################
# ANGULAR-BASE
# Sets up Node and Angular
########################################
FROM node:22-bullseye  AS angular-base

# Setup workspace
WORKDIR /app

ARG ROOT_CA_CERTIFICATES=

# Copy all source files
COPY . .

# Copy the plugins source files if exist
COPY --from=plugins . /app/src/plugins/

# Install the Angular CLI
RUN npm install -g @angular/cli
RUN npm install --force

# Optional: Install a root CA TLS certificate
COPY ${ROOT_CA_CERTIFICATES} /usr/local/share/ca-certificates/corporate-ca.crt
# Update the system's CA certificates bundle
RUN update-ca-certificates

# Install dependencies for headless Chromium browser
RUN apt-get update && apt-get install -y libxkbcommon-x11-0 libgbm-dev && apt-get clean

# Install dependencies for headless Chromium browser
RUN apt-get update && apt-get install -y gettext && apt-get clean

# Install Java for running OpenAPI Generator
RUN apt-get update && apt-get install -y default-jre curl && apt-get clean

# Generate the POP API client package
RUN npm run generate:api:client java

RUN npm cache clean --force

RUN chmod +x /app/entrypoint.sh

########################################
# DEVLEOPMENT
# Serve application for development
########################################
FROM angular-base AS development
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
COPY --from=builder /app/dist/client /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh", "--files", "/usr/share/nginx/html/assets/env.js", "--files", "/usr/share/nginx/html/assets/plugins.env.js"]
CMD ["nginx", "-g", "daemon off;"]
EXPOSE 80