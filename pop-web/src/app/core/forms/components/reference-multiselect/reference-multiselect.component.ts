import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule, DatePipe} from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MultiSelectModule } from 'primeng/multiselect';

@Component({
    standalone: true,
    selector: 'reference-multiselect',
    templateUrl: './reference-multiselect.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => ReferenceMultiSelect),
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
export class ReferenceMultiSelect implements ControlValueAccessor {
    

    @Input() formControlName!: string;
    @Input() references!: any[];

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