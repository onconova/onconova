import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { LayoutService } from '../../../layout/service/app.layout.service'
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styles: [`
        :host ::ng-deep .pi-eye,
        :host ::ng-deep .pi-eye-slash {
            transform:scale(1.6);
            margin-right: 1rem;
            color: var(--primary-color) !important;
        }
    `]
})
export class LoginComponent {

    valCheck: string[] = ['remember'];
    username!: string;
    password!: string;
    loading: boolean = false;

    constructor(
        private router: Router,
        public layoutService: LayoutService,
        private messageService: MessageService,
        private authService: AuthService) { }

    ngOnInit(): void {
    }
  

    login(): void {
        this.loading = true
        this.authService.login(this.username, this.password).subscribe(
            (response) => {
                this.loading = false
                this.router.navigate(['/dashboard']).then(() => 
                    this.messageService.add({ severity: 'success', summary: 'Logout', detail: 'Succesful login' })
                )
            },
            (error) => {
                this.loading = false
                if (error.status == 401) {
                    this.messageService.add({ severity: 'error', summary: 'Login failed', detail: 'Invalid credentials' });
                } else 
                if (error.status == 400 ){
                    this.messageService.add({ severity: 'error', summary: 'Login failed', detail: 'Please provide a username and a password' });
                } else {
                    this.messageService.add({ severity: 'error', summary: 'Network error', detail: error.message });
                }
            }
        )
    }
}


