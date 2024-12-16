import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable, from, filter, mergeMap } from 'rxjs';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
    constructor(
        private auth: AuthService,
        private router: Router) { }

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        if (request.url.includes('/auth/token')) {
            return next.handle(request);
        } 
        return from(this.auth.checkAuthentication()).pipe(
            mergeMap(
                (isAuthenticated) => {
                const isApiUrl = request.url.startsWith('https://localhost:4443/api');
                if (!isAuthenticated) (
                    this.router.navigate(['login'])
                )
                if (isApiUrl) {
                    request = request.clone({
                        setHeaders: { Authorization: `Bearer ${this.auth.getAccessToken()}` }
                    });
                }
                return next.handle(request);
            })
        )
    }
}