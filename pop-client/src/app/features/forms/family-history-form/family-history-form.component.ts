import { Component, computed, effect, inject, input } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { toSignal } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { ToggleSwitchModule } from 'primeng/toggleswitch';

import { 
    FamilyHistory,
    FamilyHistoryCreate,
    FamilyHistoriesService,
    CodedConcept,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  RadioChoice,
  RadioSelectComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
    selector: 'family-history-form',
    templateUrl: './family-history-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        InputNumber,
        ButtonModule,
        ToggleSwitchModule,
        ConceptSelectorComponent,
        RadioSelectComponent,
        FormControlErrorComponent,
    ]
})
export class FamilyHistoryFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
  public initialData = input<FamilyHistory>();

  // Service injections using Angular's `inject()` API
  readonly #familyHistoriesService: FamilyHistoriesService = inject(FamilyHistoriesService)
  readonly #fb = inject(FormBuilder)

    // Create and update service methods for the form data
  public readonly createService = (payload: FamilyHistoryCreate) => this.#familyHistoriesService.createFamilyHistory({familyHistoryCreate: payload});
  public readonly updateService = (id: string, payload: FamilyHistoryCreate) => this.#familyHistoriesService.updateFamilyHistory({familyHistoryId: id, familyHistoryCreate: payload})

  // Reactive form definition
  public form = this.#fb.group({
    date: this.#fb.control<string | null>(null, Validators.required),
    relationship: this.#fb.control<CodedConcept | null>(null, Validators.required),
    hadCancer: this.#fb.control<boolean>(false, Validators.required),
    contributedToDeath: this.#fb.control<boolean | null>(null),
    onsetAge: this.#fb.control<number | null>(null),
    topography: this.#fb.control<CodedConcept | null>(null),
    morphology: this.#fb.control<CodedConcept | null>(null),
  });

  readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;
  
    this.form.patchValue({
      date: data.date ?? null,
      relationship: data.relationship ?? null,
      hadCancer: data.hadCancer ?? false,
      contributedToDeath: data.contributedToDeath ?? null,
      onsetAge: data.onsetAge ?? null,
      topography: data.topography ?? null,
      morphology: data.morphology ?? null,
    });
  });

  payload = (): FamilyHistoryCreate => {    
    const data = this.form.value
    return {
      caseId: this.caseId(),
      date: data.date!,
      relationship: data.relationship!,
      hadCancer: data.hadCancer!,
      contributedToDeath: data.contributedToDeath,
      onsetAge: data.onsetAge,
      topography: data.topography,
      morphology: data.morphology,
    };
  }

  // Signal to track the had cancer flag from form changes
  #hadCancer = toSignal(this.form.controls['hadCancer'].valueChanges, { initialValue: this.initialData()?.hadCancer! })
  // Effect to reset condition selections when the hadCancer value changes
  #hadCancerChanged = effect(() => {
    if (!this.#hadCancer()) {
      ['contributedToDeath', 'onsetAge', 'topography', 'morphology'].forEach(
        (field: string) => {
            this.form.get(field)!.setValue(null)
        })
    }
  })

  public readonly contributedToDeathChoices : RadioChoice[] = [
      {name: 'Unknown', value: null},
      {name: 'Yes', value: true},
      {name: 'False', value: false},
  ]


}