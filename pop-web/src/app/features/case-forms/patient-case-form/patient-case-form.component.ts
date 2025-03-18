import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PatientCaseCreate, PatientCasesService, PatientCaseConsentStatusChoices } from '../../../shared/openapi'
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

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


import { UserPlus } from 'lucide-angular';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  standalone: true,
  selector: 'patient-form',
  templateUrl: './patient-case-form.component.html',
  styles: `
    .illustration {
      color: var(--p-primary-color);
      display: flex;   
      height: 15rem;
    }
  `,
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
export class PatientFormComponent extends AbstractFormBase implements OnInit {


  private readonly caseService = inject(PatientCasesService);
  public readonly formBuilder = inject(FormBuilder);

  public readonly createService = (payload: PatientCaseCreate) => this.caseService.createPatientCase({patientCaseCreate: payload});
  public readonly updateService = (id: string, payload: PatientCaseCreate) => this.caseService.updatePatientCaseById({caseId: id, patientCaseCreate: payload});
  public initialData: any = {};

  public readonly centerIllustration = 'assets/images/accessioning/hospital.svg';
  public readonly consentIllustration = 'assets/images/accessioning/consent.svg';

  public readonly title: string = 'Accessioning'
  public readonly subtitle: string = 'Register a new patient case'
  public readonly icon = UserPlus;

  public centers: string[] = [];

  ngOnInit() {
    this.constructForm();
    this.onIsAliveChange();
  }

  private constructForm() {
    this.form = this.formBuilder.group({
      identification: this.formBuilder.group({
        clinicalCenter: [null,Validators.required],
        clinicalIdentifier: [null,Validators.required],
      },Validators.required),
      general: this.formBuilder.group({
        gender: [null,Validators.required],
        dateOfBirth: [null,Validators.required],
        isAlive: [true,Validators.required],
        dateOfDeath: (null),
        causeOfDeath: (null),
      },Validators.required),
      consent: this.formBuilder.group({
        consentValid: [null, Validators.required],
      },Validators.required)
    });
  }

  constructAPIPayload(data: any): PatientCaseCreate {
    return {
      gender: data.general.gender,
      dateOfBirth: data.general.dateOfBirth,
      dateOfDeath: !data.general.isAlive ? data.general.dateOfDeath : null,
      causeOfDeath: !data.general.isAlive ? data.general.causeOfDeath: null,
      clinicalCenter: data.identification.clinicalCenter,
      clinicalIdentifier: data.identification.clinicalIdentifier,
      consentStatus: data.consent.consentValid ? PatientCaseConsentStatusChoices.Valid : PatientCaseConsentStatusChoices.Unknown,
    };
  }

  private onIsAliveChange(): void {
    this.form.get('general')?.get('isAlive')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(isAlive => {
      const dateOfDeathControl = this.form.get('general')?.get('dateOfDeath');
      const causeOfDeathControl = this.form.get('general')?.get('causeOfDeath');
      const requiredValidator = [Validators.required];
  
      if (isAlive) {
        dateOfDeathControl?.removeValidators(requiredValidator);
        causeOfDeathControl?.removeValidators(requiredValidator);
      } else {
        dateOfDeathControl?.addValidators(requiredValidator);
        causeOfDeathControl?.addValidators(requiredValidator);
      }  
      dateOfDeathControl?.updateValueAndValidity();
      causeOfDeathControl?.updateValueAndValidity();
    });
  }

  searchCenter(event: {originalEvent: Event, query: string} ) {
    this.caseService.getPatientCases({clinicalCenterContains: event.query}).pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe({
      next: response => {
        this.centers = [...new Set(response.items.map(item => item.clinicalCenter))]
      }
    })
  }

}