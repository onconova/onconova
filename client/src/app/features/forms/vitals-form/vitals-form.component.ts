import { Component, computed, effect, inject, input} from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectModule } from 'primeng/select';

import { 
    Measure,
    Vitals,
    VitalsCreate,
    VitalsService,
} from 'onconova-api-client'

import { 
  DatePickerComponent,
  FormControlErrorComponent,
  MeasureInputComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';


@Component({
    selector: 'vitals-form',
    templateUrl: './vitals-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        SelectModule,
        DatePickerComponent,
        Fluid,
        ButtonModule,
        MeasureInputComponent,
        FormControlErrorComponent,
    ]
})
export class VitalsFormComponent extends AbstractFormBase{

    // Input signal for initial data passed to the form
    initialData = input<Vitals>();

    // Service injections
    readonly #vitalsService = inject(VitalsService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: VitalsCreate) => this.#vitalsService.createVitals({vitalsCreate: payload});
    public readonly updateService = (id: string, payload: VitalsCreate) => this.#vitalsService.updateVitalsById({vitalsId: id, vitalsCreate: payload});

    // Define the form
    public form = this.#fb.group({
        date: this.#fb.control<string | null>(null, Validators.required),
        height: this.#fb.control<Measure | null>(null),
        weight: this.#fb.control<Measure | null>(null),
        bloodPressureDiastolic: this.#fb.control<Measure | null>(null),
        bloodPressureSystolic: this.#fb.control<Measure | null>(null),
        temperature: this.#fb.control<Measure | null>(null),
      }, { validators: this.atLeastOneValueValidator });

    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;
        
        this.form.patchValue({
            date: data.date ?? null,
            height: data.height ?? null,
            weight: data.weight ?? null,
            bloodPressureDiastolic: data.bloodPressureDiastolic ?? null,
            bloodPressureSystolic: data.bloodPressureSystolic ?? null,
            temperature: data.temperature ?? null,
        });
    });
        
    // API Payload construction function
    payload = (): VitalsCreate => {    
        const data = this.form.value;
        return {
            caseId: this.caseId(),
            date: data.date,
            height: data.height,
            weight: data.weight,
            bloodPressureDiastolic: data.bloodPressureDiastolic,
            bloodPressureSystolic: data.bloodPressureSystolic,
            temperature: data.temperature
        };
    }

    private atLeastOneValueValidator(formGroup: FormGroup) {
        const values = Object.values(formGroup.controls);
        const hasNonNullValue = values.some((control: any) => control.value !== null && control !== formGroup.get('date'));
        return hasNonNullValue ? null : { atLeastOneValue: true };
    };

}