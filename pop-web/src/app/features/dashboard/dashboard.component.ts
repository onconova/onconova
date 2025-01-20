import { Component, inject } from '@angular/core';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { InlineSVGModule } from 'ng-inline-svg-2';

@Component({
    standalone: true,
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.css',
    imports: [
        InlineSVGModule
    ],
})
export class DashboardComponent {
    public readonly authService = inject(AuthService);
    public readonly illustration: string = 'assets/images/landing/researcher.svg';
}
