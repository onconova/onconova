import { Injectable, inject } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { EMPTY, Observable, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { URLs } from '../services/allauth-api.service';

@Injectable()
export class UnauthorizedInterceptor implements HttpInterceptor {
  #authService = inject(AuthService);
  #router = inject(Router);
  #messageService = inject(MessageService);

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
            // Session is no longer valid, delete session data 
            this.#authService.sessionToken.set(null);
            this.#authService.sessionUserId.set(null);
            // Redirect the user to the login page              
            this.#router.navigate(['auth', 'login']);
            // Handle the different cases, and inform the user appropriately
            if (request.url.includes(URLs.SESSIONS)) {
                // User has manually logged out
                this.#messageService.add({ severity: 'success', summary: 'Logout', detail: 'Successfully logged out' });
                return EMPTY;
            }
            if (request.url.includes(URLs.PROVIDER_TOKEN) && error.error?.meta.session_token) {
                // User is signing in for first time but lacks certain data
                this.#messageService.add({ severity: 'info', summary: 'Signup', detail: 'Additional information required to sign you up' });
                return throwError(() => error);
            } else {
                // Session is no longer valid
                this.#messageService.add({ severity: 'error', summary: 'Session expired', detail: 'Please log in again' });
                return throwError(() => error);
            }
        }
        this.#messageService.add({ severity: 'error', summary: `Server Error (HTTP 500)`, detail: error.message , sticky: true });
        console.error(error)
        return throwError(() => error);
      })
    );
  }
}