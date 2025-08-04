import { Component, forwardRef, input } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule, formatDate} from '@angular/common';
import { DatePicker, DatePickerTypeView} from 'primeng/datepicker';
import { ReactiveFormsModule } from '@angular/forms';
import { DateMaskDirective } from '../../directives/date-mask-directive';
import { Message } from 'primeng/message';

@Component({
    selector: 'pop-datepicker',
    template: `
        <p-datepicker 
            [formControl]="formControl"
            [view]="view()"
            [showIcon]="true"
            [showOnFocus]="false"
            [dateFormat]="dateFormat()" 
            [placeholder]="placeholder()" 
            [selectionMode]="selectionMode()"
            [minDate]="minDate"
            [maxDate]="maxDate"
            [keepInvalid]="true"
            dataType="string"
            appendTo="body"
            dateMask 
            />
        @if (formControl.errors?.['invalidDate']) {
            <p-message severity="error" text="Invalid date"></p-message>
        }
        @if (formControl.errors?.['invalidPeriod']) {
            <p-message severity="error" text="Period's start date must be before end date"></p-message>
        }
        @if (formControl.errors?.['tooFarInThePast']) {
            <p-message severity="error" text="Date too far in the past"></p-message>
        }
        @if (formControl.errors?.['tooFarInTheFuture']) {
            <p-message severity="error" text="Date cannot be in the future"></p-message>
        }
    `,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => DatePickerComponent),
            multi: true,
        },
    ],
    imports: [
        CommonModule,
        Message,
        FormsModule,
        ReactiveFormsModule,
        DatePicker,
        DateMaskDirective,
    ]
})
export class DatePickerComponent implements ControlValueAccessor {
    
    // Input properties to customize the date picker behavior
    public dateFormat = input<string>('dd/mm/yy');
    public placeholder = input<string>('DD/MM/YYYY');
    public selectionMode = input<"single" | "multiple" | "range" | undefined>('single');
    public view = input<DatePickerTypeView>('date');

    public readonly minDate: Date = new Date(new Date().setFullYear(new Date().getFullYear() - 200));
    public readonly maxDate: Date = new Date();
    
    // Functions to call when form control's value changes or is touched
    public formControl: FormControl = new FormControl();
    private onChange: (value: any) => void = () => {};
    private onTouched: () => void = () => {};

    // Writes a new value to the element
    writeValue(value: any): void {
        if (value?.start || value?.end) {
            // Range selection: Convert ISO -> User-friendly format
            const start_date = new Date(value.start);
            const end_date = new Date(value.end);
            const displayValue = `${this.formatDateToDisplayFormat(start_date)} - ${this.formatDateToDisplayFormat(end_date)}`;
            this.formControl.setValue(displayValue, { emitEvent: false });
        } else if (value) {
            // Single date: Convert ISO -> User-friendly format
            const date = new Date(value);
            const displayValue = this.formatDateToDisplayFormat(date);
            this.formControl.setValue(displayValue, { emitEvent: false });
        } else {
            this.formControl.setValue(null, { emitEvent: false });
        }
    }
    
    // Registers a callback function that is called when the control's value changes in the UI
    registerOnChange(fn: any): void {
        this.onChange = fn;
        this.formControl.valueChanges.subscribe(val => {
            if (!val) {
                this.onChange(null);
                return;
            }

            if (this.selectionMode() === 'range') {
                // Convert user-friendly format -> ISO for range
                const dates = val.includes(' - ') ? val.split(' - ') : val;
                if (dates.length === 2) {

                    const isoStart = this.parseToISO(dates[0]);
                    const isoEnd = this.parseToISO(dates[1]);
                    this.validatePeriod(isoStart, isoEnd);
                    this.onChange({ start: isoStart, end: isoEnd });
                }
            } else {
                // Convert user-friendly format -> ISO for single date
                const isoDate = this.parseToISO(val);
                this.validateDate(isoDate);
                this.onChange(isoDate);
            }
        });
    }

    // Registers a callback function that is called by the forms API on touch
    registerOnTouched(fn: any): void {
        this.onTouched = fn;
        this.formControl.valueChanges.subscribe(() => this.onTouched());
    }

    // Enables or disables the form control
    setDisabledState?(isDisabled: boolean): void {
        isDisabled ? this.formControl.disable() : this.formControl.enable();
    }

    formatDateToDisplayFormat(date: Date): string {
        // The dateFormat string must be reformated to the formatDate() data nomenclature
        return formatDate(date, this.dateFormat().replaceAll('m','M').replace('yy','yyyy'), 'en-US')
    }

    // Helper function to parse a date string into ISO format
    parseToISO(dateStr: string): string {
        let day, month, year;
        switch (this.dateFormat()) {
            case 'dd/mm/yy':
                [day, month, year] = dateStr.split('/');
                return `${year}-${month}-${day}`;
            case 'mm/yy':
                [month, year] = dateStr.split('/');
                return `${year}-${month}-01`;
            default:
                return dateStr
        }
    }


    validateDate(value: string) {
        const date = new Date(value);
        const validDate = isFinite(date.getTime());

        if (validDate) {
            const tooFarInThePast = date.getTime() < this.minDate.getTime();
            const tooFarInTheFuture = date.getTime() > this.maxDate.getTime();
            if (tooFarInThePast) {
                this.formControl.setErrors({'tooFarInThePast': true});
            }
            if (tooFarInTheFuture) {
                this.formControl.setErrors({'tooFarInTheFuture': true});
            } 
        } else {
            this.formControl.setErrors({'invalidDate': true});
        }
    }

    validatePeriod(start: string, end: string) {
        this.validateDate(start);
        this.validateDate(end);
        const startDate = new Date(start);
        const endDate = new Date(end);

        if (startDate && endDate) {
            const invalidPeriod = startDate.getTime() > endDate.getTime();
            if (invalidPeriod) {
                this.formControl.setErrors({'invalidPeriod': true});
            }
        }
    }
}
 