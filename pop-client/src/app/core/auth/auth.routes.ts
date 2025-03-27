import { Routes } from "@angular/router"

export const authRoutes: Routes = [
    { path: 'error', loadComponent: () => import('./pages/error/error.component').then(m => m.ErrorComponent) },
    { path: 'login', loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent) },
    { path: '**', redirectTo: '/notfound' }
]