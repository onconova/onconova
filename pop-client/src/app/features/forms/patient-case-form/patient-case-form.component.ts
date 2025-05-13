import { Component, computed, effect, inject, input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PatientCaseCreate, PatientCasesService, PatientCaseConsentStatusChoices, PatientCase, CodedConcept } from '../../../shared/openapi'
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';

import { InlineSVGModule } from 'ng-inline-svg-2';

import { ButtonModule } from 'primeng/button';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { Fluid } from 'primeng/fluid';
import { StepperModule } from 'primeng/stepper';
import { InputTextModule } from 'primeng/inputtext';
import { AutoCompleteModule } from 'primeng/autocomplete';

import { AbstractFormBase } from '../abstract-form-base.component';
import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
} from '../../../shared/components';

@Component({
    selector: 'patient-form',
    templateUrl: './patient-case-form.component.html',
    imports: [
        CommonModule,
        FormsModule,
        InlineSVGModule,
        ReactiveFormsModule,
        ConceptSelectorComponent,
        DatePickerComponent,
        AutoCompleteModule,
        InputTextModule,
        StepperModule,
        ButtonModule,
        ToggleSwitch,
        Fluid,
    ]
})
export class PatientFormComponent extends AbstractFormBase {

  // Input signal for initial data passed to the form
  initialData = input<PatientCase>();

  // Service injections
  readonly #caseService = inject(PatientCasesService);
  readonly #fb = inject(FormBuilder);

  // Create and update service methods for the form data
  public readonly createService = (payload: PatientCaseCreate) => this.#caseService.createPatientCase({patientCaseCreate: payload});
  public readonly updateService = (id: string, payload: PatientCaseCreate) => this.#caseService.updatePatientCaseById({caseId: id, patientCaseCreate: payload});

  // Path to illustrations
  public readonly centerIllustration = 'assets/images/accessioning/hospital.svg';
  public readonly consentIllustration = 'assets/images/accessioning/consent.svg';

  // Define the form
  public form = this.#fb.group({
    identification: this.#fb.nonNullable.group({
      clinicalCenter: this.#fb.control<string | null>(null, Validators.required),
      clinicalIdentifier: this.#fb.control<string | null>(null, Validators.required),
    }),
    general: this.#fb.nonNullable.group({
      gender: this.#fb.control<CodedConcept | null>(null, Validators.required),
      dateOfBirth: this.#fb.control<string | null>(null, Validators.required),
      isAlive: this.#fb.control<boolean | null>(true, Validators.required),
      dateOfDeath: this.#fb.control<string | null>(null),
      causeOfDeath: this.#fb.control<CodedConcept | null>(null),
    }),
    consent: this.#fb.nonNullable.group({
      consentValid: this.#fb.control<boolean | null>(false, Validators.required),
    }),
  });

  readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;
  
    this.form.patchValue({
      identification: {
        clinicalCenter: data.clinicalCenter ?? null,
        clinicalIdentifier: data.clinicalIdentifier ?? null,
      },
      general: {
        gender: data.gender ?? null,
        dateOfBirth: data.dateOfBirth ?? null,
        isAlive: !data.isDeceased,
        dateOfDeath: data.dateOfDeath ?? null,
        causeOfDeath: data.causeOfDeath ?? null,
      },
      consent: {
        consentValid: false,
      },
    });
  });

  // API Payload construction function
  public payload = (): PatientCaseCreate => {
    const data = this.form.value;
    return {
      gender: data.general!.gender!,
      dateOfBirth: data.general!.dateOfBirth!,
      dateOfDeath: !data.general!.isAlive ? data.general!.dateOfDeath : null,
      causeOfDeath: !data.general!.isAlive ? data.general!.causeOfDeath: null,
      clinicalCenter: data.identification!.clinicalCenter!,
      clinicalIdentifier: data.identification!.clinicalIdentifier!,
      consentStatus: data.consent!.consentValid ? PatientCaseConsentStatusChoices.Valid : PatientCaseConsentStatusChoices.Unknown,
    };
  }
  // Get the default clinical center through the API
  public defaultClinicalCenter = rxResource({
    request: () => ({}),
    loader: ({request}) => this.#caseService.getDefaultClinicalCenter().pipe(map(center => {
      const ClinicalCenterControl = this.form.get('identification')?.get('clinicalCenter');
      if (ClinicalCenterControl) {
        ClinicalCenterControl.setValue(center);
        ClinicalCenterControl.updateValueAndValidity();
      }
    }))
  })
  // Dynamically react to changes to the clinical center input query and search for matching centers
  public clinicalCenterQuery = signal<string>('');
  public clinicalCenters = rxResource({
    request: () => ({clinicalCenterContains: this.clinicalCenterQuery()}),
    loader: ({request}) => this.#caseService.getPatientCases(request).pipe(map(response => [...new Set(response.items.map(item => item.clinicalCenter))]))
  })

  // Dynamically react to changes to the isAlive field
  public currentIsAlive = toSignal(this.form.controls['general']!.controls['isAlive']!.valueChanges, {initialValue: true})
  #vitalStatusChangesEffect = effect(() => {
    const dateOfDeathControl = this.form.get('general')!.get('dateOfDeath');
    const causeOfDeathControl = this.form.get('general')!.get('causeOfDeath');
    if (this.currentIsAlive()) {
      dateOfDeathControl?.removeValidators([Validators.required]);
      causeOfDeathControl?.removeValidators([Validators.required]);
    } else {
      dateOfDeathControl?.addValidators([Validators.required]);
      causeOfDeathControl?.addValidators([Validators.required]);
    }  
    dateOfDeathControl?.updateValueAndValidity();
    causeOfDeathControl?.updateValueAndValidity();
  })

}