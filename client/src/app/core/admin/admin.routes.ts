import { Routes } from "@angular/router"

export const adminRoutes: Routes = [
    { path: 'users', loadComponent: () => import('./components/users-management/users-management.component').then(m => m.UsersManagementCompnent) },
    { path: 'users/:username', loadComponent: () => import('./components/user-details/user-details.component').then(m => m.UserDetailsComponent) },
    { path: '**', redirectTo: '/notfound' }
]