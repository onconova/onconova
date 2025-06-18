# POP


## Development server

Run `ng serve` for an HTTPS dev server.
```bash 
ng serve --ssl --ssl-cert ../etc/certs/localhost.pem --ssl-key ../etc/certs/localhost-key.pem 
```
 Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Regenerate OpenAPI client

```bash
npm run generate:api:client
```

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).
