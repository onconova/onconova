import { Component, computed, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { ButtonModule } from 'primeng/button';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { Fluid } from 'primeng/fluid';
import { InputText } from 'primeng/inputtext';

import { CohortCreate, Cohort, CohortsService, ProjectsService, GetProjectsRequestParams } from 'pop-api-client'

import { AbstractFormBase } from '../abstract-form-base.component';
import { 
  FormControlErrorComponent 
} from '../../../shared/components';
import { rxResource } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { Select } from 'primeng/select';
import { Message } from 'primeng/message';

@Component({
    selector: 'cohort-form',
    templateUrl: './cohort-form.component.html',
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        FormControlErrorComponent,
        Message,
        ButtonModule,
        Select,
        Fluid,
        InputText,
    ]
})
export class CohortFormComponent extends AbstractFormBase {

  // Input signal for initial data passed to the form
  initialData = input<Cohort>();

  // Service injections using Angular's `inject()` API
  readonly #cohortsService = inject(CohortsService);
  readonly #projectsService = inject(ProjectsService);
  readonly #authService = inject(AuthService);
  readonly #fb = inject(FormBuilder);

  #currentUser = computed(() => this.#authService.user());
  protected invalidUser = computed(() => this.relatedProjects.hasValue() && this.relatedProjects.value().length === 0)
  // Create and update service methods for the form data
  public readonly createService = (payload: CohortCreate) => this.#cohortsService.createCohort({cohortCreate: payload});
  public readonly updateService = (id: string, payload: CohortCreate) => this.#cohortsService.updateCohort({cohortId: id, cohortCreate: payload});

  public form =  computed(() => this.#fb.group({
    name: this.#fb.nonNullable.control<string>(
      this.initialData()?.name || '', Validators.required
    ),
    project: this.#fb.nonNullable.control<string>(
      this.initialData()?.projectId || '', Validators.required
    ),
  }));
  
  payload = (): CohortCreate => {
    const data = this.form().value;
    return {
      name: data.name!,
      projectId: data.project,
    }
  }

  protected relatedProjects = rxResource({
    request: () => ({membersUsername: this.#currentUser()?.username, status: 'ongoing'} as GetProjectsRequestParams),
    loader: ({request}) => this.#projectsService.getProjects(request).pipe(
      map(response => response.items)
    )
  })

}