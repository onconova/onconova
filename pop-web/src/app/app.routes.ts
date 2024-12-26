import { Routes } from '@angular/router';

import { NotfoundComponent } from './core/notfound/notfound.component';
import { AppLayoutComponent } from "./core/layout/app.layout.component";
import { AuthGuard } from './core/auth/guards/auth.guard';

import { CaseBrowserComponent } from './features/case-browser/case-browser.component';
import { CaseManagerComponent } from './features/case-manager/case-manager.component';


export const routes: Routes = [
    
    { 
        path: 'login', 
        loadChildren: () => import('./core/auth/pages/login/login.module').then(m => m.LoginModule),
    },
    {
        path: '', 
        component: AppLayoutComponent,
        canActivate: [AuthGuard],
        children: [
            { path: 'dashboard', loadChildren: () => import('./features/dashboard/dashboard.module').then(m => m.DashboardModule) },
            { path: 'cases', 
                children: [
                    { path: '', component: CaseBrowserComponent},
                    { path: ':pseudoidentifier',  component: CaseManagerComponent }
                ]
            },
        ]
    },
    { path: 'notfound', component: NotfoundComponent },
    { path: '**', redirectTo: '/notfound' },
];
