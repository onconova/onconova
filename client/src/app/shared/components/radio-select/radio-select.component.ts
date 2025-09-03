/**
 * A reusable Angular component for rendering a group of radio buttons using PrimeNG's `p-radiobutton`.
 * Implements `ControlValueAccessor` for use with Angular forms.
 *
 * - The `choices` input is required and should be an array of objects with `name` and `value` properties.
 * - The `class` input allows custom styling of the radio group container.
 * - Integrates seamlessly with reactive and template-driven forms.
 * - Uses the new Angular `input()` function for input binding.
 *
 * ```html
 * <onconova-radio-select
 *   [choices]="[{ name: 'Option 1', value: 1 }, { name: 'Option 2', value: 2 }]"
 *   [class]="'my-custom-class'"
 *   [(ngModel)]="selectedValue">
 * </onconova-radio-select>
 * 
 * ```
 */
import { Component, Input, forwardRef, input } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule} from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RadioButton } from 'primeng/radiobutton';

export interface RadioChoice {
    name: string 
    value: any
}


@Component({
    selector: 'onconova-radio-select',
    template: `
        <div [ngClass]="class()">
            @for (choice of choices(); track choice.value;) {
                <div class="flex items-center">
                    <p-radiobutton 
                        [inputId]="choice.value" 
                        [value]="choice.value" 
                        [formControl]="formControl"/>
                    <label [for]="choice.value" class="ml-2">{{ choice.name }}</label>
                </div>               
            }
        </div>
    `,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => RadioSelectComponent),
            multi: true,
        },
    ],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        RadioButton
    ]
})
export class RadioSelectComponent implements ControlValueAccessor {
    
    public choices = input.required<RadioChoice[]>();
    public class = input<String>('flex flex-wrap gap-4');

    public formControl = new FormControl<RadioChoice|null>(null);

    writeValue(value: any): void {
        this.formControl.setValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }
}