import { Component, inject, input, computed, effect} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';

import { 
    NeoplasticEntitiesService, 
    RiskAssessmentCreate,
    RiskAssessmentsService,
    RiskAssessment,
    CodedConcept,
    TerminologyService,
} from 'pop-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { RadioButton } from 'primeng/radiobutton';

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
        RadioButton,
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
  readonly #terminologyService = inject(TerminologyService);
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

  public riskClassifications = rxResource({
    request: () => ({terminologyName: "CancerRiskAssessmentClassification", codes: this.allowedRiskClassificationCodes()}),
    loader: ({request}) => this.#terminologyService.getTerminologyConcepts(request).pipe(map(response => response.items))
  })

  // All neoplastic entities related to this patient case
  public relatedEntities = rxResource({
    request: () => ({caseId: this.caseId()}),
    loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
  }) 

  readonly #methodologyValue = toSignal(this.form.controls.methodology.valueChanges)
  private allowedRiskClassificationCodes = computed(() => {
    switch (this.#methodologyValue()?.code) {

      case "C136962": // Follicular Lymphoma International Prognostic Index (FLIPI)
        return [
          "C136965", // FLIPI Score 0-1, Low Risk
          "C136967", // FLIPI Score 2, Intermediate Risk
          "C136968", // FLIPI Score Greater than or Equal to 3, High Risk
        ];

      case "C181086": // D'Amico Prostate Cancer Risk Classification
        return [
          "C102403", // Low risk
          "C102402", // Intermediate risk
          "C102401", // High risk
        ];

      case "C127872": // European Treatment Outcome Study (EUTOS) Score
        return [
          "C102403", // Low risk
          "C102401", // High risk
        ];

      case "C127873": // Hasford Score
        return [
          "C102403", // Low risk
          "C102402", // Intermediate risk
          "C102401", // High risk
        ];

      case "C127875": // Sokal Score
        return [
          "C102403", // Low risk
          "C102402", // Intermediate risk
          "C102401", // High risk
        ];

      case "C155843": // International Metastatic Renal Cell Carcinoma Database Consortium (IMDC) Criteria
        return [
          "C155844", // IMDC Favorable risk
          "C155845", // IMDC Intermediate Risk
          "C155846", // IMDC Poor risk
        ];

      case "C161805": // International Prognostic Index (IPI) Risk Group
        return [
          "C161809", // High Risk
          "C161808", // High-Intermediate Risk
          "C161806", // Low Risk
          "C161807", // Low-Intermediate Risk
        ];

      case "C177562": // European LeukemiaNet Risk Classification
        return [
          "C188368", // Adverse-Risk Category
          "C188369", // Favorable-Risk Category
          "C188370", // Intermediate-Risk Category
        ];

      case "C121007": // Child-Pugh Clinical Classification
        return [
          "C113691", // Class A
          "C146790", // Class A5
          "C146791", // Class A6
          "C113692", // Class B
          "C146792", // Class B7
          "C146793", // Class B8
          "C146794", // Class B9
          "C113694", // Class C
          "C146795", // Class C10
          "C146796", // Class C11
          "C146797", // Class C12
          "C146798", // Class C13
          "C146799", // Class C14
          "C146801", // Class C15
          "C148151", // A-B7 Cirrhosis
        ];

      case "C181085": // UCSF Cancer of the Prostate Risk Assessment Score
        return [
          "C102403", // Low risk
          "C102402", // Intermediate risk
          "C102401", // High risk
        ];

      case "C162781": // Mantle Cell Lymphoma International Prognostic Index (MIPI)
        return [
          "C102403", // Low risk
          "C102402", // Intermediate risk
          "C102401", // High risk
        ];

      case "C181084": // NCCN Prostate Cancer Risk Stratification for Clinically Localized Disease
        return [
          "C192873", // Very Low Risk Group
          "C192874", // Low Risk Group
          "C192877", // Unfavorable-Intermediate Risk Group
          "C192876", // Favorable-Intermediate Risk Group
          "C192875", // Intermediate Risk Group
          "C192878", // High Risk Group
          "C192879", // Very High Risk Group
        ];

      case "C177309": // Seminoma IGCCC Risk Classification
        return [
          "C177313", // Good
          "C177314", // Intermediate
        ];

      case "C177308": // Non-Seminomatous Germ Cell Tumor IGCCC Risk Classification
        return [
          "C177310", // Good
          "C177311", // Intermediate
          "C177312", // Poor
        ];

      case "C142346": // International Society of Urological Pathology Gleason Grade Group
        return [
          "C162654", // Grade Pattern 1
          "C162655", // Grade Pattern 2
          "C162656", // Grade Pattern 3
          "C162657", // Grade Pattern 4
          "C162658", // Grade Pattern 5
        ];

      default:
        return [];
    }
  });

}