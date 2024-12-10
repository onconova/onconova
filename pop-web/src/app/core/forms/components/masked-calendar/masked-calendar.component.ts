import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule, DatePipe} from '@angular/common';
import { DatePicker, DatePickerTypeView } from 'primeng/datepicker';
import { ReactiveFormsModule } from '@angular/forms';
import { DateMaskDirective } from '../directives/date-mask-directive';
import * as moment from 'moment'; 

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
        DatePicker,
        DateMaskDirective,
    ]
})
export class MaskedCalendarComponent implements ControlValueAccessor {
    

    @Input() formControlName!: string;
    @Input() dateFormat: string = 'dd/mm/yy';
    @Input() placeholder: string = 'DD/MM/YYYY';
    @Input() view: DatePickerTypeView = 'date';


    public formControl: FormControl = new FormControl();

    writeValue(value: any): void {
        console.log('writeValue(',value,')')
        if (value) {
            const date = new Date(value);
            value = moment(date).format(this.placeholder);
        }
        this.formControl.patchValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }
}