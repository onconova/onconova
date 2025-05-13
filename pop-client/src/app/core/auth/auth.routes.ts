import { Routes } from "@angular/router"

export const authRoutes: Routes = [
    { path: 'error', loadComponent: () => import('./components/auth.error.component').then(m => m.ErrorComponent) },
    { path: 'login', loadComponent: () => import('./components/login.component').then(m => m.LoginComponent) },
    { path: '**', redirectTo: '/notfound' }
]