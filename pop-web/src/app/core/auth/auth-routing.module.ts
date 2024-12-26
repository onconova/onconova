import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';

@NgModule({
    imports: [RouterModule.forChild([
        { path: 'error', loadChildren: () => import('./pages/error/error.module').then(m => m.ErrorModule) },
        { path: 'access', loadChildren: () => import('./pages/access/access.module').then(m => m.AccessModule) },
        { path: 'login', loadChildren: () => import('./pages/login/login.module').then(m => m.LoginModule) },
        { path: '**', redirectTo: '/notfound' }
    ])],
    exports: [RouterModule]
})
export class AuthRoutingModule { }
