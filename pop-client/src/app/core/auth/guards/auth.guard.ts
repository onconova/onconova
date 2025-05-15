import { inject, Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import {Observable} from 'rxjs';
import { MessageService } from 'primeng/api';

@Injectable({
    providedIn: 'root',
})
export class AuthGuard implements CanActivate {

    private readonly router: Router = inject(Router);
    private readonly auth: AuthService = inject(AuthService);
    private readonly messageService = inject(MessageService);

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
        return new Promise( (resolve, reject) => {
                if (this.auth.isAuthenticated()) {
                    resolve(true)
                } else {
                    this.router.navigate(['auth/login'], { queryParams: { next: state.url } });
                    resolve(false)
                }                     
            })    
    }
}