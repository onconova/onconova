########################################
# ANGULAR-BASE
# Sets up Node and Angular
########################################
FROM node:22-alpine as angular-base

# Setup workspace
WORKDIR /app

# Copy all source files
COPY . .

# Install the Angular CLI
RUN npm install -g @angular/cli
RUN npm install --force

########################################
# DEVLEOPMENT
# Serve application for development
########################################
FROM angular-base as development
# Serve angular application
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "80", "--disable-host-check", "--configuration", "development"]

########################################
# BUILDER
# Build the production-ready application
########################################
FROM angular-base as builder
# Creating angular build
RUN ng build --output-path dist/client --configuration production

########################################
# PRODUCTION
# Nginx for serving built app files
########################################
FROM nginx:1.23.3-alpine as production
COPY --from=builder /app/dist/client /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80