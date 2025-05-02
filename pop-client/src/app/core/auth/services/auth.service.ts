import { computed, inject, Injectable, linkedSignal, signal } from '@angular/core';
import { AuthService as APIAuthService } from 'src/app/shared/openapi';
import { map, Observable } from 'rxjs'
import { firstValueFrom } from 'rxjs';
import { User, UserCredentials, TokenPair, RefreshedTokenPair} from 'src/app/shared/openapi/';
import { JwtHelperService } from '@auth0/angular-jwt';
import { rxResource } from '@angular/core/rxjs-interop';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiAuth = inject(APIAuthService);
  private jwtHelper = new JwtHelperService();
  // Signals initialized from localStorage
  public username = signal(this.getStoredUsername());
  public accessToken = signal(this.getStoredAccessToken());
  public refreshToken = signal(this.getStoredRefreshToken());

  // Computed: validity status for access/refresh tokens
  public isAccessTokenValid = computed(() => !this.jwtHelper.isTokenExpired(this.accessToken()));
  public isRefreshTokenValid = computed(() => !this.jwtHelper.isTokenExpired(this.refreshToken()));
  
  // Computed: isAuthenticated (reactive, based on access token validity)
  public isAuthenticated = computed(() => this.isAccessTokenValid() && this.isRefreshTokenValid());

  // Reactive user resource (refetches on username change)
  public userResource = rxResource({
    request: () => ({username: this.username()}),
    loader: ({request}) => this.apiAuth.getUsers(request).pipe(
      map(data => data.items[0])
    )
  });  
  // Computed: Current user value from resource
  public user = linkedSignal(() => this.userResource.value() as User);

  login(username: string, password: string): Observable<void> {
    const userCredentials: UserCredentials = { username, password };
    return this.apiAuth.getTokenPair({ userCredentials }).pipe(
      map((response: TokenPair) => {
        this.storeAccessToken(response.access);
        this.storeRefreshToken(response.refresh);
        this.storeUsername(response.username);
        this.accessToken.set(response.access);
        this.refreshToken.set(response.refresh);
        this.username.set(response.username);
      })
    );
  }

  logout() {
    localStorage.removeItem('pop_logged_username');
    localStorage.removeItem('pop_access_token');
    localStorage.removeItem('pop_refresh_token');
    this.username.set('');
  }

  private storeAccessToken(token: string) {
    localStorage.setItem('pop_access_token', token);
  }

  private storeRefreshToken(token: string) {
    localStorage.setItem('pop_refresh_token', token);
  }

  private storeUsername(username: string) {
    localStorage.setItem('pop_logged_username', username);
  }

  private getStoredUsername(): string {
    return localStorage.getItem('pop_logged_username') || '?';
  }

  private getStoredAccessToken(): string | null {
    return localStorage.getItem('pop_access_token');
  }

  private getStoredRefreshToken(): string | null {
    return localStorage.getItem('pop_refresh_token');
  }

  // Manual token check and refresh (to be called by guards/resolvers)
  async ensureAuthenticated(): Promise<boolean> {
    if (!this.isAccessTokenValid() && this.isRefreshTokenValid()) {
      const refreshToken = this.refreshToken();
      if (refreshToken) {
        await firstValueFrom(
          this.apiAuth.refreshTokenPair({ tokenRefresh: { refresh: refreshToken } }).pipe(
            map((tokenPair: RefreshedTokenPair) => {
              this.accessToken.set(tokenPair.access);
              this.refreshToken.set(tokenPair.refresh);
              if (tokenPair.access) {
                this.storeAccessToken(tokenPair.access);
              } else {
                localStorage.removeItem('pop_access_token');
              }
              this.storeRefreshToken(tokenPair.refresh);
            })
          )
        );
      }
    }
    return this.isAuthenticated();
  }
}