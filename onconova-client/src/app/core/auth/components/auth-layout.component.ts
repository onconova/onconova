import { Component, contentChild, inject, TemplateRef } from '@angular/core';
import { LayoutService } from '../../layout/app.layout.service'
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { FluidModule } from 'primeng/fluid';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';

@Component({
    selector: 'onconova-auth-layout',
    template: `
    <div class="flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
        <div class="flex flex-column align-items-center justify-content-center">
            <div [inlineSVG]="logo" class="onconova-logo w-8rem h-8rem mr-3 mb-3" alt="Onconova logo"></div>            
            <div style="border-radius:56px; padding:0.3rem; background: linear-gradient(180deg, var(--p-primary-color) 10%, rgba(33, 150, 243, 0) 30%); min-width: 40rem;">
                <div class="w-full surface-card py-8 px-5 sm:px-8" style="border-radius:53px; background: var(--p-content-background) !important;">                
                    <ng-container *ngTemplateOutlet="inside()"></ng-container>
                </div>
            </div>
        @if (outside(); as outside) {
            <div>
                <ng-container *ngTemplateOutlet="outside"></ng-container>
            </div>
        }
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
]
})
export class AuthLayoutComponent {

    readonly inside = contentChild.required<TemplateRef<any>>('inside', { descendants: false });
    readonly outside = contentChild<TemplateRef<any>>('outside', { descendants: false });


    #layoutService = inject(LayoutService);
    protected logo = this.#layoutService.logo
}