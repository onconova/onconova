import { computed, effect, inject, Injectable, linkedSignal, signal } from '@angular/core';
import { AuthService as APIAuthService } from 'src/app/shared/openapi';
import { map, Observable, of, switchMap } from 'rxjs'
import { firstValueFrom } from 'rxjs';
import { User, UserCredentials, TokenPair, RefreshedTokenPair} from 'src/app/shared/openapi/';
import { JwtHelperService } from '@auth0/angular-jwt';
import { rxResource } from '@angular/core/rxjs-interop';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AllAuthApiService } from '../allauth-api.service';
import { SocialAuthService } from '@abacritt/angularx-social-login';

export const LOGOUT_ENDPOINT = '/api/allauth/app/v1/auth/session';
export const LOGIN_ENDPOINT = '/api/allauth/app/v1/auth/login';
export const CONFIG_ENDPOINT = '/api/allauth/app/v1/config';


@Injectable({
  providedIn: 'root'
})
export class AuthService {


  #apiAuth = inject(APIAuthService);
  #allAuthApiService = inject(AllAuthApiService);
  #http = inject(HttpClient);
  #router = inject(Router);
  #socialAuthService = inject(SocialAuthService);

  // Signals initialized from localStorage
  public sessionUserId = signal<string | null>(this.getStoredSessionUserId());
  public sessionToken = signal<string | null>(this.getStoredSessionToken());

  public identityProvider: string | null = null

  // Computed: isAuthenticated (reactive, based on session token)
  public isAuthenticated = computed(() => !!this.sessionToken());

  // Reactive user resource (refetches on username change)
  public userResource = rxResource({
    request: () => ({userId: this.sessionUserId() as string}),
    loader: ({request}): Observable<any> => this.#apiAuth.getUserById(request)
  });  
  // Computed: Current user value from resource
  public user = linkedSignal(() => this.userResource.value() as User);

  constructor() {
    // Keep localStorage in sync with the signal
    effect(() => {
      const token = this.sessionToken();
      if (token) {
        this.setStoredSessionToken(token);
      } else {
        this.removeStoredSessionToken();
      }
    });
    effect(() => {
      const userId = this.sessionUserId();
      if (userId) {
        this.setStoredSessionUserId(userId);
      } else {
        this.removeStoredSessionUserId();
      }
    });
  }

  login(username: string, password: string) {
    return this.#allAuthApiService.login({ username, password })
      .pipe(
        map( (response: any) => {
          this.sessionToken.set(response.meta.session_token);
          this.sessionUserId.set(response.data.user.id);
        })
      );
  }

  loginThroughProvider(provider: string, client_id: string, id_token: string) {
    return this.#allAuthApiService.authenticateWithProviderToken({
          provider: provider,
          process: "login",
          token: {
            client_id: client_id,
            id_token: id_token
          }
    }).pipe(
      map( (response: any) => {
        this.sessionToken.set(response.meta.session_token);
        this.sessionUserId.set(response.data.user.id);
      })
    )
  }
  
  logout() {
    if (this.identityProvider) {
      console.log('LOGGOUT FROM', this.identityProvider);
      this.#socialAuthService.signOut();
    } else {
      this.#allAuthApiService.logoutCurrentSession().subscribe();
      console.log('LOGGOUT LOCAL');
    }
    this.identityProvider = null;
  }

  private setStoredSessionToken(token: string) {
    localStorage.setItem('sessionToken', token);
  }
  private removeStoredSessionToken() {
    localStorage.removeItem('sessionToken');
  }
  private getStoredSessionToken(): string | null {
    return localStorage.getItem('sessionToken');
  }
  private setStoredSessionUserId(userId: string) {
    localStorage.setItem('sessionUserId', userId);
  }
  private removeStoredSessionUserId() {
    localStorage.removeItem('sessionUserId');
  }
  private getStoredSessionUserId(): string {
    return localStorage.getItem('sessionUserId') || '?';
  }

}