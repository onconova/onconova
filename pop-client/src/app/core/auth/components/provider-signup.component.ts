import { Component, effect, inject, input } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AllAuthApiService } from '../services/allauth-api.service';
import { rxResource } from '@angular/core/rxjs-interop';
import { AuthService } from '../services/auth.service';
import { UsersService } from 'src/app/shared/openapi';
import { CommonModule } from '@angular/common';
import { LayoutService } from '../../layout/app.layout.service';
import { InputIconModule } from 'primeng/inputicon';
import { IconFieldModule } from 'primeng/iconfield';
import { Button } from 'primeng/button';
import { InputText } from 'primeng/inputtext';
import { Fluid } from 'primeng/fluid';
import { AuthLayoutComponent } from './auth-layout.component';

@Component({
  selector: 'app-signup',
  imports: [
    ReactiveFormsModule, 
    CommonModule, 
    AuthLayoutComponent,    
    InputIconModule,
    IconFieldModule,
    Fluid,
    Button,
    InputText,
],
  template: `
    <pop-auth-layout>
        <ng-template #inside>
            <div class="text-center mb-3 pb-4">
                <div class="text-900 text-3xl font-medium mb-2">First-time sign-up</div>
                <span class="text-600 font-medium text-muted">Please complete the following information</span>
            </div>

            @if (providerSignupInfo.value()?.data.account.provider; as provider) {
                <div class="text-center mb-5">
                    <div class="text-muted mb-2">Identity provided by:</div>
                    <div class="font-xl">
                    <i class="pi pi-{{provider.id}}"></i> {{provider.name}} 
                    </div>
                </div>
            }


            <form [formGroup]="signupForm" (ngSubmit)="onSubmit()">
                <p-fluid>
                    <div class="field">
                        <label for="username" class="form-label required">Username</label>
                        <p-iconfield>
                            <p-inputicon styleClass="pi pi-user" />
                            <input type="text" pInputText placeholder="Username" name="username" fluid formControlName="username" class="py-3 px-5" autocomplete="username"/>
                        </p-iconfield>
                    </div>

                    <div class="field">
                        <label for="username" class="form-label required">E-mail</label>
                        <p-iconfield>
                            <p-inputicon styleClass="pi pi-envelope" />
                            <input type="text" pInputText placeholder="E-mail" name="email" fluid formControlName="email" class="py-3 px-5" autocomplete="email"/>
                        </p-iconfield>
                    </div>
                    <p-button type="submit" label="Sign-up"  styleClass="w-full p-3 text-xl mt-3" />
                </p-fluid>
            </form>
        </ng-template>
    </pop-auth-layout>
  `,
})
export class ProviderSignupComponent {

    readonly session = input.required<string>()
    readonly provider = input.required<string>()

    readonly #fb = inject(FormBuilder);
    readonly #authService = inject(AuthService);
    readonly #usersService = inject(UsersService);
    readonly #allAuthApiService = inject(AllAuthApiService);
    public layoutService =  inject(LayoutService);

    protected signupForm: FormGroup = this.#fb.group({
      username: this.#fb.control<string>('', Validators.required),
      email: this.#fb.control<string>('', [Validators.required, Validators.email]),
    })

    public providerSignupInfo = rxResource({
      request: () => this.session(),
      loader: ({request}) => this.#allAuthApiService.getproviderSignupInfo(request)
    }) 

    constructor() {
        effect(() => {
          if (this.providerSignupInfo.hasValue()) {
            const data = this.providerSignupInfo.value().data
            this.signupForm.patchValue({
                username: data.user?.username,
                email: data.user?.email
            })
            this.signupForm.controls['email'].disable()
            this.signupForm.updateValueAndValidity()
          }
        })
    }

  onSubmit(): void {
    const signupData = this.signupForm.value;
    this.#authService.signupProviderAccount(signupData, this.session())   
    }
}