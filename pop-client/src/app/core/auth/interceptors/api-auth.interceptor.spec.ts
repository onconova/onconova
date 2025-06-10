import { TestBed } from '@angular/core/testing';
import { APIAuthInterceptor } from './api-auth.interceptor';
import { AuthService } from '../services/auth.service';
import { BASE_PATH } from 'pop-api-client';
import { HTTP_INTERCEPTORS, HttpClient, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { signal } from '@angular/core';

describe('APIAuthInterceptor', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let authService: AuthService;
  let authServiceStub: Partial<AuthService>;


  const basePath = 'http://localhost:4200';

  beforeEach(() => {

    authServiceStub = {
      sessionToken: signal(null)
    };

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptorsFromDi()), 
        provideHttpClientTesting(),
        { provide: AuthService, useValue: authServiceStub },
        { provide: BASE_PATH, useValue: basePath },
        {
          provide: HTTP_INTERCEPTORS,
          useClass: APIAuthInterceptor,
          multi: true
        },
      ]
    });

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    authService = TestBed.inject(AuthService);
  
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should add authorization header for POP API requests if token exists', () => {
    authService.sessionToken.set('mock-session-token');
    http.get(`${basePath}/api/users`).subscribe();

    const req = httpMock.expectOne(`${basePath}/api/users`);
    expect(req.request.headers.get('X-SESSION-TOKEN')).toBe('mock-session-token');
    req.flush({});
  });

  it('should not add authorization header for non-POP API requests', () => {
    http.get(`${basePath}/assets/logo.png`).subscribe();

    const req = httpMock.expectOne(`${basePath}/assets/logo.png`);
    expect(req.request.headers.has('X-SESSION-TOKEN')).toBeFalse();
    req.flush({});
  });

  it('should not add authorization header if session token does not exist', () => {

    http.get(`${basePath}/api/data`).subscribe();

    const req = httpMock.expectOne(`${basePath}/api/data`);
    expect(req.request.headers.has('X-SESSION-TOKEN')).toBeFalse();
    req.flush({});
  });
});
