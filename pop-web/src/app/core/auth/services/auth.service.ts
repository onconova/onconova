import { inject, Injectable } from '@angular/core';
import { AuthService as APIAuthService, PaginatedUser } from 'src/app/shared/openapi';
import { first, map, Observable, switchMap } from 'rxjs'
import { tap, firstValueFrom } from 'rxjs';
import { User, UserCredentials, TokenPair, TokenRefresh, RefreshedTokenPair} from 'src/app/shared/openapi/';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiAuth = inject(APIAuthService);
  public username: string | null = this.getUsername();
  public user!: User;

  login(username: string, password: string): Observable<void> {
    const userCredentials: UserCredentials = {
        username: username,
        password: password
    }
    return this.apiAuth.getTokenPair({userCredentials: userCredentials}).pipe(
      map((response: TokenPair) => {
        this.setAccessToken(response.access);
        this.setRefreshToken(response.refresh);
        this.setUsername(response.username);
    })) 
  }
  
  logout(): void {
    localStorage.removeItem('pop_logged_username');
    localStorage.removeItem('pop_access_token');
    localStorage.removeItem('pop_refresh_token');
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

  getUser(username: string) {
    return this.apiAuth.getUsers({username: username, limit: 1}).pipe(
      map((response: PaginatedUser) => {
        return response.items[0];
      })
    )
  }

  checkUserExists() {
    if (!this.user || this.user.username !== this.getUsername()) {
      this.getUser(this.getUsername()).pipe(
        map(user => {this.user=user})
        ,first()
      ).subscribe()
    }
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