import { TestBed } from '@angular/core/testing';
import { AuthGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';
import { ActivatedRouteSnapshot, provideRouter, Router, RouterStateSnapshot, withComponentInputBinding } from '@angular/router';
import { fakeAsync, tick } from '@angular/core/testing';

describe('AuthGuard', () => {
  let authGuard: AuthGuard;
  let authService: jasmine.SpyObj<AuthService>;
  let router: Router;

  beforeEach(async () => {
    authService = jasmine.createSpyObj('AuthService', ['isAuthenticated']);

    await TestBed.configureTestingModule({
      providers: [
        AuthGuard,
        provideRouter([], withComponentInputBinding()),
        { provide: AuthService, useValue: authService }
      ]
    });

    authGuard = TestBed.inject(AuthGuard);
    router = TestBed.inject(Router);

    spyOn(router, 'navigate').and.resolveTo(true); // mock router.navigate
  });

  it('should allow access to route when user is authenticated', async () => {
    authService.isAuthenticated.and.returnValue(true);

    const route = new ActivatedRouteSnapshot();
    const state = { url: '/some-url' } as RouterStateSnapshot;

    const result = await authGuard.canActivate(route, state);

    expect(result).toBe(true);
  });


  it('should redirect to login page when user is not authenticated', fakeAsync(() => {
    authService.isAuthenticated.and.returnValue(false);
  
    const route = new ActivatedRouteSnapshot();
    const state = { url: '/some-url' } as RouterStateSnapshot;
  
    let result: boolean | undefined;
    authGuard.canActivate(route, state).then(res => {
      result = res;
    })
  
    tick(); // flush microtasks
  
    expect(router.navigate).toHaveBeenCalledWith(['auth/login'], { queryParams: { next: state.url } });
    expect(result).toBe(false);
  }));
});
