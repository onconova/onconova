import { Component, Input, forwardRef, input } from '@angular/core';
import { ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { InputNumberModule } from 'primeng/inputnumber';

@Component({
    selector: 'pop-range-input',
    template: `
        <div class="p-fluid p-grid flex gap-1 align-items-center">
            <div class="p-col">
                <span class="p-float-label">
                    <p-inputnumber
                        [ngModel]="start"
                        (ngModelChange)="onStartChange($event)"
                        [disabled]="disabled()"
                        placeholder="Enter a value"
                        useGrouping="false"
                        mode="decimal"
                        [minFractionDigits]="1"
                        [maxFractionDigits]="3"
                        locale="en-US"/>
                </span>
            </div>
            <div>-</div>
            <div class="p-col">
                <span class="p-float-label">
                    <p-inputnumber
                        [ngModel]="end"
                        (ngModelChange)="onEndChange($event)"
                        [disabled]="disabled()"
                        placeholder="Enter a value"
                        useGrouping="false"
                        mode="decimal"
                        [minFractionDigits]="1"
                        [maxFractionDigits]="3"
                        locale="en-US"/>
                </span>
            </div>
        </div>
    `,
    imports: [FormsModule, InputNumberModule],
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => RangeInputComponent),
            multi: true
        }
    ]
})
export class RangeInputComponent implements ControlValueAccessor {

    disabled = input<boolean>(false);

    start: number | null = null;
    end: number | null = null;

    private onChange: any = () => {};
    private onTouched: any = () => {};

    writeValue(value: { start: number | null, end: number | null } | null): void {
        if (value) {
            this.start = value.start ?? null;
            this.end = value.end ?? null;
        } else {
            this.start = null;
            this.end = null;
        }
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    onStartChange(value: number | null) {
        this.start = value;
        // Validation: start cannot be after end
        if (this.start !== null && this.end !== null && this.start > this.end) {
            this.end = this.start;
        }
        this.propagateChange();
    }

    onEndChange(value: number | null) {
        this.end = value;
        // Validation: start cannot be after end
        if (this.start !== null && this.end !== null && this.start > this.end) {
            this.start = this.end;
        }
        this.propagateChange();
    }

    propagateChange() {
        this.onChange({ start: this.start, end: this.end });
        this.onTouched();
    }
}