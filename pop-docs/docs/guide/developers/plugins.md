The Precision Oncology Platform (POP) supports a plugin architecture for extending the Angular client without modifying the core platform codebase. This enables institutions and developers to add custom views, dashboards, visualizations, or workflows tailored to their needs — while keeping the core client clean, maintainable, and upgradeable.

This page explains what plugins are, how to develop them, and how to integrate them into POP.

## What Are POP Plugins?

A *plugin* is a standalone Angular component or feature module that:

- Extends or customizes the POP client.
- Is developed separately from core platform features.
- Can add new routes, components, or override existing views.
- Optionally consumes APIs from POP itself or from institution-specific microservices.

**Plugins allow you to build institution-specific functionality without altering the core client code.**


## When to Use a Plugin
Use a plugin when you need to:

- Add institution-specific dashboards or reports.
- Integrate visualizations from a local microservice.
- Customize or extend core workflows (e.g., adding new panels to existing dashboards).
- Provide internal utilities or admin tools visible only to authorized users.

!!! danger  

    Never hardcode institution-specific functionality directly into the core platform.

## How to Develop a Plugin

1. **Create a plugins directory**

    Create a new directory where all POP plugins will reside. 

    *Example*:
    ```bash
    mkdir myplugins
    ```


2. **Create a Plugin Component**
    
    Create a new Angular standalone component or module for your plugin. 

    *Example*: Customizing the POP landing dashboard with an additional panel.

    ```ts
        import { Component } from '@angular/core';
        import { CommonModule } from '@angular/common';
        import { Card } from 'primeng/card';

        import { DashboardComponent } from 'src/app/features/dashboard/dashboard.component';

        @Component({
        standalone: true,
        selector: 'my-custom-dashboard',
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
        export class MyCustomDashboardComponent {
            public newContent = 'This is a new panel!!'
        }
    ```

 3. **Add or Override a Route**
   
    To add your plugin into the client’s routing, add or override a route in a `plugins.route.ts` file.

    *Example*: Override the `/dashboard` route to serve our customized dashboard component

    ```ts
    export const pluginRoutes: Routes = [
        {
            path: '',
            children: [
                { path: 'dashboard', loadComponent: () => import('.my-custom-dashboard.component').then(m => m.MyCustomDashboardComponent) }
            ],
        }
    ];
    ```

3. **Installing the plugins**

    To integrate your plugin into the POP client, you need to configure the client to load your plugin directory at runtime.

    This is done by setting the `CLIENT_PLUGINS_PATH` environment variable to point to the directory containing your plugin code.
    Once set, restarting the client container will make the Angular application automatically discover and load your plugins.


    *Example*: Install the custom dashboard plugin located in `./myplugins`.

    ```bash
    CLIENT_PLUGINS_PATH=./myplugins
    docker compose up pop-client
    ```

    This command starts the POP client container, instructing it to look for plugin components and route definitions in the `./myplugins` directory.


    !!! important

        For the plugin installation to work properly, the `plugins.route.ts` file **must be located inside the same directory** specified by `CLIENT_PLUGINS_PATH`.

        This route file defines how your custom plugin routes integrate with the POP application routing system.
        Without it, your plugins won’t be registered or accessible within the client.


    For **production**, build the client container anew with the `CLIENT_PLUGINS_PATH` variable set to build the container along the plugins. 

## Integrating with Microservices

Plugins can optionally consume APIs exposed by institution-specific microservices for:

- Fetching external or derived data.
- Displaying institution-specific reports or tools.

Follow the same API consumption best practices as with the POP API:

- Use environment variables for base URLs.
- Implement proper authentication and error handling.
- Keep plugin services modular and independent.