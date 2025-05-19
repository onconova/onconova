import { Component, inject, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { AuthLayoutComponent } from './auth-layout.component';

@Component({
  selector: 'app-auth-callback',
  imports: [AuthLayoutComponent],
  template: `
    <pop-auth-layout>
      <ng-template #inside>
          <h2 class="text-center">Signing you in...</h2>
      </ng-template>
    </pop-auth-layout>
    `
})
export class AuthCallbackComponent implements OnInit {

    #authService = inject(AuthService);
    
    ngOnInit() {
        this.#authService.handleOpenIdAuthCallback();
    }
}