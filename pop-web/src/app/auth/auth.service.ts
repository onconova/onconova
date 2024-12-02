import { Injectable } from '@angular/core';
import { AuthService as APIAuthService } from '../core/modules/openapi';
import { Observable } from 'rxjs'
import { tap } from 'rxjs/operators';
import { UserCredentialsSchema, SlidingTokenSchema } from '../core/modules/openapi/';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private token: string = '';

  constructor(
    private apiAuth: APIAuthService,
  ) {}

  login(username: string, password: string): Observable<SlidingTokenSchema> {
    const userCredentials: UserCredentialsSchema = {
        username: username,
        password: password
    }
    return this.apiAuth.getSlidingToken(userCredentials)
      .pipe(tap((response: SlidingTokenSchema) => {
        localStorage.setItem('pop_access_token', response.token);
      })) 
  }
  
  logout(): void {
    localStorage.removeItem('pop_access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('pop_access_token');
  }

  setToken(token: string): void {
    this.token = token;
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem('pop_access_token');
    // Check whether the token is expired and return true or false
    const jwtHelper = new JwtHelperService();
    return !jwtHelper.isTokenExpired(token);
  }

}