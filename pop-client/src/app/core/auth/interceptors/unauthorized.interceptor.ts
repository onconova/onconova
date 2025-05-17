import { Injectable, inject } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { EMPTY, Observable, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { URLs } from '../allauth-api.service';

@Injectable()
export class AuthErrorInterceptor implements HttpInterceptor {
  private authService = inject(AuthService);
  private router = inject(Router);
  private messageService = inject(MessageService);

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
            this.authService.sessionToken.set(null);
            this.authService.sessionUserId.set(null);
            this.router.navigate(['auth', 'login']);
            if (req.url.includes(URLs.SESSIONS)) {
                // User has manually logged out
                this.messageService.add({ severity: 'success', summary: 'Logout', detail: 'Successfully logged out' });
                return EMPTY;
            } else {
                // Session is no longer valid
                this.messageService.add({ severity: 'error', summary: 'Session expired', detail: 'Please log in again' });
                return throwError(() => error);
            }
        }
        return throwError(() => error);
      })
    );
  }
}