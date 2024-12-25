import { Routes } from '@angular/router';

import { NotfoundComponent } from './notfound/notfound.component';
import { AppLayoutComponent } from "./layout/app.layout.component";
import { AuthGuard } from './auth/auth.guard';

import { CaseBrowserComponent } from './case-browser/case-browser.component';
import { CaseManagerComponent } from './case-manager/case-manager.component';


export const routes: Routes = [
    
    { 
        path: 'login', 
        loadChildren: () => import('./auth/login/login.module').then(m => m.LoginModule),
    },
    {
        path: '', 
        component: AppLayoutComponent,
        canActivate: [AuthGuard],
        children: [
            { path: 'dashboard', loadChildren: () => import('./dashboard/dashboard.module').then(m => m.DashboardModule) },
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
