import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { AllAuthApiService } from './allauth-api.service';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { of, throwError } from 'rxjs';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { BASE_PATH } from 'onconova-api-client';
import { AppConfigService } from 'src/app/app.config.service';
import { Location } from '@angular/common';

describe('AuthService', () => {
    let service: AuthService;
    let routerSpy: jasmine.SpyObj<Router>;
    let locationSpy: jasmine.SpyObj<Location>;
    let configService: AppConfigService;
    let redirectSpy: jasmine.Spy<jasmine.Func>;
    let allAuthApiServiceSpy: jasmine.SpyObj<AllAuthApiService>;
    let configServiceSpy: jasmine.SpyObj<AppConfigService>;
    let messageServiceSpy: jasmine.SpyObj<MessageService>;
    let location: Location;
    beforeEach(async () => {
        allAuthApiServiceSpy = jasmine.createSpyObj('AllAuthApiService', ['login','logoutCurrentSession','authenticateWithProviderToken']);
        allAuthApiServiceSpy.logoutCurrentSession.and.returnValue(of({}));

        routerSpy = jasmine.createSpyObj('Router', ['navigateByUrl','navigate']);
        routerSpy.navigateByUrl.and.resolveTo(true);
        routerSpy.navigate.and.resolveTo(true);

        locationSpy = jasmine.createSpyObj('Location', ['go']);
        locationSpy.go.and.resolveTo();

        messageServiceSpy = jasmine.createSpyObj('MessageService', ['add']);

        configServiceSpy = jasmine.createSpyObj('AppConfigService', ['getAppConfig', 'getIdentityProviderClientId','getOpenIdAuthorizationEndpoint']);
        configServiceSpy.BASE_PATH = 'http://localhost:443';

        await TestBed.configureTestingModule({
        providers: [
            provideHttpClient(withInterceptorsFromDi()),
            provideHttpClientTesting(),
            AuthService,
            { provide: AppConfigService, useValue: configServiceSpy },
            { provide: AllAuthApiService, useValue: allAuthApiServiceSpy },
            { provide: Router, useValue: routerSpy },
            { provide: MessageService, useValue: messageServiceSpy },
            { provide: BASE_PATH, useValue: 'http://localhost:443' },
        ],
        });
        location = TestBed.inject(Location);
        service = TestBed.inject(AuthService);
        configService = TestBed.inject(AppConfigService);

        redirectSpy = spyOn(service, 'redirect');
        redirectSpy.and.returnValue(null);

    });

    // login() tests

    it('#login should login successfully with valid credentials', () => {
        const credentials = { username: 'test', password: 'test' };
        const response = { meta: { session_token: 'token' }, data: { user: { id: '1' } } };
        allAuthApiServiceSpy.login.and.returnValue(of(response));

        service.login(credentials);

        expect(service.sessionToken()).toBe('token');
        expect(service.sessionUserId()).toBe('1');
        expect(routerSpy.navigateByUrl).toHaveBeenCalledWith('/');
    });

    it('#login should login successfully with valid credentials and next URL', () => {
        const credentials = { username: 'test', password: 'test' };
        const nextUrl = '/next';
        const response = { meta: { session_token: 'token' }, data: { user: { id: '1' } } };
        allAuthApiServiceSpy.login.and.returnValue(of(response));

        service.login(credentials, nextUrl);

        expect(service.sessionToken()).toBe('token');
        expect(service.sessionUserId()).toBe('1');
        expect(routerSpy.navigateByUrl).toHaveBeenCalledWith(nextUrl);
    });

    it('#login should handle failure with invalid credentials (401 status)', () => {
        const credentials = { username: 'test', password: 'test' };
        const error = { status: 401, error: { detail: 'Invalid credentials' } };
        const nextUrl = '/next';
        allAuthApiServiceSpy.login.and.returnValue(throwError(error));

        service.login(credentials);

        expect(service.sessionToken()).toBeNull();
        expect(service.sessionUserId()).toBeNull();
        expect(routerSpy.navigateByUrl).not.toHaveBeenCalledWith(nextUrl);

    });

    it('#login should handle failure with missing credentials (400 status)', () => {
        const credentials = { username: 'test', password: 'test' };
        const error = { status: 400, error: { detail: 'Please provide a username and a password' } };
        const nextUrl = '/next';
        allAuthApiServiceSpy.login.and.returnValue(throwError(error));

        service.login(credentials);

        expect(service.sessionToken()).toBeNull();
        expect(service.sessionUserId()).toBeNull();
        expect(routerSpy.navigateByUrl).not.toHaveBeenCalledWith(nextUrl);
    });

    it('#login should handle login failure with network error (other status)', () => {
        const credentials = { username: 'test', password: 'test' };
        const error = { status: 500, error: { detail: 'Network error' } };
        const nextUrl = '/next';
        allAuthApiServiceSpy.login.and.returnValue(throwError(error));

        service.login(credentials);

        expect(service.sessionToken()).toBeNull();
        expect(service.sessionUserId()).toBeNull();
        expect(routerSpy.navigateByUrl).not.toHaveBeenCalledWith(nextUrl);

    });

    // logout() tests

    it('#logout should logout when there is an active user session', () => {
        service.sessionToken.set('token')
        service.logout();
        expect(allAuthApiServiceSpy.logoutCurrentSession).toHaveBeenCalledTimes(1);
        expect(service.sessionToken()).toBeNull();
        expect(service.sessionUserId()).toBeNull();
    });

    it('#logout should not logout and should throw an error when there is no active user session', () => {
        service.sessionToken.set(null)
        expect(() => service.logout()).toThrowError('There is no active session to log out');
        expect(messageServiceSpy.add).toHaveBeenCalledTimes(1);
        expect(messageServiceSpy.add).toHaveBeenCalledWith({ severity: 'error', summary: 'Logout failed', detail: 'There is no active user session.' });
        expect(allAuthApiServiceSpy.logoutCurrentSession).not.toHaveBeenCalled();
    });

    // initiateOpenIdAuthentication() tests

    it('#initiateOpenIdAuthentication should throw an error when the provider ID is invalid', () => {
        expect(() => service.initiateOpenIdAuthentication('')).toThrowError('Invalid provider ID');
    });

    it('#initiateOpenIdAuthentication should throw an error when the client ID is not found', () => {    
        configServiceSpy.getIdentityProviderClientId.and.returnValue(null);
        expect(() => service.initiateOpenIdAuthentication('providerId')).toThrowError('No client ID found for provider providerId');
    });

    it('#initiateOpenIdAuthentication should construct the authorization URL correctly', () => {
        configServiceSpy.getIdentityProviderClientId.and.returnValue('clientId');
        configServiceSpy.getOpenIdAuthorizationEndpoint.and.returnValue(of('https://example.com/authorize'));
        expect(service.initiateOpenIdAuthentication('providerId')).toBeUndefined();
        expect(redirectSpy).toHaveBeenCalled();

    });

    it('#initiateOpenIdAuthentication should redirect to the authorization URL', () => {
        configServiceSpy.getIdentityProviderClientId.and.returnValue('clientId');
        configServiceSpy.getOpenIdAuthorizationEndpoint.and.returnValue(of('https://example.com/authorize'));
        expect(service.initiateOpenIdAuthentication('providerId')).toBeUndefined();
        expect(redirectSpy).toHaveBeenCalled();
    });


    it('#handleOpenIdAuthCallback should authenticate successfully with access token', () => {
        const credentialsSpy = spyOn(service, 'getCurrentURLOpenIdCredentials');
        credentialsSpy.and.returnValue({accessToken: '123abc', idToken: null, authorizationCode: null, state: 'abc123'});
        const response = { meta: { session_token: 'session-token' }, data: { user: { id: 'user-id' } } };
        allAuthApiServiceSpy.authenticateWithProviderToken.and.returnValue(of(response));


        service.handleOpenIdAuthCallback();

        expect(routerSpy.navigate).toHaveBeenCalledWith(['/dashboard']);
        expect(service.sessionToken()).toBe('session-token');
        expect(service.sessionUserId()).toBe('user-id');
    });

    it('#handleOpenIdAuthCallback should authenticate successfully with ID token', () => {
        const credentialsSpy = spyOn(service, 'getCurrentURLOpenIdCredentials');
        credentialsSpy.and.returnValue({accessToken: null, idToken: '456def', authorizationCode: null, state: 'abc123'});
        const response = { meta: { session_token: 'session-token' }, data: { user: { id: 'user-id' } } };
        allAuthApiServiceSpy.authenticateWithProviderToken.and.returnValue(of(response));

        service.handleOpenIdAuthCallback();

        expect(routerSpy.navigate).toHaveBeenCalledWith(['/dashboard']);
        expect(service.sessionToken()).toBe('session-token');
        expect(service.sessionUserId()).toBe('user-id');
    });

    it('#handleOpenIdAuthCallback should authenticate with authorization code', () => {
        const credentialsSpy = spyOn(service, 'getCurrentURLOpenIdCredentials');
        credentialsSpy.and.returnValue({accessToken: null, idToken: null, authorizationCode: '789ghi', state: 'abc123'});
        const response = { access_token: 'access-token', id_token: 'id-token' };
        allAuthApiServiceSpy.authenticateWithProviderToken.and.returnValue(of(response));

        service.handleOpenIdAuthCallback();

    });

    it('#handleOpenIdAuthCallback should handle error when no credentials are found', () => {
        const credentialsSpy = spyOn(service, 'getCurrentURLOpenIdCredentials');
        credentialsSpy.and.returnValue({accessToken: null, idToken: null, authorizationCode: null, state: null});

        service.handleOpenIdAuthCallback();

        expect(routerSpy.navigate).toHaveBeenCalledWith(['/auth/login']);
    });

    it('#handleOpenIdAuthCallback should handle error when authentication fails with 401 status', () => {
        const credentialsSpy = spyOn(service, 'getCurrentURLOpenIdCredentials');
        credentialsSpy.and.returnValue({accessToken: '123abc', idToken: '456def', authorizationCode: '789ghi', state: 'abc123'});
        const response = { status: 401, error: { meta: { session_token: 'session-token' } } };
        allAuthApiServiceSpy.authenticateWithProviderToken.and.returnValue(throwError(()=>response));

        service.handleOpenIdAuthCallback();

        expect(routerSpy.navigate).toHaveBeenCalledWith(['/auth/signup', null, 'session-token']);
    });

    it('#handleOpenIdAuthCallback should handle error when authentication fails with other status', () => {
        const credentialsSpy = spyOn(service, 'getCurrentURLOpenIdCredentials');
        credentialsSpy.and.returnValue({accessToken: '123abc', idToken: '456def', authorizationCode: '789ghi', state: 'abc123'});
        const response = { status: 500, error: 'Internal Server Error' };
        allAuthApiServiceSpy.authenticateWithProviderToken.and.returnValue(throwError(()=>response));

        service.handleOpenIdAuthCallback();

        expect(routerSpy.navigate).toHaveBeenCalledWith(['/auth/login']);
        });

});