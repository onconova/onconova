import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CodedConceptSelectComponent } from './coded-concept-select.component';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
    declarations: [
        CodedConceptSelectComponent
    ],
    imports: [
        CommonModule,
        AutoCompleteModule,
        ReactiveFormsModule,
    ],
    exports: [
        CodedConceptSelectComponent,
    ]
})
export class CodedConceptSelectModule { }
