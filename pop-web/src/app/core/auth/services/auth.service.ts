import { Injectable } from '@angular/core';
import { AuthService as APIAuthService } from 'src/app/shared/openapi';
import { Observable } from 'rxjs'
import { tap, firstValueFrom } from 'rxjs';
import { GetTokenPairRequestParams, UserCredentials, TokenPair, TokenRefresh, RefreshedTokenPair} from 'src/app/shared/openapi/';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  public username: string | null = null;

  constructor(
    private apiAuth: APIAuthService,
  ) {}

  login(username: string, password: string): Observable<TokenPair> {
    const userCredentials: UserCredentials = {
        username: username,
        password: password
    }
    return this.apiAuth.getTokenPair({userCredentials: userCredentials})
      .pipe(tap((response: TokenPair) => {
        this.setAccessToken(response.access);
        this.setRefreshToken(response.refresh);
        this.setUsername(response.username);
    })) 
  }
  
  logout(): void {
    localStorage.removeItem('pop_access_token');
    localStorage.removeItem('pop_access_token');
  }

  setAccessToken(token: string) {
    localStorage.setItem('pop_access_token', token);
  }

  setRefreshToken(token: string) {
    localStorage.setItem('pop_refresh_token', token);
  }

  setUsername(username: string) {
    this.username = username;
    localStorage.setItem('pop_logged_username', username);
  }

  getUsername(): string {
    return this.username || localStorage.getItem('pop_logged_username') || '?';
  }

  getAccessToken(): string | null {
    return localStorage.getItem('pop_access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('pop_refresh_token');
  }

  async refreshTokenPair() {
    const refreshToken = this.getRefreshToken()
    if (refreshToken) {
      const slidingToken: TokenRefresh = {
        refresh: refreshToken,
      }
      const freshTokenPair: RefreshedTokenPair = await firstValueFrom(this.apiAuth.refreshTokenPair({tokenRefresh: slidingToken}))
      if (freshTokenPair.access) {
        this.setAccessToken(freshTokenPair.access);
        this.setRefreshToken(freshTokenPair.refresh);
      }
    } 
  }


  async checkAuthentication() {
    // Check whether the token is expired and return true or false
    const jwtHelper = new JwtHelperService();
    let accessTokenHasExpired =  jwtHelper.isTokenExpired(this.getAccessToken());
    if ( accessTokenHasExpired ) {
      const refreshTokenHasExpired =  jwtHelper.isTokenExpired(this.getRefreshToken());
      if ( !refreshTokenHasExpired ) {
        await this.refreshTokenPair()
        accessTokenHasExpired =  jwtHelper.isTokenExpired(this.getAccessToken());
      }
    }
    return !accessTokenHasExpired
  }

}