import { Component, computed, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { ButtonModule } from 'primeng/button';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { Fluid } from 'primeng/fluid';
import { InputText } from 'primeng/inputtext';

import { CohortCreate, Cohort, CohortsService } from '../../../shared/openapi'

import { AbstractFormBase } from '../abstract-form-base.component';
import { 
  FormControlErrorComponent 
} from '../../../shared/components';

@Component({
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
export class CohortFormComponent extends AbstractFormBase {

  // Input signal for initial data passed to the form
  initialData = input<Cohort>();

  // Service injections using Angular's `inject()` API
  readonly #cohortsService = inject(CohortsService);
  readonly #fb = inject(FormBuilder);

  // Create and update service methods for the form data
  public readonly createService = (payload: CohortCreate) => this.#cohortsService.createCohort({cohortCreate: payload});
  public readonly updateService = (id: string, payload: CohortCreate) => this.#cohortsService.updateCohort({cohortId: id, cohortCreate: payload});

  public form =  computed(() => this.#fb.group({
    name: this.#fb.nonNullable.control<string>(
      this.initialData()?.name || '', Validators.required
    ),
    isPublic: this.#fb.nonNullable.control<boolean>(
      this.initialData()?.isPublic || false, Validators.required
    ),
  }));
  
  payload = (): CohortCreate => {
    const data = this.form().getRawValue();
    return {
      name: data.name,
      isPublic: data.isPublic,
    }
  }

}