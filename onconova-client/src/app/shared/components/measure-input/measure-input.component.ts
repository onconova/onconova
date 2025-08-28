import { Component, effect, forwardRef, inject, input } from '@angular/core';
import { ControlValueAccessor, FormsModule, FormControl, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable, map, of } from 'rxjs';
import { ReactiveFormsModule } from '@angular/forms';
import { InputGroup } from 'primeng/inputgroup';
import { InputNumber } from 'primeng/inputnumber';
import { Select } from 'primeng/select';

import { MeasuresService, Measure } from 'onconova-api-client';
import { rxResource } from '@angular/core/rxjs-interop';

export interface MeasureUnit {
    unit: string; 
    display: string;
}

@Component({
    selector: 'onconova-measure-input',
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
    
  // Injected services
  readonly #measuresService = inject(MeasuresService);

  // The specific measure (unit type) to fetch options for
  public measure = input.required<string>();
  public defaultUnit = input<string>();

  // Public observables for unit data
  public defaultSelectedUnit$!: Observable<MeasureUnit>;
  public allowedUnits$!: Observable<MeasureUnit[]>;

  // Local component state
  public measureValue!: number | null;
  public measureUnit!: MeasureUnit;


  // Fetch allowed units for the given measure from the service
  public allowedUnits = rxResource({
    request: () => ({measureName: this.measure()}),
    loader: ({request}) => this.#measuresService.getMeasureUnits(request).pipe(
      map((units): MeasureUnit[] => units.map((unit): MeasureUnit => ({
        unit: unit as string,
        display: unit?.replace('__', '/').replace('_', ' ') as string,
      })))
    )
  }) 

  public defaultMeasureUnit = rxResource({
    request: () => ({measureName: this.measure()}),
    loader: ({request}) => this.defaultUnit() ? of({
      unit: this.defaultUnit()!.replace('/', '__').replace(' ', '_'), 
      display: this.defaultUnit()!.replace('__', '/').replace('_', ' ') 
    }) : this.#measuresService.getMeasureDefaultUnits(request).pipe(
      map((unit): MeasureUnit => ({
        unit: unit as string,
        display: unit?.replace('__', '/').replace('_', ' ') as string,
      }))
    )
  })

  #setDefaultUnitEffect = effect(() => {
    this.measureUnit = this.defaultMeasureUnit.value()!;
  })

  // Form control to track the value
  public formControl = new FormControl<Measure | null>(null);

  // This method updates the form control's value when the user changes input or selects a unit
  updateFormControlValue() {
    // Only update if input value and selected unit are valid
    if (this.measureValue && this.measureUnit) {
      this.formControl.setValue({
        value: this.measureValue,
        unit: this.measureUnit.unit,
      });
    } else {
      this.formControl.setValue(null); // Clear value if inputs are invalid
    }
  }

  // Write value from the parent component into this component's form control
  writeValue(value: any): void {
    if (value) {
      this.measureValue = value.value;
      this.measureUnit = {
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
    