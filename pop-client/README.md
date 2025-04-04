# POP


## Development server

Run `ng serve` for an HTTPS dev server.
```bash 
ng serve --ssl --ssl-cert ../etc/certs/localhost.pem --ssl-key ../etc/certs/localhost-key.pem 
```
 Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Regenerate OpenAPI client

```bash
docker compose run -v "${PWD}/pop-client/openapi.json:/app/openapi.json" pop-server python manage.py export_openapi_schema --output /app/openapi.json --indent 4
```

```bash
rm -r pop-client/src/app/shared/openapi && npx @openapitools/openapi-generator-cli generate -i pop-client/openapi.json -g typescript-angular -o pop-client/src/app/shared/openapi --additional-properties fileNaming=kebab-case,withInterfaces=true,useSingleRequestParameter=true --generate-alias-as-model 
```
Alternatively using Docker
```bash
rm -r ${PWD}/pop-client/src/app/shared/openapi && docker run --rm -v "${PWD}/pop-client/:/local" openapitools/openapi-generator-cli:latest-release generate \
    -i /local/openapi.json \
    -g typescript-angular \
    -o /local/src/app/shared/openapi \
    --additional-properties fileNaming=kebab-case,withInterfaces=true,useSingleRequestParameter=true --generate-alias-as-model      
```

## Adding plugins

1. Create a plugin component in `/src/plugins`. For example, let's create a new custom dashboard with an additional panel
```ts
import { Component } from '@angular/core';
import { DashboardComponent } from 'src/app/features/dashboard/dashboard.component';
import { CommonModule } from '@angular/common';
import { Card } from 'primeng/card';

@Component({
    standalone: true,
    selector: 'custom-dashboard',
    template: `
    <pop-dashboard>
        <ng-template #additionalPanels>
            <p-card>{{ newContent }}</p-card>
        </ng-template>
    </pop-dashboard>
    `,
    imports: [
        CommonModule,
        DashboardComponent,
        Card,
    ],
})
export class CustomDashboardComponent {
    public newContent = 'This is a new panel!!!!!!!'
}
```

2. Add new route or override an existing one on the `src/plugins/plugins.route.ts` file: 
```ts
export const pluginRoutes: Routes = [
    {
        path: '', 
        children: [
            { path: 'dashboard', loadComponent: () => import('./custom-dashboard/custom-dashboard.component').then(m => m.CustomDashboardComponent) }
        ],
    }
];
```


## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).
