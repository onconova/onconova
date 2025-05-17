
export interface AuthenticationMeta {
  session_token?: string;
  access_token?: string;
  is_authenticated: boolean;
}


export interface AllAuthResponse {
  status: string;
  data?: any | any[]; 
  errors?: any[];
  meta?: AuthenticationMeta;
}

export interface AccountConfiguration {
  login_methods?: string[];
  is_open_for_signup: boolean;
  email_verification_by_code_enabled: boolean;
  login_by_code_enabled: boolean;
  password_reset_by_code_enabled?: boolean;
}

export interface SocialAccountConfiguration {
  description: string;
  providers: ProviderConfig[];
}

export interface ProviderConfig {
  id: string;
  name: string;
  client_id?: string;
  openid_configuration_url?: string;
  flows: ('provider_redirect' | 'provider_token')[];
}

export interface MFAConfiguration {
  supported_types: string[];  // assuming an array of strings for MFA types (e.g., ['totp', 'sms'])
}

export interface UserSessionsConfiguration {
  track_activity: boolean;
}

export interface AllAuthConfiguration {
  account: AccountConfiguration;
  socialaccount?: SocialAccountConfiguration;
  mfa?: MFAConfiguration;
  usersessions?: UserSessionsConfiguration;
}

export const Client = Object.freeze({
  APP: 'app',
  BROWSER: 'browser'
})

export const settings = {
  client: Client.APP,
  baseUrl: `api/allauth/${Client.BROWSER}/v1`,
  withCredentials: false
}

const ACCEPT_JSON = {
  accept: 'application/json'
}

export const AuthProcess = Object.freeze({
  LOGIN: 'login',
  CONNECT: 'connect'
})

export const Flows = Object.freeze({
  LOGIN: 'login',
  LOGIN_BY_CODE: 'login_by_code',
  MFA_AUTHENTICATE: 'mfa_authenticate',
  MFA_REAUTHENTICATE: 'mfa_reauthenticate',
  MFA_TRUST: 'mfa_trust',
  MFA_WEBAUTHN_SIGNUP: 'mfa_signup_webauthn',
  PASSWORD_RESET_BY_CODE: 'password_reset_by_code',
  PROVIDER_REDIRECT: 'provider_redirect',
  PROVIDER_SIGNUP: 'provider_signup',
  REAUTHENTICATE: 'reauthenticate',
  SIGNUP: 'signup',
  VERIFY_EMAIL: 'verify_email',
})

export const URLs = Object.freeze({
  // Meta
  CONFIG: '/config',

  // Account management
  CHANGE_PASSWORD: '/account/password/change',
  EMAIL: '/account/email',
  PROVIDERS: '/account/providers',

  // Account management: 2FA
  AUTHENTICATORS: '/account/authenticators',
  RECOVERY_CODES: '/account/authenticators/recovery-codes',
  TOTP_AUTHENTICATOR: '/account/authenticators/totp',

  // Auth: Basics
  LOGIN: '/auth/login',
  REQUEST_LOGIN_CODE: '/auth/code/request',
  CONFIRM_LOGIN_CODE: '/auth/code/confirm',
  SESSION: '/auth/session',
  REAUTHENTICATE: '/auth/reauthenticate',
  REQUEST_PASSWORD_RESET: '/auth/password/request',
  RESET_PASSWORD: '/auth/password/reset',
  SIGNUP: '/auth/signup',
  VERIFY_EMAIL: '/auth/email/verify',

  // Auth: 2FA
  MFA_AUTHENTICATE: '/auth/2fa/authenticate',
  MFA_REAUTHENTICATE: '/auth/2fa/reauthenticate',
  MFA_TRUST: '/auth/2fa/trust',

  // Auth: Social
  PROVIDER_SIGNUP: '/auth/provider/signup',
  REDIRECT_TO_PROVIDER: '/auth/provider/redirect',
  PROVIDER_TOKEN: '/auth/provider/token',

  // Auth: Sessions
  SESSIONS: '/auth/sessions',

  // Auth: WebAuthn
  REAUTHENTICATE_WEBAUTHN: '/auth/webauthn/reauthenticate',
  AUTHENTICATE_WEBAUTHN: '/auth/webauthn/authenticate',
  LOGIN_WEBAUTHN: '/auth/webauthn/login',
  SIGNUP_WEBAUTHN: '/auth/webauthn/signup',
  WEBAUTHN_AUTHENTICATOR: '/account/authenticators/webauthn'
})

export const AuthenticatorType = Object.freeze({
  TOTP: 'totp',
  RECOVERY_CODES: 'recovery_codes',
  WEBAUTHN: 'webauthn'
})

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map, Observable, tap } from 'rxjs'

@Injectable({
  providedIn: 'root'
})
export class AllAuthApiService {

  private readonly baseUrl = '/api/allauth/app/v1';

  private readonly httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  // Meta
  getConfig(): Observable<AllAuthConfiguration> {
    return this.http.get<AllAuthResponse>(`${this.baseUrl}/config`, this.httpOptions).pipe(map((response: AllAuthResponse) => response.data), tap(() => console.log("RETURNS")));
  }

  // Account management
  changePassword(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/account/password/change`, data, this.httpOptions);
  }

  getEmail(): Observable<any> {
    return this.http.get(`${this.baseUrl}/account/email`, this.httpOptions);
  }

  getProviders(): Observable<any> {
    return this.http.get(`${this.baseUrl}/account/providers`, this.httpOptions);
  }

  // Account management: 2FA
  getAuthenticators(): Observable<any> {
    return this.http.get(`${this.baseUrl}/account/authenticators`, this.httpOptions);
  }

  getRecoveryCodes(): Observable<any> {
    return this.http.get(`${this.baseUrl}/account/authenticators/recovery-codes`, this.httpOptions);
  }

  getTotpAuthenticator(): Observable<any> {
    return this.http.get(`${this.baseUrl}/account/authenticators/totp`, this.httpOptions);
  }

  // Auth: Basics
  login(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/login`, data, this.httpOptions);
  }

  requestLoginCode(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/code/request`, data, this.httpOptions);
  }

  confirmLoginCode(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/code/confirm`, data, this.httpOptions);
  }

  getSession(): Observable<any> {
    return this.http.get(`${this.baseUrl}/auth/session`, this.httpOptions);
  }

  reauthenticate(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/reauthenticate`, data, this.httpOptions);
  }

  requestPasswordReset(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/password/request`, data, this.httpOptions);
  }

  resetPassword(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/password/reset`, data, this.httpOptions);
  }

  signup(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/signup`, data, this.httpOptions);
  }

  verifyEmail(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/email/verify`, data, this.httpOptions);
  }

  // Auth: 2FA
  mfaAuthenticate(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/2fa/authenticate`, data, this.httpOptions);
  }

  mfaReauthenticate(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/2fa/reauthenticate`, data, this.httpOptions);
  }

  mfaTrust(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/2fa/trust`, data, this.httpOptions);
  }


  // Auth: Social
  providerSignup(data: any, headers: any = {}): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/provider/signup`, data, {headers: new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...headers
    })});
  }

  getproviderSignupInfo(headers: any = {}): Observable<any> {
    return this.http.get(`${this.baseUrl}/auth/provider/signup`, {headers: new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...headers
    })});
  }
  
  redirectToProvider(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/provider/redirect`, data, this.httpOptions);
  }

  authenticateWithProviderToken(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/provider/token`, data, this.httpOptions);
  }

  // Auth: Sessions
  logoutCurrentSession(): Observable<any> {
    return this.http.delete(`${this.baseUrl}/auth/sessions`, this.httpOptions);
  }
  getSessions(): Observable<any> {
    return this.http.get(`${this.baseUrl}/auth/sessions`, this.httpOptions);
  }

  // Auth: WebAuthn
  reauthenticateWebauthn(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/webauthn/reauthenticate`, data, this.httpOptions);
  }

  authenticateWebauthn(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/webauthn/authenticate`, data, this.httpOptions);
  }

  loginWebauthn(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/webauthn/login`, data, this.httpOptions);
  }

}