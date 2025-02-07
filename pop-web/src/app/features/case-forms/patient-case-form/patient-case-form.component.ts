import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PatientCaseCreate, PatientCasesService, PatientCase } from '../../../shared/openapi'
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { ButtonModule } from 'primeng/button';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { Fluid } from 'primeng/fluid';

import { AbstractFormBase } from '../abstract-form-base.component';
import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent 
} from '../../../shared/components';

import { User } from 'lucide-angular';
import { EmptyObject } from 'chart.js/dist/types/basic';

@Component({
  standalone: true,
  selector: 'patient-form',
  templateUrl: './patient-case-form.component.html',
  imports: [
    CommonModule,
    FormsModule, 
    ReactiveFormsModule,
    ConceptSelectorComponent,
    DatePickerComponent,
    FormControlErrorComponent,
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

  public readonly title: string = 'Accessioning'
  public readonly subtitle: string = 'New patient'
  public readonly icon = User;

  ngOnInit() {
    this.constructForm();
    this.onIsAliveChange();
  }

  private constructForm() {
    this.form = this.formBuilder.group({
      gender: [null,Validators.required],
      dateOfBirth: [null,Validators.required],
      isAlive: [true,Validators.required],
      clinicalCenter: [null,Validators.required],
      clinicalIdentifier: [null,Validators.required],
      dateOfDeath: (null),
      consentStatus: [null,Validators.required],
    });
  }

  constructAPIPayload(data: any): PatientCaseCreate {
    return {
      gender: data.gender,
      dateOfBirth: data.dateOfBirth,
      dateOfDeath: !data.isAlive ? data.dateOfDeath : null,
      causeOfDeath: !data.isAlive ? data.causeOfDeath: null,
      clinicalCenter: data.clinicalCenter,
      clinicalIdentifier: data.clinicalIdentifier,
      consentStatus: data.consentStatus,
    };
  }

  private onIsAliveChange(): void {
    this.form.get('isAlive')?.valueChanges.subscribe(isAlive => {
      const dateOfDeathControl = this.form.get('dateOfDeath');
      const causeOfDeathControl = this.form.get('causeOfDeath');
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


}