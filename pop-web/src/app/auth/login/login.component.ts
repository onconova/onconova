import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { LayoutService } from '../../layout/service/app.layout.service'
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
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
    `],
    providers: [MessageService]
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
                this.messageService.add({ severity: 'error', summary: 'Login failed', detail: 'Please check your credentials' });
            }
        )
    }
}


