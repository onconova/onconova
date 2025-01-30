# POP


## Development server

Run `ng serve` for an HTTPS dev server.
```bash 
ng serve --ssl --ssl-cert ../etc/certs/localhost.pem --ssl-key ../etc/certs/localhost-key.pem 
```
 Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Regenerate OpenAPI client

```bash
rm -r src/app/shared/openapi && npx openapi-generator-cli generate -i openapi.json -g typescript-angular -o src/app/shared/openapi --additional-properties fileNaming=kebab-case,withInterfaces=true,useSingleRequestParameter=true --generate-alias-as-model 
```

## Generate a local development SSL certificate 

```bash 
sudo certbot certonly --standalone --preferred-challenges http -d localhost -d localhost
```

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
