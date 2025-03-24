import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule} from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RadioButton } from 'primeng/radiobutton';

export interface RadioChoice {
    name: string 
    value: any
}

@Component({
    standalone: true,
    selector: 'pop-radio-select',
    template: `
        <div class="{{class}}">
            <ng-container *ngFor="let choice of choices">
                <div class="flex items-center">
                    <p-radiobutton 
                        [inputId]="choice.value" 
                        [value]="choice.value" 
                        [formControl]="formControl"/>
                    <label [for]="choice.value" class="ml-2">{{ choice.name }}</label>
                </div>
            </ng-container>
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
    
    @Input() choices: RadioChoice[] = [];
    @Input() class: string = 'flex flex-wrap gap-4';

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