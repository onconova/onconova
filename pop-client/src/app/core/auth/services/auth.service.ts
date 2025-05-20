import { computed, effect, inject, Injectable, linkedSignal, signal } from '@angular/core';
import { Location } from '@angular/common';
import { UsersService } from 'src/app/shared/openapi';
import { iif, map, Observable, of, switchMap, throwError } from 'rxjs'
import { User} from 'src/app/shared/openapi/';
import { rxResource } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { AllAuthApiService, AllAuthResponse } from './allauth-api.service';
import { AppConfigService } from 'src/app/app.config.service';
import { MessageService } from 'primeng/api';

export const OPENID_CALLBACK_URL = '/auth/callback'
export interface OpenIDCredentials {
  accessToken: string | null,
  idToken: string | null,
  authorizationCode: string | null,
  state: string | null
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  // Injected services
  #router = inject(Router);
  #userService = inject(UsersService);
  #allAuthApiService = inject(AllAuthApiService);
  #messageService = inject(MessageService);
  #configService = inject(AppConfigService);

  // Signals initialized from localStorage
  public sessionUserId = signal<string | null>(this.getStoredSessionUserId());
  public sessionToken = signal<string | null>(this.getStoredSessionToken());

  // Computed: isAuthenticated (reactive, based on session token)
  public isAuthenticated = computed(() => !!this.sessionToken());

  // Reactive user resource (refetches on username change)
  public userResource = rxResource({
    request: () => ({userId: this.sessionUserId() as string}),
    loader: ({request}): Observable<User> => this.isAuthenticated() ? this.#userService.getUserById(request) : of({username: 'anonymous', id: '', email: '', accessLevel: 0} as User),
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

  public login(credentials: {username: string, password: string}, nextUrl?: string): void {
    this.#allAuthApiService.login(credentials)
      .pipe(
        // Set the session token and user ID signals after a successful login
        map( (response: AllAuthResponse) => {
          this.sessionToken.set(response.meta?.session_token || null);
          this.sessionUserId.set(response.data.user.id);
        })
      ).subscribe({
        next: () => {
            this.#router.navigateByUrl(nextUrl || '/').then(() => 
                this.#messageService.add({ severity: 'success', summary: 'Login', detail: 'Succesful login' })
            )
        },
        error: (error) => {
            if (error.status == 401) {
                this.#messageService.add({ severity: 'error', summary: 'Login failed', detail: 'Invalid credentials' });
            } else 
            if (error.status == 400 ){
                this.#messageService.add({ severity: 'error', summary: 'Login failed', detail: 'Please provide a username and a password' });
            } else {
                this.#messageService.add({ severity: 'error', summary: 'Network error', detail: error.error.detail });
            }
        }
    });
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
    this.#allAuthApiService.logoutCurrentSession().subscribe({
      next: () => {
        this.sessionToken.set(null);
        this.sessionUserId.set(null);
      }
    });
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
    if (!providerId) {
      throw new Error('Invalid provider ID');
    }
    const config = this.#configService;
    const callbackUrl = config.BASE_PATH + OPENID_CALLBACK_URL;
    console.log('callbackUrl',callbackUrl)
    const scope = 'openid email profile';
    const responseType = 'token id_token';
    const state = this.generateRandomState(16);
    const nonce = this.generateRandomState(16);

    // Get the client ID for the provider from the server
    const clientId = config.getIdentityProviderClientId(providerId);    
    if (!clientId) {
      this.#messageService.add({ severity: 'error', summary: 'Login failed', detail: `No client ID found for provider '${providerId}'` });
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
        this.redirect(url);
      })
    ).subscribe({
      error: (error) => {
        this.#messageService.add({ severity: 'error', summary: 'Could not retrieve authorization endpoint from OpenID provider', detail: error });
        console.error(error);
      }
    });
  }

  redirect(url: URL): void {
    // Return the authorization URL
    window.location.href = url.toString();
  }

  /**
   * Handle the OpenID Connect callback from a provider and authenticate the user using the authorization
   * code, access token, or ID token provided by the provider.
   *
   * The OpenID Connect callback is handled by this method by extracting the authorization code, access
   * token, and ID token from the redirect URL, and using them to authenticate the user and start a
   * session.
   *
   * If the authentication is successful, the user is redirected to the dashboard.
   *
   */
  handleOpenIdAuthCallback(): void {
    const provider = localStorage.getItem('login_provider')!;
    const client_id = localStorage.getItem('login_client_id')!;

    // Get the OpdnID callback parameters encoded in the redirect URL
    const credentials = this.getCurrentURLOpenIdCredentials();

    of(credentials).pipe(
      // If OpenID Connect access token or ID token is present, just return the credentials
      switchMap((creds: OpenIDCredentials): Observable<OpenIDCredentials> => iif(() => Boolean(creds.idToken || creds.accessToken), of(creds),
        // Otherwise, if authorization code is present exchange it
        iif(() => Boolean(creds.authorizationCode),
          // To be implemented...
          throwError(() => 'The OpenID authorization code flow is not supported.'),
          // If no credentials are found, throw an error
          throwError(() => 'No OpenID Connect access token, ID token, or authorization code found in callback')
        )
      )),
      // Use the ID token or access token to authenticate the user and start a session
      switchMap((creds: OpenIDCredentials): Observable<AllAuthResponse> => this.#allAuthApiService.authenticateWithProviderToken({
        provider: provider, process: "login",
        token: {client_id: client_id, id_token: creds.idToken, access_token: creds.accessToken,}
      }))
    ).subscribe({
          next: (response: AllAuthResponse) => {
            this.sessionToken.set(response.meta!.session_token || '');
            this.sessionUserId.set(response.data.user.id);
            // Redirect the user to the dashboard
            this.#router.navigate(['/dashboard']);
          },
          error: (error) => {
            if (error?.status == 401 && error.error?.meta.session_token) {
              // If the authentication failed because the user needs to create a POP username,
              // redirect the user to a signup form to create a POP username
              this.#router.navigate(['/auth/signup',provider, error.error.meta.session_token])
            } else {
              console.error('OpenID Connect callback authentication failed:', error);
              this.#router.navigate(['/auth/login']);
            }
          },
        });
  }


  public signupProviderAccount(data: {username: string, email: string}, sessionToken: string): void {
    this.#allAuthApiService.providerSignup(data, sessionToken)
      .subscribe({
        next: (response: AllAuthResponse) => {
            // Store the session token locally
            this.sessionToken.set(response.meta!.session_token || '');
            this.sessionUserId.set(response.data.user.id);
            // Redirect the user to the dashboard
            this.#router.navigate(['/dashboard']);
        },
        error: (error) => {
          const message = error?.error?.errors?.map((e: any) => e?.message || 'a').join(', ');
          this.#messageService.add({ severity: 'error', summary: 'Identity Provider Signup', detail: message });
          console.error(error);
        }
      });
  }

  /**
   * Returns an object with the OpenID Connect credentials from the current URL.
   */
  public getCurrentURLOpenIdCredentials(): OpenIDCredentials {
    // Parse the URL search parameters (e.g. ?access_token=...)
    const searchParams = new URLSearchParams(window.location.search);
    // Parse the URL hash parameters (e.g. #access_token=...)
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    // Helper function to get a parameter value from either the URL search or hash parameters.
    const getURLParam = (name: string) => searchParams.get(name) || hashParams.get(name);
    // Return the OpenID Connect credentials
    return {
      accessToken: getURLParam('access_token'),
      idToken: getURLParam('id_token'),
      authorizationCode: getURLParam('code'),
      state: getURLParam('state'),
    }
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
  private getStoredSessionUserId(): string | null {
    return localStorage.getItem('sessionUserId');
  }


  private generateRandomState(length: number) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    return Array.from({ length }, () => chars.charAt(Math.floor(Math.random() * chars.length))).join('');
  }
}