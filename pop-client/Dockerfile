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

# Install the Angular CLI
RUN npm install -g @angular/cli
RUN npm install --force

# Optional: Install a root CA TLS certificate
COPY ${ROOT_CA_CERTIFICATES} /usr/local/share/ca-certificates/corporate-ca.crt
# Update the system's CA certificates bundle
RUN update-ca-certificates

# Install Java for running OpenAPI Generator
RUN apt-get update && apt-get install -y default-jre curl && apt-get clean

# Generate the POP API client package
RUN npm run generate:api:client java

RUN npm cache clean --force

########################################
# DEVLEOPMENT
# Serve application for development
########################################
FROM angular-base AS development
# Serve angular application
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
EXPOSE 80