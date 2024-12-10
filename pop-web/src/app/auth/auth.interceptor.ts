import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
    constructor(
        private auth: AuthService,
        private router: Router) { }

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        // add auth header with jwt if account is logged in and request is to the api url
        const isAuthenticated = this.auth.isAuthenticated();
        const isApiUrl = request.url.startsWith('https://localhost:4443/api');
        if (isAuthenticated && isApiUrl) {
            request = request.clone({
                setHeaders: { Authorization: `Bearer ${this.auth.getToken()}` }
            });
        } else if (!isAuthenticated) (
            this.router.navigate(['login'])
        )

        return next.handle(request);
    }
}