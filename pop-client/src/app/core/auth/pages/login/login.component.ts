import { Component, inject, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { LayoutService } from '../../../layout/app.layout.service'
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
    standalone: true,
    selector: 'pop-login',
    templateUrl: './login.component.html',
    styles: [`
        :host ::ng-deep .pi-eye,
        :host ::ng-deep .pi-eye-slash {
            transform:scale(1.6);
            margin-right: 1rem;
            color: var(--primary-color) !important;
        }
    `],
    imports:[
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


