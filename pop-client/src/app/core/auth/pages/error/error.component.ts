import { Component, inject } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { InlineSVGModule } from 'ng-inline-svg-2';

import { LayoutService } from 'src/app/core/layout/service/app.layout.service';

@Component({
    standalone: true,
    selector: 'pop-error',
    templateUrl: './error.component.html',
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