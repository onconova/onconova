import { Routes } from '@angular/router';

// Dynamically imported plugin components
export const pluginRoutes: Routes = [
    
    // Example adding new path: 
    // {
    //     path: 'custom', 
    //     children: [
    //         { path: 'new-page', loadComponent: () => import('./new-page/new-page.component').then(m => m.NewPageComponent) }
    //     ],
    // }

    // Example overriding exting path: 
    // {
    //     path: '', 
    //     children: [
    //         { path: 'dashboard', loadComponent: () => import('./custom-dashboard/custom-dashboard.component').then(m => m.CustomDashboardComponent) }
    //     ],
    // }
    
];