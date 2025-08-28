import { Component, computed, effect, inject, input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PatientCaseCreate, PatientCasesService, PatientCaseConsentStatusChoices, PatientCase, CodedConcept, PatientCaseVitalStatusChoices } from 'onconova-api-client'
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
import { environment } from 'src/environments/environment';

import { AbstractFormBase } from '../abstract-form-base.component';
import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
} from '../../../shared/components';
import { SelectButton } from "primeng/selectbutton";

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
    SelectButton
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
      clinicalCenter: this.#fb.control<string | null>(environment.organizationName, Validators.required),
      clinicalIdentifier: this.#fb.control<string | null>(null, Validators.required),
    }),
    general: this.#fb.nonNullable.group({
      gender: this.#fb.control<CodedConcept | null>(null, Validators.required),
      dateOfBirth: this.#fb.control<string | null>(null, Validators.required),
      vitalStatus: this.#fb.control<PatientCaseVitalStatusChoices | null>(PatientCaseVitalStatusChoices.Alive, Validators.required),
      dateOfDeath: this.#fb.control<string | null>(null),
      causeOfDeath: this.#fb.control<CodedConcept | null>(null),
      endOfRecords: this.#fb.control<string | null>(null),
    }),
    consent: this.#fb.nonNullable.group({
      consentCheck: this.#fb.control<boolean | null>(false, Validators.required),
      consentStatus: this.#fb.control<PatientCaseConsentStatusChoices | null>(null, Validators.required),
    }),
  });

  readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;
    this.form.patchValue({
      identification: {
        clinicalCenter: data.clinicalCenter ?? environment.organizationName,
        clinicalIdentifier: data.clinicalIdentifier ?? null,
      },
      general: {
        gender: data.gender ?? null,
        dateOfBirth: typeof data.dateOfBirth === 'string' ? data.dateOfBirth as string : data.dateOfBirth as string  ?? null,
        vitalStatus: data.vitalStatus,
        dateOfDeath: data.dateOfDeath ?? null,
        causeOfDeath: data.causeOfDeath ?? null,
        endOfRecords: data.endOfRecords ?? null,
      },
      consent: {
        consentCheck: false,
        consentStatus: data.consentStatus,
      },
    });
  });

  // API Payload construction function
  public payload = (): PatientCaseCreate => {
    const data = this.form.value;
    return {
      gender: data.general!.gender!,
      dateOfBirth: data.general!.dateOfBirth! as string,
      endOfRecords: data.general!.vitalStatus == PatientCaseVitalStatusChoices.Unknown ? data.general!.endOfRecords! : undefined,
      dateOfDeath: data.general!.vitalStatus == PatientCaseVitalStatusChoices.Deceased ? data.general!.dateOfDeath! : undefined,
      causeOfDeath: data.general!.vitalStatus == PatientCaseVitalStatusChoices.Deceased ? data.general!.causeOfDeath!: undefined,
      clinicalCenter: data.identification!.clinicalCenter!,
      clinicalIdentifier: data.identification!.clinicalIdentifier!,
      consentStatus: data.consent!.consentStatus!,
    };
  }
  // Dynamically react to changes to the clinical center input query and search for matching centers
  public clinicalCenterQuery = signal<string>('');
  public clinicalCenters = rxResource({
    request: () => ({query: this.clinicalCenterQuery()}),
    loader: ({request}) => this.#caseService.getClinicalCenters(request)
  })

  // Dynamically react to changes to the isAlive field
  public currentVitalStatus = toSignal(this.form.controls['general']!.controls['vitalStatus']!.valueChanges)
  #vitalStatusChangesEffect = effect(() => {
    const dateOfDeathControl = this.form.get('general')!.get('dateOfDeath');
    const causeOfDeathControl = this.form.get('general')!.get('causeOfDeath');
    const endOfRecordsControl = this.form.get('general')!.get('endOfRecords');
    if (this.currentVitalStatus() == PatientCaseVitalStatusChoices.Alive) {
      dateOfDeathControl?.removeValidators([Validators.required]);
      causeOfDeathControl?.removeValidators([Validators.required]);
      endOfRecordsControl?.removeValidators([Validators.required]);
    } else if (this.currentVitalStatus() == PatientCaseVitalStatusChoices.Deceased) {
      dateOfDeathControl?.addValidators([Validators.required]);
      causeOfDeathControl?.addValidators([Validators.required]);
      endOfRecordsControl?.removeValidators([Validators.required]);
    } else if (this.currentVitalStatus() == PatientCaseVitalStatusChoices.Unknown) {
      dateOfDeathControl?.removeValidators([Validators.required]);
      causeOfDeathControl?.removeValidators([Validators.required]);
      endOfRecordsControl?.addValidators([Validators.required]);
    }
    dateOfDeathControl?.updateValueAndValidity();
    causeOfDeathControl?.updateValueAndValidity();
    endOfRecordsControl?.updateValueAndValidity();
  })

  protected readonly consentStatusOptions = [
    {label: 'Valid', value: PatientCaseConsentStatusChoices.Valid},
    {label: 'Revoked', value: PatientCaseConsentStatusChoices.Revoked},
    {label: 'Unknown', value: PatientCaseConsentStatusChoices.Unknown},
  ]
  protected readonly vitalStatusOptions = [
    {label: 'Alive', value: PatientCaseVitalStatusChoices.Alive},
    {label: 'Deceased', value: PatientCaseVitalStatusChoices.Deceased},
    {label: 'Unknown', value: PatientCaseVitalStatusChoices.Unknown},
  ]
}