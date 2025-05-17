import { computed, effect, inject, Injectable, linkedSignal, signal } from '@angular/core';
import { AuthService as APIAuthService } from 'src/app/shared/openapi';
import { map, Observable, of, switchMap, tap } from 'rxjs'
import { User} from 'src/app/shared/openapi/';
import { rxResource } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { AllAuthApiService, AllAuthResponse } from '../allauth-api.service';
import { AppConfigService } from 'src/app/app.config.service';
import { OAuthExchangeCode } from 'src/app/shared/openapi/model/o-auth-exchange-code';
import { MessageService } from 'primeng/api';

export const OPENID_CALLBACK_URL = '/auth/callback'

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  // Injected services
  #apiAuth = inject(APIAuthService);
  #allAuthApiService = inject(AllAuthApiService);
  #router = inject(Router);
  #messageService = inject(MessageService);
  #configService = inject(AppConfigService);

  // Signals initialized from localStorage
  public sessionUserId = signal<string | null>(this.getStoredSessionUserId());
  public sessionToken = signal<string | null>(this.getStoredSessionToken());

  public identityProvider: string | null = null

  // Computed: isAuthenticated (reactive, based on session token)
  public isAuthenticated = computed(() => !!this.sessionToken());

  // Reactive user resource (refetches on username change)
  public userResource = rxResource({
    request: () => ({userId: this.sessionUserId() as string}),
    loader: ({request}): Observable<User> => this.isAuthenticated() ? this.#apiAuth.getUserById(request) : of({username: 'anonymous', id: '', email: '', accessLevel: 0} as User),
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

  /**
   * Perform a login with a username and password.
   *
   * @param username The username to use for login.
   * @param password The password to use for login.
   * @returns An observable that resolves to the response from the server, after setting the
   * session token and user ID signals.
   */
  public login(username: string, password: string): Observable<any> {
    return this.#allAuthApiService.login({ username, password })
      .pipe(
        // Set the session token and user ID signals after a successful login
        map( (response: AllAuthResponse) => {
          this.sessionToken.set(response.meta?.session_token || null);
          this.sessionUserId.set(response.data.user.id);
        })
      );
  }
  
  /**
   * Logout the current user session.
   *
   * This method sends a request to the server to delete the current user session. 
   * If successful, the server will respond with a 401 which will be handled by the 
   * interceptor and redirect the user to the login page.
   *
   */
  public logout(): void {
    if (!this.sessionToken()) {
      this.#messageService.add({ severity: 'error', summary: 'Logout failed', detail: `There is no active user session.` });
      throw new Error('There is no active session to log out');
    }
    // Send a request to the server to delete the current user session
    this.#allAuthApiService.logoutCurrentSession().subscribe();
    this.identityProvider = null;
  }

  /**
   * Start the login process using the specified OpenID provider. This method redirects the user to the
   * authorization endpoint of the provider, passing the client ID, redirect URI, response type, and
   * scope. The user is also passed a random state and nonce, which are used to verify the response.
   *
   * @param providerId The ID of the OpenID provider to use for authentication.
   * @returns The authorization URL, or null if the client ID or authorization endpoint was not found.
   */
  public initiateOpenIdAuthentication(providerId: string): void {
    if (!providerId || typeof providerId !== 'string') {
      throw new Error('Invalid provider ID');
    }
    const config = this.#configService;
    const callbackUrl = config.BASE_PATH + OPENID_CALLBACK_URL;
    const scope = 'openid email profile';
    const responseType = 'token id_token';
    const state = this.generateRandomString(16);
    const nonce = this.generateRandomString(16);

    // Get the client ID for the provider from the server
    const clientId = config.getIdentityProviderClientId(providerId);    
    if (!clientId) {
      this.#messageService.add({ severity: 'error', summary: 'Login failed', detail: `No client ID found for provider '${providerId}'` });
      console.error('No client ID found for provider', providerId);
      throw new Error(`No client ID found for provider ${providerId}`);
    }

    // Get the authorization endpoint from the OpenID configuration
    config.getOpenIdAuthorizationEndpoint(providerId).pipe(
      map((authorizationEndpoint) => {
        if (!authorizationEndpoint) {
          this.#messageService.add({ severity: 'error', summary: 'Login failed', detail: `No authorization endpoint was specified by the '${providerId}' openID configuration` });
          throw new Error(`No authorization endpoint was specified by the ${providerId} openID configuration`);
        }
        // Construct the authorization URL
        const url = new URL(authorizationEndpoint);
        url.searchParams.set('client_id', clientId);
        url.searchParams.set('redirect_uri', callbackUrl);
        url.searchParams.set('response_type', responseType);
        url.searchParams.set('scope', scope);
        url.searchParams.set('state', state);
        url.searchParams.set('nonce', nonce);

        // Return the authorization URL
        window.location.href = url.toString();
      })
    ).subscribe();
  }



  handleAuthCallback() {
    const provider = localStorage.getItem('login_provider')!;
    const client_id = localStorage.getItem('login_client_id')!;

    const params = new URLSearchParams(window.location.search);
    const params2 = new URLSearchParams(window.location.hash.substring(1));
    const accessToken = params.get('access_token') || params2.get('access_token');
    const idToken = params.get('id_token') || params2.get('id_token');
    const code = params.get('code') || params2.get('code');
    const state = params.get('state') || params2.get('state');

    if (code && state) {
      const payload: OAuthExchangeCode = {        
        provider: provider,
        code: code,
        state: state,
      }
      this.#apiAuth.exchangeOauthCodeForAccessToken({oAuthExchangeCode: payload}).pipe(
        switchMap((response: any) => {
        console.log('ACCESS TOKEN RETURNED BY POP SERVER', response)
        return this.authenticateWithProviderToken(provider, client_id, undefined, response?.access_token);
      })).subscribe({
        next: (response) => {
          localStorage.setItem('app_access_token', response?.meta?.access_token);
          this.#router.navigate(['/dashboard']);
        },
        error: (err) => {
          console.log(err)
          console.error('Backend authentication failed', err);
        },
      })
    } else if (accessToken && idToken) {
      this.authenticateWithProviderToken(provider, client_id, idToken, accessToken).subscribe({
        next: (response) => {
          localStorage.setItem('app_access_token', response?.meta?.access_token);
          this.#router.navigate(['/dashboard']);
        },
        error: (error) => {
          console.log('SIGNUP ERROR', error.error)
          if (error?.status == 401 && error.error?.meta.session_token) {
            localStorage.setItem('app_access_token', error.error?.meta.session_token);
             this.#allAuthApiService.getproviderSignupInfo({'X-SESSION-TOKEN': error.error?.meta.session_token}).subscribe({
              next: response => this.#allAuthApiService.providerSignup(
                // TODO: Create a proper signup form component for users to connect a provider account with a POP username
                {username: response.data.user.email.split('@')[0], email: response.data.user.email},
                {'X-SESSION-TOKEN': error.error?.meta.session_token}
              ).subscribe({
                next: (response) => {
                  localStorage.setItem('app_access_token', response?.meta?.access_token);
                  this.#router.navigate(['/dashboard']);
                },
                error: (error) => {
                  const message = error?.error?.errors?.map((e: any) => e?.message || 'a').join(', ');
                  this.#messageService.add({ severity: 'error', summary: 'Identity Provider Signup', detail: message});
                  console.error(error);
                }
              })
              
             })
          } else {
            console.error('Backend authentication failed', error);
          }
        },
      });
    } else {
      console.error('Tokens missing in callback URL', params);
    }
  }


  private authenticateWithProviderToken(provider: string, client_id: string, id_token?: string, access_token?: string): Observable<any> {
    return this.#allAuthApiService.authenticateWithProviderToken({
          provider: provider,
          process: "login",
          token: {
            client_id: client_id,
            id_token: id_token,
            access_token: access_token,
          }
    }).pipe(
      map( (response: any) => {
        this.sessionToken.set(response.meta.session_token);
        this.sessionUserId.set(response.data.user.id);
      })
    )
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


  private generateRandomString(length: number) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    return Array.from({ length }, () => chars.charAt(Math.floor(Math.random() * chars.length))).join('');
  }
}