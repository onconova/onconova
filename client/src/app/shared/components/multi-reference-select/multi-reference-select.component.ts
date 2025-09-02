import { Component, forwardRef, input } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule} from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MultiSelectModule } from 'primeng/multiselect';

// Define the interface for the Reference object
interface Reference {
    id: string;
    description: string;
}

/**
 * MultiReferenceSelectComponent
 * 
 * A reusable Angular component for selecting multiple references from a list.
 * Utilizes PrimeNG's MultiSelect UI component and integrates with Angular forms via ControlValueAccessor.
 * 
 * - The `options` input must be an array of objects implementing the `Reference` interface ({ id: string, description: string }).
 * - Designed for use in reactive forms; supports form validation and value access.
 * 
 * ```html
 * <onconova-multi-reference-select
 *   [options]="referenceList"
 *   [placeholder]="'Choose references'"
 *   [formControl]="myFormControl">
 * </onconova-multi-reference-select>
 * ```
 * 
 */
@Component({
    selector: 'onconova-multi-reference-select',
    template: `
    <p-multiselect 
        [options]="options()" 
        [formControl]="formControl"
        [placeholder]="placeholder()" 
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
    
    public options = input.required<Reference[]>();
    public placeholder = input<string>('Select one or more options');
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