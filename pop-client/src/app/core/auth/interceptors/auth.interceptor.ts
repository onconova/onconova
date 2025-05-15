import { AuthService } from '../services/auth.service';
import { Injectable, inject } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BASE_PATH } from 'src/app/shared/openapi';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  
    private authService = inject(AuthService);

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    const basePath: string = inject(BASE_PATH);
    const router = inject(Router);

    if (request.url.endsWith('/auth/login')) {
        return next.handle(request);
    }

        const isApiUrl = request.url.startsWith(`${basePath}/api`);
        if (!this.authService.isAuthenticated()) (
            router.navigate(['auth','login'])
        )
        if (isApiUrl) {
            request = request.clone({
                setHeaders: {
                    'X-SESSION-TOKEN': this.authService.sessionToken() as string,
                },
            });
            return next.handle(request);
        }
        return next.handle(request);
    }
  }