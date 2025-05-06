import { Component, effect, inject, input } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
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
  readonly #formBuilder = inject(FormBuilder)

    // Create and update service methods for the form data
  public readonly createService = (payload: FamilyHistoryCreate) => this.#familyHistoriesService.createFamilyHistory({familyHistoryCreate: payload});
  public readonly updateService = (id: string, payload: FamilyHistoryCreate) => this.#familyHistoriesService.updateFamilyHistory({familyHistoryId: id, familyHistoryCreate: payload})

  // Reactive form definition
  override form: FormGroup = this.#formBuilder.group({
    date: [Validators.required],
    relationship: [Validators.required],
    hadCancer: [Validators.required],
    contributedToDeath: [],
    onsetAge: [],
    topography: [],
    morphology: [],
  })

  // Effect to initialize form data when input changes
  readonly #initializeFormEffect = effect(() => this.initializeFormData(this.initialData()));

  // Signal to track the had cancer flag from form changes
  #hadCancer = toSignal(this.form.controls['hadCancer'].valueChanges, { initialValue: this.initialData()?.hadCancer })
  // Effect to reset condition selections when the hadCancer value changes
  #hadCancerChanged = effect(() => {
    if (!this.#hadCancer()) {
      ['contributedToDeath', 'onsetAge', 'topography', 'morphology'].forEach(
        (field: string) => {
            this.form.controls[field]!.setValue(null)
        })
    }
  })

  public readonly contributedToDeathChoices : RadioChoice[] = [
      {name: 'Unknown', value: null},
      {name: 'Yes', value: true},
      {name: 'False', value: false},
  ]

  // Populate form controls with initial data
  initializeFormData(data: FamilyHistory | undefined) {
    this.form.patchValue({
      date: data?.date,
      relationship: data?.relationship,
      hadCancer: data?.hadCancer,
      contributedToDeath: data?.contributedToDeath,
      onsetAge: data?.onsetAge,
      topography: data?.topography,
      morphology: data?.morphology,
    })
  }

  constructAPIPayload(data: any): FamilyHistoryCreate {    
    return {
      caseId: this.caseId(),
      date: data.date,
      relationship: data.relationship,
      hadCancer: data.hadCancer,
      contributedToDeath: data.contributedToDeath,
      onsetAge: data.onsetAge,
      topography: data.topography,
      morphology: data.morphology,
    };
  }


}