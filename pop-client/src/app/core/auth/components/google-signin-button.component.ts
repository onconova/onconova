import { Component, EventEmitter, Output } from '@angular/core';
import { Button } from 'primeng/button';

declare global {
  interface Window {
    google: any;
  }
}

@Component({
selector: 'app-google-signin',
imports: [Button],
template: `
    <p-button icon="pi pi-google" (onClick)="handleGoogleLogin()" styleClass="w-30rem py-3" severity="secondary" [raised]="true" size="large" [rounded]="true" label="Sign In with Google"/>
`,
})
export class GoogleSigninComponent {

  @Output() loginWithGoogle: EventEmitter<any> = new EventEmitter<any>();

  createFakeGoogleWrapper = () => {
      const googleLoginWrapper = document.createElement('div');
      googleLoginWrapper.style.display = 'none';
      googleLoginWrapper.classList.add('custom-google-button');
      document.body.appendChild(googleLoginWrapper);
      window.google.accounts.id.renderButton(googleLoginWrapper, {
        type: 'icon',
        width: '200',
      });

      const googleLoginWrapperButton = googleLoginWrapper.querySelector(
        'div[role=button]'
      ) as HTMLElement;

      return {
        click: () => {
            googleLoginWrapperButton?.click();
        },
      };
  };

  handleGoogleLogin() {
      this.loginWithGoogle.emit(this.createFakeGoogleWrapper());
  }
}