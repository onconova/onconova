// dynamic-form-modal.component.ts
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AvatarModule } from 'primeng/avatar';
import { DialogModule } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';

import { LucideAngularModule } from 'lucide-angular';
import { DynamicDialogConfig, DynamicDialogRef } from 'primeng/dynamicdialog';

@Component({
    selector: 'onconova-modal-form-header',
    template: `
        <div class="flex">
            <p-avatar size="large">
                <lucide-angular [img]="config.data.icon"></lucide-angular>
            </p-avatar>
            <div class="ml-2 mr-auto my-auto">
                <div class="title">
                    {{ config.data.title }}
                </div>
                <div class="subtitle text-muted">
                    {{ config.data.subtitle }}
                </div>
            </div>
            <p-button styleClass="form-close-button" (click)="ref.close()" class="my-auto">
                <i class="pi pi-times"></i>
            </p-button>
        </div>
        <p-divider />
    `,
    imports: [
        LucideAngularModule,
        CommonModule,
        AvatarModule,
        DialogModule,
        ButtonModule,
        DividerModule,
    ]
})
export class ModalFormHeaderComponent {

    readonly ref  = inject(DynamicDialogRef)
    readonly config = inject(DynamicDialogConfig)  

}