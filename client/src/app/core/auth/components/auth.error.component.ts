import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { AuthLayoutComponent } from './auth-layout.component';

@Component({
    selector: 'onconova-error',
    template: `
    <onconova-auth-layout>
        <ng-template #inside>
            <div class="grid flex flex-column align-items-center">
                <h1 class="text-900 font-bold text-5xl mb-2">404 Error Occured</h1>
                <span class="text-600 mb-5">Requested resource is not available.</span>
                <img src="assets/images/error/asset-error.svg" alt="Error" class="mb-5" width="80%">
                <button pButton pRipple icon="pi pi-arrow-left" label="Go to Dashboard" class="p-button-text" [routerLink]="['/']"></button>
            </div>
        </ng-template>
    </onconova-auth-layout>
    `,
    imports: [
        AuthLayoutComponent,
        RouterModule,
        CommonModule,
        ButtonModule,
    ]
})
export class ErrorComponent {}