import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PatientCaseCreate, PatientCasesService, PatientCase } from '../../modules/openapi'
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { ButtonModule } from 'primeng/button';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { Fluid } from 'primeng/fluid';

import * as moment from 'moment';

import { AbstractFormBase } from '../abstract-form-base.component';
import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent 
} from '../components';

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
    CodedConceptSelectComponent,
    MaskedCalendarComponent,
    ControlErrorComponent,
    ButtonModule,
    ToggleSwitch,
    Fluid,
  ]
})
export class PatientFormComponent extends AbstractFormBase implements OnInit {


  private readonly caseService = inject(PatientCasesService);
  public readonly formBuilder = inject(FormBuilder);

  public readonly createService = this.caseService.createPatientCase.bind(this.caseService);
  public readonly updateService = this.caseService.updatePatientCaseById.bind(this.caseService);
  public initialData: PatientCase | EmptyObject = {};

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
      dateOfDeath: (null),
      causeOfDeath: [null],
    });
  }

  constructAPIPayload(data: any): PatientCaseCreate {
    return {
      gender: data.gender,
      dateOfBirth: moment(data.dateOfBirth, ['MM/YYYY','YYYY-MM-DD']).format('YYYY-MM-DD'),
      dateOfDeath: !data.isAlive?  moment(data.dateOfDeath, ['MM/YYYY','YYYY-MM-DD']).format('YYYY-MM-DD'): null,
      causeOfDeath: !data.isAlive? data.causeOfDeath: null,
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