import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorRoutingModule } from './error-routing.module';
import { ErrorComponent } from './error.component';
import { ButtonModule } from 'primeng/button';
import { InlineSVGModule } from 'ng-inline-svg-2';

@NgModule({
    imports: [
        CommonModule,
        ErrorRoutingModule,
        InlineSVGModule,
        ButtonModule
    ],
    declarations: [ErrorComponent]
})
export class ErrorModule { }
