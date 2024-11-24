import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CodedConceptSelectComponent } from './coded-concept-select.component';
import { AutoCompleteModule } from 'primeng/autocomplete';

@NgModule({
    declarations: [
        CodedConceptSelectComponent
    ],
    imports: [
        CommonModule,
        AutoCompleteModule,
    ],
    exports: [
        CodedConceptSelectComponent,
    ]
})
export class CodedConceptSelectModule { }
