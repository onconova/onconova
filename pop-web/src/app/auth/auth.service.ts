import { Injectable } from '@angular/core';
import { AuthService as APIAuthService } from '../core/modules/openapi';
import { Observable } from 'rxjs'
import { tap, firstValueFrom } from 'rxjs';
import { UserCredentialsSchema, TokenPairSchema, TokenRefreshSchema, RefreshedTokenPairSchema} from '../core/modules/openapi/';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(
    private apiAuth: APIAuthService,
  ) {}

  login(username: string, password: string): Observable<TokenPairSchema> {
    const userCredentials: UserCredentialsSchema = {
        username: username,
        password: password
    }
    return this.apiAuth.getSlidingToken(userCredentials)
      .pipe(tap((response: TokenPairSchema) => {
        this.setAccessToken(response.access);
        this.setRefreshToken(response.refresh);
    })) 
  }
  
  logout(): void {
    localStorage.removeItem('pop_access_token');
  }

  setAccessToken(token: string) {
    localStorage.setItem('pop_access_token', token);
  }
  setRefreshToken(token: string) {
    localStorage.setItem('pop_refresh_token', token);
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
      const slidingToken: TokenRefreshSchema = {
        refresh: refreshToken,
      }
      const freshTokenPair: RefreshedTokenPairSchema = await firstValueFrom(this.apiAuth.refereshSlidingToken(slidingToken))
      if (freshTokenPair.access) {
        this.setAccessToken(freshTokenPair.access);
        this.setRefreshToken(freshTokenPair.refresh);
        console.log('REFRESHED')
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