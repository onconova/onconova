import { inject, Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor, HttpInterceptorFn, HttpHandlerFn } from '@angular/common/http';
import { Observable, from, filter, mergeMap } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

export const authInterceptor: HttpInterceptorFn = (request: HttpRequest<any>, next: HttpHandlerFn) => {
    const auth = inject(AuthService);
    const router = inject(Router);
    if (request.url.includes('/auth/token')) {
        return next(request);
    } 
    return from(auth.checkAuthentication()).pipe(
        mergeMap(
            (isAuthenticated) => {
            const isApiUrl = request.url.startsWith('https://localhost:4443/api');
            if (!isAuthenticated) (
                router.navigate(['login'])
            )
            if (isApiUrl) {
                request = request.clone({
                    setHeaders: { Authorization: `Bearer ${auth.getAccessToken()}` }
                });
            }
            return next(request);
        })
    )
  };
