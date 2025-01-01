import { inject, Injectable } from '@angular/core';
import { Router, CanActivate } from '@angular/router';
import { AuthService } from '../services/auth.service';
import {Observable} from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class AuthGuard implements CanActivate {

    private readonly router: Router = inject(Router);
    private readonly auth: AuthService = inject(AuthService);

    canActivate(): Observable<boolean> | Promise<boolean> | boolean {
        return new Promise( (resolve, reject) => {
            this.auth.checkAuthentication().then(
                (isAuthenticated) => {
                    if (isAuthenticated) {
                        resolve(true)
                    } else {
                        this.router.navigate(['auth/login']);
                        resolve(false)
                    }   
                })         
        })
    }

}