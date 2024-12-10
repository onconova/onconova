import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { CalendarModule, CalendarTypeView } from 'primeng/calendar';
import { ReactiveFormsModule } from '@angular/forms';
import { DateMaskDirective } from '../directives/date-mask-directive';

@Component({
    standalone: true,
    selector: 'masked-calendar',
    templateUrl: './masked-calendar.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MaskedCalendarComponent),
            multi: true,
        },
    ],
    imports: [
        CommonModule,
        FormsModule, 
        ReactiveFormsModule,
        CalendarModule,
        DateMaskDirective,
    ]
})
export class MaskedCalendarComponent implements ControlValueAccessor {
    

    @Input() formControlName!: string;
    @Input() dateFormat: string = 'dd/mm/yy';
    @Input() placeholder: string = 'DD/MM/YYYY';
    @Input() view: CalendarTypeView = 'date';


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