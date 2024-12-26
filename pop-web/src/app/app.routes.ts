import { Routes } from '@angular/router';

import { AuthGuard } from './core/auth/guards/auth.guard';

export const routes: Routes = [
    
    { 
        path: 'auth', 
        loadChildren: () => import('./core/auth/auth.routes').then(m => m.authRoutes),
    },
    {
        path: '', 
        loadComponent: () => import('./core/layout/app.layout.component').then(m => m.AppLayoutComponent),
        canActivate: [AuthGuard],
        children: [
            { path: 'dashboard', loadChildren: () => import('./features/dashboard/dashboard.module').then(m => m.DashboardModule) },
            { path: 'cases', 
                children: [
                    { path: '', loadComponent: () => import('./features/case-browser/case-browser.component').then(m => m.CaseBrowserComponent) },
                    { path: ':pseudoidentifier',  loadComponent: () => import('./features/case-manager/case-manager.component').then(m => m.CaseManagerComponent) }
                ]
            },
        ]
    },
    { path: 'notfound', loadComponent: () => import('./core/notfound/notfound.component').then(m => m.NotfoundComponent) },
    { path: '**', redirectTo: '/notfound' },
];
