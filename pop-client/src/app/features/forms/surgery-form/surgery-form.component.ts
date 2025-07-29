import { Component, computed, effect, inject, input} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { rxResource } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectModule } from 'primeng/select';

import { 
    NeoplasticEntitiesService, 
    SurgeryCreate,
    SurgeriesService,
    SurgeryIntentChoices,
    Surgery,
    CodedConcept
} from 'pop-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent,
  MultiReferenceSelectComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { map } from 'rxjs';
import { SelectButton } from 'primeng/selectbutton';

@Component({
    selector: 'surgery-form',
    templateUrl: './surgery-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        SelectModule,
        SelectButton,
        DatePickerComponent,
        Fluid,
        ButtonModule,
        MultiReferenceSelectComponent,
        ConceptSelectorComponent,
        FormControlErrorComponent,
    ]
})
export class SurgeryFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<Surgery>();

    // Service injections
    readonly #surgeriesService: SurgeriesService = inject(SurgeriesService);
    readonly #neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: SurgeryCreate) => this.#surgeriesService.createSurgery({surgeryCreate: payload});
    public readonly updateService = (id: string, payload: SurgeryCreate) => this.#surgeriesService.updateSurgeryById({surgeryId: id, surgeryCreate: payload});

    // Define the form
    public form = this.#fb.group({
        date: this.#fb.control<string | null>(null, Validators.required),
        targetedEntities: this.#fb.control<string[]>([], Validators.required),
        procedure: this.#fb.control<CodedConcept | null>(null, Validators.required),
        intent: this.#fb.control<SurgeryIntentChoices | null>(null, Validators.required),
        bodysite: this.#fb.control<CodedConcept | null>(null),
        bodysiteQualifier: this.#fb.control<CodedConcept | null>(null),
        bodysiteLaterality: this.#fb.control<CodedConcept | null>(null),
        outcome: this.#fb.control<CodedConcept | null>(null),
      });

    readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;
    
    this.form.patchValue({
        date: data.date ?? null,
        targetedEntities: data.targetedEntitiesIds ?? [],
        procedure: data.procedure ?? null,
        intent: data.intent ?? null,
        bodysite: data.bodysite ?? null,
        bodysiteQualifier: data.bodysiteQualifier ?? null,
        bodysiteLaterality: data.bodysiteLaterality ?? null,
        outcome: data.outcome ?? null,
    });
    });
    // API Payload construction function
    payload = (): SurgeryCreate => {    
        const data = this.form.value;
        return {
            caseId: this.caseId(),
            date: data.date!,
            targetedEntitiesIds: data.targetedEntities!,
            procedure: data.procedure!,
            intent: data.intent!,
            bodysite: data.bodysite ?? undefined,
            bodysiteQualifier: data.bodysiteQualifier ?? undefined,
            bodysiteLaterality: data.bodysiteLaterality ?? undefined,
            outcome: data.outcome ?? undefined,
        };
    }

    // All neoplastic entities related to this patient case
    public relatedEntities = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
    }) 

    // Human readable choices for UI elements
    public readonly intentChoices = [
        {label: 'Curative', value: SurgeryIntentChoices.Curative},
        {label: 'Palliative', value: SurgeryIntentChoices.Palliative},
    ]
}