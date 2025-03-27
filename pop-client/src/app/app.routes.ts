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
            { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
            { path: 'dashboard', loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent) },
            { path: 'cases', 
                children: [
                    { path: 'search', loadComponent: () => import('./features/cases/case-search/case-search.component').then(m => m.CaseBrowserComponent) },
                    { path: 'search/:manager', loadComponent: () => import('./features/cases/case-search/case-search.component').then(m => m.CaseBrowserComponent) },
                    { path: 'management/:pseudoidentifier',  loadComponent: () => import('./features/cases/case-manager/case-manager.component').then(m => m.CaseManagerComponent) },
                    { path: 'import', loadComponent: () => import('./features/cases/case-importer/case-importer.component').then(m => m.CaseImporterComponent) },
                ]
            },
            { path: 'cohorts', 
                children: [
                    { path: ':cohortId/management', loadComponent: () => import('./features/cohorts/cohort-builder/cohort-builder.component').then(m => m.CohortBuilderComponent) },
                    { path: 'search', loadComponent: () => import('./features/cohorts/cohort-search/cohort-search.component').then(m => m.CohortSearchComponent) },
                    { path: 'search/:currentUser', loadComponent: () => import('./features/cohorts/cohort-search/cohort-search.component').then(m => m.CohortSearchComponent) },
                ]
            },
            { path: 'admin', 
                loadChildren: () => import('./core/admin/admin.routes').then(m => m.adminRoutes),
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
