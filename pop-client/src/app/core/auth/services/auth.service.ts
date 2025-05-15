import { computed, effect, inject, Injectable, linkedSignal, signal } from '@angular/core';
import { AuthService as APIAuthService } from 'src/app/shared/openapi';
import { map, Observable, of } from 'rxjs'
import { firstValueFrom } from 'rxjs';
import { User, UserCredentials, TokenPair, RefreshedTokenPair} from 'src/app/shared/openapi/';
import { JwtHelperService } from '@auth0/angular-jwt';
import { rxResource } from '@angular/core/rxjs-interop';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

export const LOGOUT_ENDPOINT = '/api/allauth/app/v1/auth/session';
export const LOGIN_ENDPOINT = '/api/allauth/app/v1/auth/login';
export const CONFIG_ENDPOINT = '/api/allauth/app/v1/config';


@Injectable({
  providedIn: 'root'
})
export class AuthService {


  #apiAuth = inject(APIAuthService);
  #http = inject(HttpClient);
  #router = inject(Router);

  // Signals initialized from localStorage
  public sessionUserId = signal<string | null>(this.getStoredSessionUserId());
  public sessionToken = signal<string | null>(this.getStoredSessionToken());

  // Computed: isAuthenticated (reactive, based on session token)
  public isAuthenticated = computed(() => !!this.sessionToken());

  // Reactive authentication backend configuration
  public configuration = rxResource({
    request: () => ({}),
    loader: ({request}) => this.#http.get(CONFIG_ENDPOINT)
  });  

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
    return this.#http.post(LOGIN_ENDPOINT, { username, password })
      .pipe(
        map( (response: any) => {
          this.sessionToken.set(response.meta.session_token);
          this.sessionUserId.set(response.data.user.id);
          this.#router.navigate(['/']);
        })
      );
  }
  
  logout() {
    this.#http.delete(LOGOUT_ENDPOINT, {headers: {'X-SESSION-TOKEN': this.sessionToken() as string}}).subscribe();
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