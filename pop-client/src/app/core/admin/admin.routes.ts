import { Routes } from "@angular/router"

export const adminRoutes: Routes = [
    // { path: 'users', loadComponent: () => import('./components/users-management/users-management.component').then(m => m.UsersManagementCompnent) },
    { path: '**', redirectTo: '/notfound' }
]