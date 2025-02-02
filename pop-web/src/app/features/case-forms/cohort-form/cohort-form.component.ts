import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { ButtonModule } from 'primeng/button';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { Fluid } from 'primeng/fluid';
import { InputText } from 'primeng/inputtext';

import { CohortCreateSchema, CohortSchema, CohortsService } from '../../../shared/openapi'

import { AbstractFormBase } from '../abstract-form-base.component';
import { 
  FormControlErrorComponent 
} from '../../../shared/components';

import { Group } from 'lucide-angular';

@Component({
  standalone: true,
  selector: 'cohort-form',
  templateUrl: './cohort-form.component.html',
  imports: [
    CommonModule,
    FormsModule, 
    ReactiveFormsModule,
    FormControlErrorComponent,
    ButtonModule,
    ToggleSwitch,
    Fluid,
    InputText,
  ]
})
export class CohortFormComponent extends AbstractFormBase implements OnInit {


  private readonly cohortsService = inject(CohortsService);
  public readonly formBuilder = inject(FormBuilder);

  public readonly createService = (payload: CohortCreateSchema) => this.cohortsService.createCohort({cohortCreateSchema: payload});
  public readonly updateService = (id: string, payload: CohortCreateSchema) => this.cohortsService.updateCohort({cohortId: id, cohortCreateSchema: payload});
  public initialData: any = {};

  public readonly title: string = 'Cohort'
  public readonly subtitle: string = 'New cohort'
  public readonly icon = Group;

  ngOnInit() {
    this.constructForm();
  }

  private constructForm() {
    this.form = this.formBuilder.group({
      name: [null,Validators.required],
      isPublic: [false,Validators.required],
    });
  }

  constructAPIPayload(data: any): CohortCreateSchema {
    return {
      name: data.name,
      isPublic: data.isPublic,
    };
  }

}