import { Component, effect, inject, input, signal} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectModule } from 'primeng/select';
import { TextareaModule } from 'primeng/textarea';
import { environment } from 'src/environments/environment';
import { 
    PatientCasesService,
    Project,
    ProjectCreate,
    ProjectsService,
    ProjectStatusChoices,
    UsersService,
} from 'onconova-api-client'

import { 
  FormControlErrorComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { InputText } from 'primeng/inputtext';
import { rxResource } from '@angular/core/rxjs-interop';
import { AutoComplete } from 'primeng/autocomplete';
import { RadioChoice, RadioSelectComponent } from "../../../shared/components/radio-select/radio-select.component";
import { UserSelectorComponent } from 'src/app/shared/components/user-selector/user-selector.component';


@Component({
    selector: 'project-form',
    templateUrl: './projects-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        SelectModule,
        Fluid,
        ButtonModule,
        TextareaModule,
        AutoComplete,
        InputText,
        FormControlErrorComponent,
        RadioSelectComponent,
        UserSelectorComponent,
    ]
})
export class ProjectFormComponent extends AbstractFormBase{

    // Input signal for initial data passed to the form
    initialData = input<Project>();

    // Service injections
    readonly #projectsService = inject(ProjectsService);
    readonly #usersService = inject(UsersService);
    readonly #caseService = inject(PatientCasesService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: ProjectCreate) => this.#projectsService.createProject({projectCreate: payload});
    public readonly updateService = (id: string, payload: ProjectCreate) => this.#projectsService.updateProjectById({projectId: id, projectCreate: payload});

    // Define the form
    public form = this.#fb.group({
        title: this.#fb.nonNullable.control<string>('', Validators.required),
        summary: this.#fb.nonNullable.control<string>('', Validators.required),
        status: this.#fb.nonNullable.control<ProjectStatusChoices>(ProjectStatusChoices.Planned, Validators.required),
        clinicalCenters: this.#fb.nonNullable.control<string[]>([environment.organizationName], Validators.required),
        leader: this.#fb.nonNullable.control<string>('', Validators.required),
        members: this.#fb.control<string[] | null>(null, Validators.required),
        ethicsApprovalNumber: this.#fb.nonNullable.control<string>('', Validators.required),
    })
    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;
        this.form.patchValue({
            title: data.title ?? '',
            summary: data.summary ?? '',
            clinicalCenters: data.clinicalCenters ?? [environment.organizationName],
            leader: data.leader ?? '',
            status: data.status ?? ProjectStatusChoices.Planned,
            members: data.members?.filter(user => user !== data.leader) ?? null,
            ethicsApprovalNumber: data.ethicsApprovalNumber ?? '',
        });
    });
        
    // API Payload construction function
    payload = (): ProjectCreate => {    
        const data = this.form.value;
        return {
            title: data.title!,
            summary: data.summary!,
            clinicalCenters: data.clinicalCenters!,
            leader: data.leader!,
            status: data.status!,
            members: [data.leader!, ...(data.members || [])],
            ethicsApprovalNumber: data.ethicsApprovalNumber!,
        };
    }

    // Dynamically react to changes to the clinical center input query and search for matching centers
    public clinicalCenterQuery = signal<string>('');
    public clinicalCenters = rxResource({
        request: () => ({query: this.clinicalCenterQuery()}),
        loader: ({request}) => this.#caseService.getClinicalCenters(request)
    })

    public statusChoices: RadioChoice[] = [
        {name: 'Planned', value: ProjectStatusChoices.Planned},
        {name: 'Ongoing', value: ProjectStatusChoices.Ongoing},
        {name: 'Completed', value: ProjectStatusChoices.Completed},
        {name: 'Aborted', value: ProjectStatusChoices.Aborted},
    ]
}