import { Component, computed, effect, inject, input} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectModule } from 'primeng/select';

import { 
    CodedConcept,
    Lifestyle,
    LifestyleCreate,
    LifestylesService,
    Measure,
} from 'pop-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  MeasureInputComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { InputNumber } from 'primeng/inputnumber';

@Component({
    selector: 'lifestyle-form',
    templateUrl: './lifestyle-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        SelectModule,
        DatePickerComponent,
        Fluid,
        ButtonModule,
        ConceptSelectorComponent,
        MeasureInputComponent,
        InputNumber,
        FormControlErrorComponent,
    ]
})
export class LifestyleFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<Lifestyle>();

    // Service injections
    readonly #lifestyleService: LifestylesService = inject(LifestylesService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: LifestyleCreate) => this.#lifestyleService.createLifestyle({lifestyleCreate: payload});
    public readonly updateService = (id: string, payload: LifestyleCreate) => this.#lifestyleService.updateLifestyleById({lifestyleId: id, lifestyleCreate: payload});

    // Define the form
    public form = this.#fb.group({
      date: this.#fb.control<string | null>(null, Validators.required),
      smokingStatus: this.#fb.control<CodedConcept | null>(null),
      smokingPackyears: this.#fb.control<number | null>(null),
      smokingQuited: this.#fb.control<Measure | null>(null),
      alcoholConsumption: this.#fb.control<CodedConcept | null>(null),
      nightSleep: this.#fb.control<Measure | null>(null),
      recreationalDrugs: this.#fb.control<CodedConcept[] | null>(null),
      exposures: this.#fb.control<CodedConcept[] | null>(null),
    });

    readonly #onInitialDataChangeEffect = effect((): void => {
      const data = this.initialData();
      if (!data) return;
    
      this.form.patchValue({
        date: data.date ?? null,
        smokingStatus: data.smokingStatus ?? null,
        smokingPackyears: data.smokingPackyears ?? null,
        smokingQuited: data.smokingQuited ?? null,
        alcoholConsumption: data.alcoholConsumption ?? null,
        nightSleep: data.nightSleep ?? null,
        recreationalDrugs: data.recreationalDrugs ?? null,
        exposures: data.exposures ?? null,
      });
    });

    // API Payload construction function
    payload = (): LifestyleCreate => {    
        const data = this.form.value;
        return {
            caseId: this.caseId(),
            date: data.date!,
            smokingStatus: data.smokingStatus ?? undefined,
            smokingPackyears: data.smokingPackyears ?? undefined,
            smokingQuited: data.smokingQuited ?? undefined,
            alcoholConsumption: data.alcoholConsumption ?? undefined,
            nightSleep: data.nightSleep ?? undefined,
            recreationalDrugs: data.recreationalDrugs ?? undefined,
            exposures: data.exposures ?? undefined,
        };
    }

    public readonly smokingStatusCodeClassification = {
        neverSmoker: '266919005',
        exSmoker: '8517006', 
    }



}