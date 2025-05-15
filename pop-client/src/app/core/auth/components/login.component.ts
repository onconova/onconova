import { Component, computed, inject, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { LayoutService } from '../../layout/app.layout.service'
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';

import { CommonModule } from '@angular/common';
import { Button } from 'primeng/button';
import { FormsModule } from '@angular/forms';
import { InputText } from 'primeng/inputtext';
import { Toast } from 'primeng/toast';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { FluidModule } from 'primeng/fluid';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';

@Component({
    selector: 'pop-login',
    template: `
    <p-toast></p-toast>
    <div class="flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
        <div class="flex flex-column align-items-center justify-content-center">
            <div [inlineSVG]="layoutService.logo" class="pop-logo w-8rem h-8rem mr-3 mb-3" alt="POP logo"></div>            
            <div style="border-radius:56px; padding:0.3rem; background: linear-gradient(180deg, var(--p-primary-color) 10%, rgba(33, 150, 243, 0) 30%); min-width: 40rem;">
                <div class="w-full surface-card py-8 px-5 sm:px-8" style="border-radius:53px; background: var(--p-content-background) !important;">
                    <div class="text-center mb-5">
                        <div class="text-900 text-3xl font-medium mb-3">Welcome!</div>
                        <span class="text-600 font-medium text-muted">Sign in to continue</span>
                    </div>

                    <form (ngSubmit)="login()">
                        <div class="field">
                            <label for="username" class="font-semibold">What is your {{ loginMethods() }}? </label>
                            <p-iconfield>
                                <p-inputicon styleClass="pi pi-at" />
                                <input type="text" pInputText placeholder="{{ loginMethods() | titlecase }}" name="username" fluid [(ngModel)]="username" class="py-3 px-5" autocomplete="username"/>
                            </p-iconfield>
                        </div>

                        <div class="field">
                            <label for="password1" class="font-semibold">Password</label>
                            <p-iconfield>
                                <p-inputicon styleClass="pi pi-key" />
                                <input type="password" pInputText placeholder="Password" name="password" fluid [(ngModel)]="password" class="py-3 px-5" autocomplete="current-password"/>
                            </p-iconfield>
                        </div>

                        <p-button type="submit" label="Sign In" styleClass="w-full p-3 text-xl mt-3"  [loading]="loading"></p-button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    `,
    imports: [
        CommonModule,
        FormsModule,
        InlineSVGModule,
        FluidModule,
        InputIconModule,
        IconFieldModule,
        Button,
        InputText,
        Toast,
    ]
})
export class LoginComponent implements OnInit {

    // Inject services
    private route = inject(ActivatedRoute);
    private router = inject(Router);
    public layoutService =  inject(LayoutService);
    private messageService = inject(MessageService);
    private authService = inject(AuthService);

    // Properties
    public valCheck: string[] = ['remember'];
    public username!: string;
    public password!: string;
    public loading: boolean = false;
    private nextUrl!: string;

    public loginMethods = computed(() => {
        const config = this.authService.configuration.value() as any;
        console.log('config?.data?.account?.login_methods', config?.data?.account?.login_methods)
        return config?.data?.account?.login_methods.join(' or ');
    })

    ngOnInit(): void {
        // Get return URL from route parameters or default to '/'
        this.nextUrl = this.route.snapshot.queryParams['next'] || '/dashboard';
    }

    login(): void {
        this.loading = true
        this.authService.login(this.username, this.password).subscribe({
            next: (response) => {
                this.loading = false
                this.router.navigateByUrl(this.nextUrl).then(() => 
                    this.messageService.add({ severity: 'success', summary: 'Login', detail: 'Succesful login' })
                )
            },
            error: (error) => {
                this.loading = false
                if (error.status == 401) {
                    this.messageService.add({ severity: 'error', summary: 'Login failed', detail: 'Invalid credentials' });
                } else 
                if (error.status == 400 ){
                    this.messageService.add({ severity: 'error', summary: 'Login failed', detail: 'Please provide a username and a password' });
                } else {
                    this.messageService.add({ severity: 'error', summary: 'Network error', detail: error.error.detail });
                }
            }
        })
    }
}


