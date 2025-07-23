The Precision Oncology Platform (POP) supports a plugin architecture for extending the Angular client **without modifying the core platform codebase**. This enables institutions and developers to add custom views, dashboards, visualizations, or workflows tailored to their needs — while keeping the core client clean, maintainable, and upgradeable.

This page explains what plugins are, how to develop them, and how to integrate them into POP.

---

## What Are POP Plugins?

A *POP plugin* is a standalone Angular component or feature module that:

- Extends or customizes the POP client.
- Is developed separately from core platform features.
- Can add new routes, components, or override existing views.
- Optionally consumes APIs from POP itself or from institution-specific microservices.


> **Why use plugins?**  
> Plugins let you introduce custom, institution-specific functionality *without touching the core client code.*

---

## When to Use a Plugin
Use a plugin when you need to:

- Add institution-specific dashboards, reports, or visualizations.
- Integrate with a local microservice (e.g., data providers or analytics tools).
- Customize or extend core workflows (e.g., adding new panels to existing dashboards).
- Provide internal tools or admin panels for authorized users only.

!!! danger "Avoid Polluting the Core"

    Never hardcode institution-specific functionality into the core POP platform. Always isolate it in a plugin.

---

## How to Develop a Plugin

1. **Create a Plugins Directory**

    Start by creating a directory to hold **all your plugins**' files:

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
        import { pluginsConfig } from '../plugins.env.js'
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
            public newContent = `This is a new panel for ${pluginsConfig.myCustomVariable}!!`
        }
    ```

 4. **Setup runtime environmental variables** (Optional)

    The POP client allows dynamic injection of environment variables at runtime using the `plugins.env.js` file. 

    *Example*: Setting the `myCustomVariable` variable at runtime 
    ```js
    pluginsConfig = {
        myCustomVariable: '${MY_CUSTOM_PLUGIN_VARIABLE}'
    }
    ```
    These values will be substituted at runtime using environment variables from the container or `.env` file.

    !!! warning "Do Not Expose Sensitive Secrets"

        Any value injected into the frontend will be accessible by end users in the browser. Never include secrets or sensitive values — use secure APIs instead.



 5. **Add or Override a Route**
   
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

6. **Installing the plugins**

    Plugins are mounted into the POP client by specifying the plugin directory via the CLIENT_PLUGINS_PATH environment variable.

    === "Development"
    
        Mount your plugin into a local development container:
        
        *Example*: Install the custom dashboard plugin located in `./myplugins`.

        ```bash
        CLIENT_PLUGINS_PATH=./myplugins
        docker compose up client
        ```
    
        This command starts the POP client container, instructing it to look for plugin components and route definitions in the `./myplugins` directory.


    === "Production"
    
        Once `CLIENT_PLUGINS_PATH` has been set, the production-ready client container must be built anew to bundle the plugin files into the client webserver image. 

        *Example*: Install the custom dashboard plugin located in `./myplugins`.

        ```bash
        CLIENT_PLUGINS_PATH=./myplugins
        docker compose up --build client
        ```
    
        This command will first build the the POP client container including the plugins, instructing it to look for plugin components and route definitions in the `./myplugins` directory.

    !!! important "Required Files"
        The plugin directory **must contain both** `plugins.route.ts` and `plugins.env.js` (if used).  
        - `plugins.route.ts` defines how your plugin integrates with the routing system.  
        - `plugins.env.js` injects runtime configuration into your components.


By following this pattern, institutions can safely extend the POP client to meet local needs without compromising the integrity, maintainability, or upgradability of the core platform.


## Integrating with Microservices

Plugins can optionally consume APIs exposed by institution-specific microservices for:

- Fetching external or derived data.
- Displaying institution-specific reports or tools.

Follow the same API consumption best practices as with the POP API:

- Use environment variables for base URLs.
- Implement proper authentication and error handling.
- Keep plugin services modular and independent.