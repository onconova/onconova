import { Component, inject, input, computed, effect} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs';
import { rxResource } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';

import { 
    NeoplasticEntitiesService, 
    RiskAssessmentCreate,
    RiskAssessmentsService,
    RiskAssessment,
    CodedConcept,
} from 'pop-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
    selector: 'risk-assessment-form',
    templateUrl: './risk-assessment-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        InputNumber,
        ButtonModule,
        ConceptSelectorComponent,
        MultiReferenceSelectComponent,
        FormControlErrorComponent,
    ]
})
export class RiskAssessmentFormComponent extends AbstractFormBase {

  // Input signal for initial data passed to the form
  initialData = input<RiskAssessment>();

  // Service injections
  readonly #riskAssessmentsService = inject(RiskAssessmentsService)
  readonly #neoplasticEntitiesService = inject(NeoplasticEntitiesService)
  readonly #fb = inject(FormBuilder)

  // Create and update service methods for the form data
  public readonly createService = (payload: RiskAssessmentCreate) => this.#riskAssessmentsService.createRiskAssessment({riskAssessmentCreate: payload})
  public readonly updateService = (id: string, payload: RiskAssessmentCreate) => this.#riskAssessmentsService.updateRiskAssessmentById({riskAssessmentId: id, riskAssessmentCreate: payload})

  // Static form definition
  public form = this.#fb.group({
    date: this.#fb.control<string | null>(null, Validators.required),
    assessedEntities: this.#fb.control<string[]>([], Validators.required),
    methodology: this.#fb.control<CodedConcept | null>(null, Validators.required),
    risk: this.#fb.control<CodedConcept | null>(null, Validators.required),
    score: this.#fb.control<number | null>(null),
  });

  // Effect to patch initial data
  readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;
    this.form.patchValue({
      date: data.date ?? null,
      assessedEntities: data.assessedEntitiesIds ?? [],
      methodology: data.methodology ?? null,
      risk: data.risk ?? null,
      score: data.score ?? null,
    });
  });

  // API Payload construction function
  payload = (): RiskAssessmentCreate => {
    const data = this.form.value;    
    return {
      caseId: this.caseId(),
      assessedEntitiesIds: data.assessedEntities!,
      date: data.date!,
      methodology: data.methodology!,
      risk: data.risk!,
      score: data.score ?? undefined,
    };
  }

  // All neoplastic entities related to this patient case
  public relatedEntities = rxResource({
    request: () => ({caseId: this.caseId()}),
    loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
  }) 

}