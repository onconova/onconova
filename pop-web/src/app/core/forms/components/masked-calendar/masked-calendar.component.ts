import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule, DatePipe} from '@angular/common';
import { DatePicker, DatePickerTypeView} from 'primeng/datepicker';
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
    @Input() selectionMode: "single" | "multiple" | "range" | undefined = 'single';
    @Input() view: DatePickerTypeView = 'date';

    private dateStringFormat: string = 'DD/MM/YYYY'
    public readonly minDate: Date = moment().subtract(200, 'years').toDate();
    public readonly maxDate: Date = moment().toDate();
    public formControl: FormControl = new FormControl();

    writeValue(value: any): void {
        if (value?.start || value?.end) {
            const start_date = new Date(value.start);
            const end_date = new Date(value.end);
            value = `${moment(start_date).format(this.dateStringFormat)} - ${moment(end_date).format(this.dateStringFormat)}`;
        }
        else if (value) {
            const date = new Date(value);
            value = moment(date).format(this.dateStringFormat);
        }
        console.log('DataField', value)
        this.formControl.patchValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }
}