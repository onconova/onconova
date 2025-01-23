import { Component, inject, ViewEncapsulation } from '@angular/core';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { InlineSVGModule } from 'ng-inline-svg-2';

import { DialogModule } from 'primeng/dialog';
import { Button } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { RandomPaperComponent } from './components/random-paper/random-paper.component';

@Component({
    standalone: true,
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
        InlineSVGModule,
        CardModule,
        Button,
        DialogModule,
        RandomPaperComponent
    ],
})
export class DashboardComponent {
    public readonly authService = inject(AuthService);
    public readonly illustration: string = 'assets/images/landing/researcher.svg';
    public disclaimerDialogVisible: boolean = false;
}
