import { RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { NotfoundComponent } from './notfound/notfound.component';
import { AppLayoutComponent } from "./layout/app.layout.component";
import { AuthGuard } from './auth/auth.guard';

import { CaseBrowserComponent } from './case-browser/case-browser.component';
import { CaseManagerComponent } from './case-manager/case-manager.component';

@NgModule({
    imports: [
        RouterModule.forRoot([
            { 
                path: 'login', 
                loadChildren: () => import('./auth/login/login.module').then(m => m.LoginModule),
            },
            {
                path: '', component: AppLayoutComponent,
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
        ], { 
            scrollPositionRestoration: 'enabled', 
            anchorScrolling: 'enabled', 
            onSameUrlNavigation: 'reload',
            bindToComponentInputs: true,
        })
    ],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
