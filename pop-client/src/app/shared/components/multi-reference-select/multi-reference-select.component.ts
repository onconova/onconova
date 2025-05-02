import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule} from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MultiSelectModule } from 'primeng/multiselect';

// Define the interface for the Reference object
interface Reference {
    id: string;
    description: string;
}

@Component({
    selector: 'pop-multi-reference-select',
    template: `
    <p-multiselect 
        [options]="options" 
        [formControl]="formControl"
        [placeholder]="placeholder" 
        optionLabel="description" 
        optionValue="id"
        filter="false"
        showToggleAll="false"
        display="chip"
        chipIcon="pi pi-times"
        appendTo="body"/>
    `,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MultiReferenceSelectComponent),
            multi: true,
        },
    ],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MultiSelectModule,
    ]
})
export class MultiReferenceSelectComponent implements ControlValueAccessor {
    
    @Input({required: true}) options!: Reference[];
    @Input() placeholder: string = 'Select one or more options';

    public formControl: FormControl = new FormControl();

    writeValue(value: any): void {
        this.formControl.patchValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }
}