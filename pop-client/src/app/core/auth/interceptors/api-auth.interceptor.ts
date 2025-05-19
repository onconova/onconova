import { AuthService } from '../services/auth.service';
import { Injectable, inject } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BASE_PATH } from 'src/app/shared/openapi';

@Injectable()
export class APIAuthInterceptor implements HttpInterceptor {
  
    #authService = inject(AuthService);
    #BASE_PATH: string = inject(BASE_PATH);


    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const isApiUrl = request.url.startsWith(`${this.#BASE_PATH}/api`);
        const apiSessionToken = this.#authService.sessionToken();
        if (isApiUrl && apiSessionToken) {
            request = request.clone({
                setHeaders: {
                    'X-SESSION-TOKEN': apiSessionToken,
                },
            });
        }
        return next.handle(request);
    }
}