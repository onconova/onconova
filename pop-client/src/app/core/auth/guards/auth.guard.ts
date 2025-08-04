import { inject, Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
    providedIn: 'root',
})
export class AuthGuard implements CanActivate {

    readonly #router: Router = inject(Router);
    readonly #auth: AuthService = inject(AuthService);

    /**
     * Determines whether the user can activate the route.
     *
     * @param route The route for which we're checking access.
     * @param state The state of the router.
     * @returns A promise that resolves to true if the user can access the route, false otherwise.
     */
    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Promise<boolean> {
        // If the user is authenticated, we allow access to the route.
        if (this.#auth.isAuthenticated()) {
            return Promise.resolve(true);
        } else {
            // Otherwise, redirect the user to the login page, passing the current route as a query parameter.
            this.#router.navigate(['auth/login'], { queryParams: { next: state.url } });
            // We don't want to let the user access the route, so we resolve to false.
            return Promise.resolve(false);
        }
    }
}