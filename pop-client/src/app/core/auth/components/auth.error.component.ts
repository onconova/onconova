import { Component, inject } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { InlineSVGModule } from 'ng-inline-svg-2';

import { LayoutService } from 'src/app/core/layout/app.layout.service';

@Component({
    selector: 'pop-error',
    template: `
    <div class="flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
        <div class="flex flex-column align-items-center justify-content-center">
            <div [inlineSVG]="layoutService.logo" alt="logo" style="width: 8rem !important; height: 8rem !important;" class="pop-logo mr-3 mb-3" alt="POP logo"></div>            
            <div style="border-radius:56px; padding:0.3rem; background: linear-gradient(180deg, var(--p-primary-color) 10%, rgba(33, 150, 243, 0) 30%); min-width: 40rem;">
                <div class="w-full surface-card py-8 px-5 sm:px-8" style="border-radius:53px; background: var(--p-content-background) !important;">
                    <div class="grid flex flex-column align-items-center">
                        <h1 class="text-900 font-bold text-5xl mb-2">404 Error Occured</h1>
                        <span class="text-600 mb-5">Requested resource is not available.</span>
                        <img src="assets/images/error/asset-error.svg" alt="Error" class="mb-5" width="80%">
                        <button pButton pRipple icon="pi pi-arrow-left" label="Go to Dashboard" class="p-button-text" [routerLink]="['/']"></button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,
    imports: [
        RouterModule,
        CommonModule,
        ButtonModule,
        InlineSVGModule
    ]
})
export class ErrorComponent { 
    public readonly layoutService = inject(LayoutService);
}