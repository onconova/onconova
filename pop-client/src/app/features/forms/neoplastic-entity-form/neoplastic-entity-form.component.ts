import { Component, computed, effect, inject, input, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


import { 
  NeoplasticEntity, 
  NeoplasticEntitiesService,
  NeoplasticEntityRelationshipChoices, 
  NeoplasticEntityCreate,
  CodedConcept,
  PaginatedNeoplasticEntity
} from 'pop-api-client'

import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { Fluid } from 'primeng/fluid';

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent 
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { EmptyObject } from 'chart.js/dist/types/basic';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';

@Component({
    selector: 'neoplastic-entity-form',
    templateUrl: './neoplastic-entity-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        Select,
        ButtonModule,
        ConceptSelectorComponent,
        FormControlErrorComponent,
    ]
})
export class NeoplasticEntityFormComponent extends AbstractFormBase{

  // Input signal for initial data passed to the form
  initialData = input<NeoplasticEntity>();

  // Service injections
  readonly #neoplasticEntitiesService = inject(NeoplasticEntitiesService)
  readonly #fb = inject(FormBuilder)

  // Create and update service methods for the form data  
  public readonly createService = (payload: NeoplasticEntityCreate) => this.#neoplasticEntitiesService.createNeoplasticEntity({neoplasticEntityCreate: payload})
  public readonly updateService = (id: string, payload: NeoplasticEntityCreate) => this.#neoplasticEntitiesService.updateNeoplasticEntityById({entityId: id, neoplasticEntityCreate: payload})

  // Define the form
  public form = this.#fb.group({
    relationship: this.#fb.nonNullable.control<NeoplasticEntityRelationshipChoices>(
      NeoplasticEntityRelationshipChoices.Primary,  // Default value
      Validators.required
    ),
    assertionDate: this.#fb.control<string | null>(
      null, // Default value
      Validators.required
    ),
    relatedPrimary: this.#fb.control<string | null>(
      null, // Default value
      Validators.required
    ),
    topography: this.#fb.control<CodedConcept | null>(
      null, // Default value
      Validators.required
    ),
    morphology: this.#fb.control<CodedConcept | null>(
      null, // Default value
      Validators.required
    ),
    laterality: this.#fb.control<CodedConcept | null>(
      null  // Default value
    ),
    differentiation: this.#fb.control<CodedConcept | null>(
      null  // Default value
    ),
  });

  // Effect to patch initial data
  readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;

    this.form.patchValue({
      relationship: data.relationship ?? NeoplasticEntityRelationshipChoices.Primary,
      assertionDate: data.assertionDate ?? null,
      relatedPrimary: data.relatedPrimaryId ?? null,
      topography: data.topography ?? null,
      morphology: data.morphology ?? null,
      laterality: data.laterality ?? null,
      differentiation: data.differentitation ?? null,
    });
  });

  // API payload construction function
  payload = (): NeoplasticEntityCreate => {
    const data = this.form.value;    
    return {
      caseId: this.caseId(),
      relationship: data.relationship!,
      assertionDate: data.assertionDate!,
      topography: data.topography!,
      relatedPrimaryId: data.relatedPrimary ?? undefined,
      morphology: data.morphology!,
      laterality: data.laterality ?? undefined,
      differentitation: data.differentiation ?? undefined,
    };
  }

  // Primary neoplastic entities that could be related to a new entry 
  relatedPrimaries = rxResource({
    request: () => ({caseId: this.caseId(), relationship: NeoplasticEntityRelationshipChoices.Primary}),
    loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map((data: PaginatedNeoplasticEntity) => data.items))
  })

  // Trigger signals for the neoplastic entity relationship changes
  #currentNeoplasticRelationship = toSignal(this.form.get('relationship')!.valueChanges, {initialValue: this.initialData()?.relationship || NeoplasticEntityRelationshipChoices.Primary});

  // Dynamically adapt the need for a related primary based on the neoplastic entity relationship
  public requiresPrimary = computed(() => ['metastatic', 'local_recurrence', 'regional_recurrence'].includes(this.#currentNeoplasticRelationship()!));

  // Dynamically adapt the terminology used for the morphology field based on the neoplastic entity relationship
  public morphologyTerminology = computed(() => this.#currentNeoplasticRelationship() === NeoplasticEntityRelationshipChoices.Metastatic ? 'CancerMorphologyMetastatic' : 'CancerMorphologyPrimary');

  // Dynamically change the requirements of the form based on changes of the neoplastic relationship
  #relatedPrimaryUpdate = effect(() => {
    const relatedPrimaryControl = this.form.get('relatedPrimary')
    if (this.#currentNeoplasticRelationship() === NeoplasticEntityRelationshipChoices.Primary) {
      relatedPrimaryControl?.removeValidators(Validators.required);
    } else {
      relatedPrimaryControl?.addValidators(Validators.required);
    }  
    relatedPrimaryControl?.updateValueAndValidity();
  })

  // Define options for UI elements
  public relationshipOptions = [
    { name: 'Primary', code: NeoplasticEntityRelationshipChoices.Primary },
    { name: 'Metastatic', code: NeoplasticEntityRelationshipChoices.Metastatic },
    { name: 'Local recurrence', code: NeoplasticEntityRelationshipChoices.LocalRecurrence },
    { name: 'Regional recurrence', code: NeoplasticEntityRelationshipChoices.RegionalRecurrence },
  ]

}