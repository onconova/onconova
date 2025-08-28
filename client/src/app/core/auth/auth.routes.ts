import { Routes } from "@angular/router"

export const authRoutes: Routes = [
    { path: 'error', loadComponent: () => import('./components/auth.error.component').then(m => m.ErrorComponent), title: 'Not Found - Onconova'  },
    { path: 'login', loadComponent: () => import('./components/login.component').then(m => m.LoginComponent), title: 'Login - Onconova' },
    { path: 'signup/:provider/:session', loadComponent: () => import('./components/provider-signup.component').then(m => m.ProviderSignupComponent), title: 'Signup - Onconova'},
    { path: 'callback', loadComponent: () => import('./components/callback.component').then(m => m.AuthCallbackComponent), title: 'Signing in...' },
    { path: '**', redirectTo: '/notfound' }
]