import { Injectable } from '@angular/core';
import { Router, CanActivate } from '@angular/router';
import { AuthService } from './auth.service';
import {Observable} from 'rxjs';

@Injectable()
export class AuthGuard implements CanActivate {

  constructor(
    private router: Router, 
    private auth: AuthService) {}

    canActivate(): Observable<boolean> | Promise<boolean> | boolean {
        return new Promise( (resolve, reject) => {
            this.auth.checkAuthentication().then(
                (isAuthenticated) => {
                    if (isAuthenticated) {
                        resolve(true)
                    } else {
                        this.router.navigate(['login']);
                        resolve(false)
                    }   
                })         
        })
    }

}