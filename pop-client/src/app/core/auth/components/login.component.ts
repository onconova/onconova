import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';

import { CommonModule } from '@angular/common';
import { Button } from 'primeng/button';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { InputText } from 'primeng/inputtext';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { Fluid, FluidModule } from 'primeng/fluid';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { Divider } from 'primeng/divider';
import { AppConfigService } from 'src/app/app.config.service';
import { AuthLayoutComponent } from './auth-layout.component';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
    selector: 'pop-login',
    imports: [
        ReactiveFormsModule,
        AuthLayoutComponent,
        CommonModule,
        FormsModule,
        InlineSVGModule,
        FluidModule,
        InputIconModule,
        IconFieldModule,
        Divider,
        Fluid,
        Button,
        InputText,
    ],
    template: `
    <pop-auth-layout>

        <ng-template #inside>
            <div class="text-center mb-5 pb-4">
                <div class="text-900 text-xl font-medium mb-1">Welcome to the</div>
                <div class="text-900 text-3xl font-medium mb-2">Precision Oncology Platform</div>
                <span class="text-600 font-medium text-muted">Please sign in to continue</span>
            </div>

            <form [formGroup]="credentials" (ngSubmit)="login()">
                <p-fluid>
                    <div class="field">
                        <label for="username" class="font-medium">Do you have a POP account? </label>
                        <p-iconfield>
                            <p-inputicon styleClass="pi pi-at" />
                            <input type="text" pInputText placeholder="Account {{ loginMethods() }}" formControlName="username" class="py-3 px-5" autocomplete="username"/>
                        </p-iconfield>
                    </div>

                    <div class="field">
                        <label for="password1" class="font-medium">Password</label>
                        <p-iconfield>
                            <p-inputicon styleClass="pi pi-key" />
                            <input type="password" pInputText placeholder="Password" formControlName="password" class="py-3 px-5" autocomplete="current-password"/>
                        </p-iconfield>
                    </div>
                    <p-button type="submit" label="Sign In" styleClass="w-full p-3 text-xl mt-3" [disabled]="credentials.invalid" [loading]="loading()"></p-button>
                </p-fluid>
            </form>
        </ng-template>

        <ng-template #outside>
                @if (identityProviders().length > 0) {
                    <p-divider class="my-5"><div class="px-3 text-muted" style="background: light-dark(var(--p-surface-50), var(--p-surface-950))">or</div></p-divider>
                    <div class="flex flex-column gap-3">
                        <div class="flex flex-column gap-3 mx-auto">
                            @for (provider of identityProviders(); track provider.id ){
                                @switch (provider.id) {
                                    @case ('google') {
                                        <p-button (onClick)="loginProvider('google')" icon="pi pi-google" styleClass="w-30rem py-3" severity="secondary" [raised]="true" size="large" [rounded]="true" label="Sign In with Google"/>
                                    }
                                    @case ('microsoft') {
                                        <p-button (onClick)="loginProvider('microsoft')" icon="pi pi-microsoft" styleClass="w-30rem py-3" severity="secondary" [raised]="true" size="large" [rounded]="true" label="Sign In with Microsoft"/>
                                    }
                                    @case ('github') {
                                        <p-button (onClick)="loginProvider('github')" icon="pi pi-github" styleClass="w-30rem py-3" severity="secondary" [raised]="true" size="large" [rounded]="true" label="Sign In with GitHub"/>
                                    }
                                }
                            }
                        </div>
                    </div>
                }
        </ng-template>
    </pop-auth-layout>
    `,
})
export class LoginComponent {

    // Inject services
    #route = inject(ActivatedRoute);
    #fb = inject(FormBuilder);
    #authService = inject(AuthService);
    #configService = inject(AppConfigService);

    // Computed signal to get the next url from the query params
    #queryParams = toSignal(this.#route.queryParamMap, { initialValue: this.#route.snapshot.queryParamMap });
    #nextUrl = computed(() => this.#queryParams().get('next') || '/');

    protected loading = signal<boolean>(false);

    // Login form
    protected credentials: FormGroup = this.#fb.group({
        username: this.#fb.nonNullable.control<string>('', Validators.required),
        password: this.#fb.nonNullable.control<string>('', Validators.required),
    })

    // Computed reactive properties
    protected loginMethods = computed(() => {
        return this.#configService.getAllowedLoginMethds().join(' or ');
    })
    protected identityProviders = computed(() => {
        return this.#configService.getIdentityProviders();
    })

    login(): void {
        this.#authService.login(this.credentials.value, this.#nextUrl(), this.loading);
    }
    

  loginProvider(provider: string) {
    // Set login variables required for callback function once redirected back
    localStorage.setItem('login_provider', provider);  
    localStorage.setItem('login_client_id', this.#configService.getIdentityProviderClientId(provider)!); 
    // Initiate OpenID Connect authentication
    this.#authService.initiateOpenIdAuthentication(provider);
  }

}


