import { TestBed } from '@angular/core/testing';
import { UnauthorizedInterceptor } from './unauthorized.interceptor';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { URLs } from '../services/allauth-api.service';
import { HTTP_INTERCEPTORS, HttpClient, HttpErrorResponse, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { map, of, throwError } from 'rxjs';
import { signal } from '@angular/core';

describe('UnauthorizedInterceptor', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let router: jasmine.SpyObj<Router>;
  let messageService: jasmine.SpyObj<MessageService>;
  let authService: AuthService;
  let authServiceStub: Partial<AuthService>;


  beforeEach(() => {

    authServiceStub = {
        sessionToken: signal('mock-session-token'),
        sessionUserId: signal('mock-session-user-id')
      };
  

    router = jasmine.createSpyObj('Router', ['navigate']);
    messageService = jasmine.createSpyObj('MessageService', ['add']);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: authServiceStub },
        { provide: Router, useValue: router },
        { provide: MessageService, useValue: messageService },
        {
          provide: HTTP_INTERCEPTORS,
          useClass: UnauthorizedInterceptor,
          multi: true
        }
      ]
    });

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    authService = TestBed.inject(AuthService);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should not affect anything if there is no HTTP error', () => {
    http.get('/api/other-endpoint').subscribe({
        complete: () => {
            expect(authService.sessionToken()).not.toBeNull();
            expect(authService.sessionUserId()).not.toBeNull();
            expect(router.navigate).not.toHaveBeenCalledWith(['auth', 'login']);
        }
    });

    const req = httpMock.expectOne('/api/other-endpoint');
    req.flush({});
  });


  it('should handle 401 responses by clearing session and redirecting to login page', () => {
    http.get(URLs.SESSIONS).pipe(
        map(() => new HttpErrorResponse({ status: 401, statusText: 'Unauthorized' }))
      ).subscribe({
      next: () => fail('request should have raised an error'),
      complete: () => {
        expect(authService.sessionToken()).toBeNull();
        expect(authService.sessionUserId()).toBeNull();
        expect(router.navigate).toHaveBeenCalledWith(['auth', 'login']);
      }
    });

    const req = httpMock.expectOne(URLs.SESSIONS);
    req.flush({}, { status: 401, statusText: 'Unauthorized' });
  });

  it('should pass through non-401 errors unchanged', () => {
    http.get('/api/other-endpoint').pipe(
        map(() => new HttpErrorResponse({ status: 500, statusText: 'Server error' }))
    ).subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(500);
      }
    });

    const req = httpMock.expectOne('/api/other-endpoint');
    req.flush({}, { status: 500, statusText: 'Server error' });
  });
});
