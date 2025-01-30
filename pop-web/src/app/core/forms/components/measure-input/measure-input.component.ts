import { Component, Input, forwardRef, inject } from '@angular/core';
import { ControlValueAccessor, AbstractControl, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule} from '@angular/common';
import { Observable, map } from 'rxjs';
import { ReactiveFormsModule } from '@angular/forms';
import { InputGroup } from 'primeng/inputgroup';
import { InputNumber } from 'primeng/inputnumber';
import { Select } from 'primeng/select';

import { MeasuresService, MeasureSchema } from 'src/app/shared/openapi';

export interface MeasureUnit {
    unit: string 
    display: string
}

@Component({
    standalone: true,
    selector: 'measure-input',
    templateUrl: './measure-input.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MeasureInputComponent),
            multi: true,
        },
    ],
    imports: [
        CommonModule,
        FormsModule, 
        ReactiveFormsModule,
        InputNumber,
        InputGroup,
        Select,
    ]
})
export class MeasureInputComponent implements ControlValueAccessor {
    
    private measuresService = inject(MeasuresService);

    @Input() formControlName!: string;
    @Input() measure!: string;
    public defaultUnit$!: Observable<MeasureUnit>;
    public allowedUnits$!: Observable<MeasureUnit[]>
    public selectedUnit!: MeasureUnit;
    public inputValue!: number;

    private formControl = new FormControl<MeasureSchema|null>(null);

    ngOnInit() {
        this.allowedUnits$ = this.measuresService.getMeasureUnits({measureName: this.measure}).pipe(
            map((units):MeasureUnit[] => units.map((unit): MeasureUnit => {
                return {
                    unit: unit as string,
                    display: unit?.replace('__', '/').replace('_',' ') as string,
                }
            }))
        );
        this.defaultUnit$ = this.measuresService.getMeasureDefaultUnits({measureName: this.measure}).pipe(
            map((unit):MeasureUnit => {
                const defaultUnit =  {
                    unit: unit,
                    display: unit.replace('__', '/').replace('_',' '),
                };
                this.selectedUnit = defaultUnit; 
                return defaultUnit
            })
        );
    }
    updateFormControlValue() {
        if (this.inputValue && this.selectedUnit) {
            this.formControl.setValue({
                value: this.inputValue,
                unit: this.selectedUnit.unit,
            });
        } else {
            this.formControl.setValue(null)
        }
      }

    writeValue(value: any): void {
        if (value) {
            this.inputValue = value.value;
            this.selectedUnit = {
                unit: value.unit,
                display: value.unit.replace('__', '/').replace('_',' '),
            }
        }
        this.formControl.setValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }
}