import { Routes } from '@angular/router';

import { AuthGuard } from './core/auth/guards/auth.guard';
import { pluginRoutes } from '../plugins/plugins.routes';


function mergeRoutes(baseRoutes: Routes, overrideRoutes: Routes): Routes {
    return baseRoutes.map(baseRoute => {
      const override = overrideRoutes.find(r => r.path === baseRoute.path);
  
      if (override) {
        return {
          ...baseRoute, // Keep existing properties (e.g., guards)
          ...override, // Override properties explicitly set in the plugin
          children: baseRoute.children
            ? mergeRoutes(baseRoute.children, override.children || [])
            : override.children || baseRoute.children, // Merge children recursively
        };
      }
  
      return baseRoute; // If no override exists, keep the base route
    }).concat(
      overrideRoutes.filter(or => !baseRoutes.some(br => br.path === or.path)) // Add new plugin routes
    );
  }

const appRoutes: Routes = [
    { 
        path: 'auth', 
        loadChildren: () => import('./core/auth/auth.routes').then(m => m.authRoutes),
    },
    {
        path: '', 
        loadComponent: () => import('./core/layout/app.layout.component').then(m => m.AppLayoutComponent),
        canActivate: [AuthGuard],
        children: [
            { path: '', redirectTo: '/dashboard', pathMatch: 'full', title: 'Dashboard - POP' },
            { path: 'dashboard', loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent), title: 'Dashboard - POP' },
            { path: 'cases', 
                children: [
                    { path: 'search', loadComponent: () => import('./features/cases/case-search/case-search.component').then(m => m.CaseSearchComponent), title: 'Search cases - POP'},
                    { path: 'search/:manager', loadComponent: () => import('./features/cases/case-search/case-search.component').then(m => m.CaseSearchComponent), title: 'My cases - POP' },
                    { path: 'management/:pseudoidentifier',  loadComponent: () => import('./features/cases/case-manager/case-manager.component').then(m => m.CaseManagerComponent) , title: 'Case management - POP'},
                    { path: 'import', loadComponent: () => import('./features/cases/case-importer/case-importer.component').then(m => m.CaseImporterComponent), title: 'Import cases - POP' },
                ]
            },
            { path: 'cohorts', 
                children: [
                    { path: ':cohortId/management', loadComponent: () => import('./features/cohorts/cohort-manager/cohort-manager.component').then(m => m.CohortBuilderComponent), title: 'Cohort management - POP' },
                    { path: 'search', loadComponent: () => import('./features/cohorts/cohort-search/cohort-search.component').then(m => m.CohortSearchComponent), title: 'Search cohorts - POP'},
                    { path: 'search/:author', loadComponent: () => import('./features/cohorts/cohort-search/cohort-search.component').then(m => m.CohortSearchComponent), title: 'My cohorts - POP' },

                ]
            },
            { path: 'projects', 
                children: [
                    { path: 'search', loadComponent: () => import('./features/project-search/project-search.component').then(m => m.ProjectSearchComponent), title: 'Projects - POP'},
                    { path: ':projectId/management', loadComponent: () => import('./features/project-management/project-management.component').then(m => m.ProjectManagementComponent), title: 'Project management - POP' },
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
        loadComponent: () => import('./core/auth/components/auth.error.component').then(m => m.ErrorComponent) 
    },
    { path: '**', redirectTo: '/notfound' },
];

export const routes: Routes = mergeRoutes(appRoutes, pluginRoutes)