import { Component, computed, effect, inject, input } from '@angular/core';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';

import { 
    NeoplasticEntitiesService, 
    TreatmentResponseCreate,
    TreatmentResponsesService,
    TreatmentResponse,
    CodedConcept,
} from 'pop-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
  RadioSelectComponent,
  RadioChoice,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { rxResource } from '@angular/core/rxjs-interop';

@Component({
    selector: 'treatment-response-form',
    templateUrl: './treatment-response-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        ButtonModule,
        ConceptSelectorComponent,
        MultiReferenceSelectComponent,
        RadioSelectComponent,
        FormControlErrorComponent,
    ]
})
export class TreatmentResponseFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<TreatmentResponse>();

    // Service injections
    readonly #treatmentResponsesService: TreatmentResponsesService = inject(TreatmentResponsesService);
    readonly #neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    readonly #fb = inject(FormBuilder);

    // Create and update service methods for the form data
    public readonly createService = (payload: TreatmentResponseCreate) => this.#treatmentResponsesService.createTreatmentResponse({treatmentResponseCreate: payload});
    public readonly updateService = (id: string, payload: TreatmentResponseCreate) => this.#treatmentResponsesService.updateTreatmentResponse({treatmentRresponseId: id, treatmentResponseCreate: payload});

    // Define the form
    public form = this.#fb.group({
        date: this.#fb.control<string | null>(null, Validators.required),
        assessedEntities: this.#fb.control<string[]>([], Validators.required),
        methodology: this.#fb.control<CodedConcept | null>(null, Validators.required),
        recist: this.#fb.control<CodedConcept | null>(null, Validators.required),
        recistInterpreted: this.#fb.control<boolean | null>(null),
        assessedBodysites: this.#fb.control<CodedConcept[] | null>(null),
    });

    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;
        this.form.patchValue({
            date: data.date ?? null,
            assessedEntities: data.assessedEntitiesIds ?? [],
            methodology: data.methodology ?? null,
            recist: data.recist ?? null,
            recistInterpreted: data.recistInterpreted ?? null,
            assessedBodysites: data.assessedBodysites ?? null,
        });
    });

    // API Payload construction function
    payload = (): TreatmentResponseCreate => {    
        const data = this.form.value;
        return {
            caseId: this.caseId(),
            assessedEntitiesIds: data.assessedEntities!,
            date: data.date!,
            recist: data.recist!,
            methodology: data.methodology!,
            recistInterpreted: data.recistInterpreted ?? undefined,
            assessedBodysites: data.assessedBodysites ?? undefined,
        };
    }
    
    // All neoplastic entities related to this patient case
    public relatedEntities = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
    }) 
    
    // Human readable choices for UI elements
    public readonly interpretationChoices: RadioChoice[] = [
        {name: 'Interpreted', value: true},
        {name: 'Reported', value: false},
    ]


}