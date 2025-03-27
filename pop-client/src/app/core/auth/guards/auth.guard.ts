import { inject, Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import {Observable} from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class AuthGuard implements CanActivate {

    private readonly router: Router = inject(Router);
    private readonly auth: AuthService = inject(AuthService);

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
        return new Promise( (resolve, reject) => {
            this.auth.checkAuthentication().then(
                (isAuthenticated) => {
                    if (isAuthenticated) {
                        this.auth.checkUserExists()
                        resolve(true)
                    } else {
                        this.router.navigate(['auth/login'], { queryParams: { next: state.url } });
                        resolve(false)
                    }   
                }
            ).catch(
                (error) => {
                    reject(error)
                }
            )         
        })
    }
}