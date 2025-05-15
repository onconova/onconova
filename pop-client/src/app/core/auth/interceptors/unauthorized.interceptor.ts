import { Injectable, inject } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService, LOGOUT_ENDPOINT } from '../services/auth.service';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';

@Injectable()
export class AuthErrorInterceptor implements HttpInterceptor {
  private authService = inject(AuthService);
  private router = inject(Router);
  private messageService = inject(MessageService);

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Session is no longer valid
            this.authService.sessionToken.set(null);
            this.authService.sessionUserId.set(null);
            if (req.url.includes(LOGOUT_ENDPOINT)) {
                this.messageService.add({ severity: 'success', summary: 'Logout', detail: 'Successfully logged out' });
            } else {
                this.messageService.add({ severity: 'error', summary: 'Session expired', detail: 'Please log in again' });
            }
            this.router.navigate(['/']);
          // Optionally display a message or toast notification here
        }
        return throwError(() => error);
      })
    );
  }
}