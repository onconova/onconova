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
            { path: 'dashboard', loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent) },
            { path: 'cases', 
                children: [
                    { path: 'search', loadComponent: () => import('./features/case-search/case-search.component').then(m => m.CaseBrowserComponent) },
                    { path: 'search/:manager', loadComponent: () => import('./features/case-search/case-search.component').then(m => m.CaseBrowserComponent) },
                    { path: 'management/:pseudoidentifier',  loadComponent: () => import('./features/case-manager/case-manager.component').then(m => m.CaseManagerComponent) }
                ]
            },
        ]
    },
    { 
        path: 'notfound', 
        canActivate: [AuthGuard],
        loadComponent: () => import('./core/notfound/notfound.component').then(m => m.NotfoundComponent) 
    },
    { path: '**', redirectTo: '/notfound' },
];
