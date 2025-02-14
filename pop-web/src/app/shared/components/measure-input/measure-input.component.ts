import { Component, Input, forwardRef, inject } from '@angular/core';
import { ControlValueAccessor, FormsModule, FormControl, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable, map } from 'rxjs';
import { ReactiveFormsModule } from '@angular/forms';
import { InputGroup } from 'primeng/inputgroup';
import { InputNumber } from 'primeng/inputnumber';
import { Select } from 'primeng/select';

import { MeasuresService, Measure } from 'src/app/shared/openapi';

export interface MeasureUnit {
    unit: string; 
    display: string;
}

@Component({
    standalone: true,
    selector: 'pop-measure-input',
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
    ],
})
export class MeasureInputComponent implements ControlValueAccessor {
    
    private measuresService = inject(MeasuresService);

    // The specific measure (unit type) to fetch options for
    @Input({required: true}) measure!: string; 

    // Public observables for unit data
    public defaultUnit$!: Observable<MeasureUnit>;
    public allowedUnits$!: Observable<MeasureUnit[]>;

    // Local component state
    public selectedUnit!: MeasureUnit;
    public inputValue!: number | null;

    // Form control to track the value
    public formControl = new FormControl<Measure | null>(null);

    ngOnInit() {
        // Fetch allowed units for the given measure from the service
        this.allowedUnits$ = this.measuresService.getMeasureUnits({ measureName: this.measure }).pipe(
          map((units): MeasureUnit[] => units.map((unit): MeasureUnit => ({
            unit: unit as string,
            display: unit?.replace('__', '/').replace('_', ' ') as string,
          })))
        );
    
        // Fetch the default unit for the given measure from the service
        this.defaultUnit$ = this.measuresService.getMeasureDefaultUnits({ measureName: this.measure }).pipe(
          map((unit): MeasureUnit => {
            const defaultUnit = {
              unit: unit,
              display: unit.replace('__', '/').replace('_', ' '),
            };
            this.selectedUnit = defaultUnit; // Set default selected unit
            return defaultUnit;
          })
        );
      }
    
      // This method updates the form control's value when the user changes input or selects a unit
      updateFormControlValue() {
        // Only update if input value and selected unit are valid
        if (this.inputValue && this.selectedUnit) {
          this.formControl.setValue({
            value: this.inputValue,
            unit: this.selectedUnit.unit,
          });
        } else {
          this.formControl.setValue(null); // Clear value if inputs are invalid
        }
      }
    
      // Write value from the parent component into this component's form control
      writeValue(value: any): void {
        if (value) {
          this.inputValue = value.value;
          this.selectedUnit = {
            unit: value.unit,
            display: value.unit.replace('__', '/').replace('_', ' '),
          };
        }
        this.formControl.setValue(value);
      }
    
      // Register on change function to propagate changes to the parent form
      registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
      }
    
      // Register on touched function to mark the form as touched when the user interacts with it
      registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
      }
    }
    