import { Component, computed, effect, inject, input, Pipe, PipeTransform} from '@angular/core';
import { FormBuilder, Validators, FormArray, FormGroup } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { forkJoin, map } from 'rxjs';

import { Fieldset } from 'primeng/fieldset';
import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectModule } from 'primeng/select';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputMaskModule } from 'primeng/inputmask';
import { RadioButton } from 'primeng/radiobutton';


import { 
    CodedConcept,
    SystemicTherapiesService,
    RadiotherapiesService,
    SurgeriesService,
    AdverseEventOutcomeChoices,
    AdverseEventSuspectedCauseCausalityChoices,
    AdverseEventMitigationCategoryChoices,
    AdverseEventsService,
    AdverseEvent,
    AdverseEventCreate,
    AdverseEventSuspectedCauseCreate,
    AdverseEventSuspectedCause,
    AdverseEventMitigation,
    AdverseEventMitigationCreate,
    SystemicTherapy,
    SystemicTherapyMedication,
    Surgery,
    Radiotherapy,
} from 'pop-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent
} from '../../../shared/components';
import { AbstractFormBase } from '../abstract-form-base.component';
import { rxResource } from '@angular/core/rxjs-interop';

@Pipe({
    standalone: true,
    name: 'getEventGrades'
  })
export class getEventGradesPipe implements PipeTransform {
  
    transform(concept: CodedConcept | null) {
        if (!concept) return [];
        const grades = Array.from({length: 5}, (_, i) => i+1);
        let gradeChoices = grades.map((grade: number) => {
            const properties = concept.properties as { [key: string]: any };
            return {
                grade: grade,
                description: properties[`grade${grade}`].trim(),                
            }
        })
        return gradeChoices.filter((choice) => choice.description !== '-')
    }
}


@Component({
    selector: 'adverse-event-form',
    templateUrl: './adverse-event-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        SelectModule,
        MultiSelectModule,
        RadioButton,
        DatePickerComponent,
        Fluid,
        Fieldset,
        InputMaskModule,
        ButtonModule,
        getEventGradesPipe,
        ConceptSelectorComponent,
        RadioSelectComponent,
        FormControlErrorComponent,
    ]
})
export class AdverseEventFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    public initialData = input<AdverseEvent>();

    // Service injections
    readonly #systemicTherapiesService: SystemicTherapiesService = inject(SystemicTherapiesService);
    readonly #radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService);
    readonly #surgeriesService: SurgeriesService = inject(SurgeriesService);
    readonly #adverseEventsService: AdverseEventsService = inject(AdverseEventsService);
    readonly #fb = inject(FormBuilder);

    // Create and update service methods for the form data
    public readonly createService = (payload: AdverseEventCreate) => this.#adverseEventsService.createAdverseEvent({adverseEventCreate: payload});
    public readonly updateService = (id: string, payload: AdverseEventCreate) => this.#adverseEventsService.updateAdverseEvent({adverseEventId: id, adverseEventCreate: payload});

    // Services to create/update/delete related resources with data in subforms
    override subformsServices = [
        {
            payloads: this.suspectedCausesPayloads.bind(this),
            deletedEntries: this.getdeletedSuspectedCauses.bind(this),
            delete: (parentId: string, id: string) => this.#adverseEventsService.deleteAdverseEventSuspectedCause({adverseEventId: parentId, causeId: id}),
            create: (parentId: string, payload: AdverseEventSuspectedCauseCreate) => this.#adverseEventsService.createAdverseEventSuspectedCause({adverseEventId: parentId, adverseEventSuspectedCauseCreate: payload}),
            update: (parentId: string, id: string, payload: AdverseEventSuspectedCauseCreate) => this.#adverseEventsService.updateAdverseEventSuspectedCause({adverseEventId: parentId, causeId: id, adverseEventSuspectedCauseCreate: payload}),
        },
        {
            payloads: this.mitigationsPayloads.bind(this),
            deletedEntries: this.getdeletedMitigations.bind(this),
            delete: (parentId: string, id: string) => this.#adverseEventsService.deleteAdverseEventMitigation({adverseEventId: parentId, mitigationId: id}),
            create: (parentId: string, payload: AdverseEventMitigationCreate) => this.#adverseEventsService.createAdverseEventMitigation({adverseEventId: parentId, adverseEventMitigationCreate: payload}),
            update: (parentId: string, id: string, payload: AdverseEventMitigationCreate) => this.#adverseEventsService.updateAdverseEventMitigation({adverseEventId: parentId, mitigationId: id, adverseEventMitigationCreate: payload}),
        },
    ]
    #deletedMitigations: string[] = [];
    #deletedSuspectedCauses: string[] = [];

    // Define the main form
    public form = this.#fb.group({
        date: this.#fb.control<string | null>(null, Validators.required),
        event: this.#fb.control<CodedConcept | null>(null, Validators.required),
        grade: this.#fb.control<number | null>(null, Validators.required),
        outcome: this.#fb.control<AdverseEventOutcomeChoices | null>(null, Validators.required),
        dateResolved: this.#fb.control<string | null>(null),
        suspectedCauses: this.#fb.array<FormGroup>([]),
        mitigations: this.#fb.array<FormGroup>([]),
      });

    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;       
        this.form.patchValue({
            date: data.date ?? null,
            event: data.event || null,
            grade: data.grade ?? null,
            outcome: data.outcome ?? null,
            dateResolved: data.dateResolved ?? null,
        });
        (data.suspectedCauses || []).forEach((initialData: AdverseEventSuspectedCause) =>
            this.form.controls.suspectedCauses.push(this.#suspectedCauseForm(initialData))
        );
        (data.mitigations || []).forEach((initialData: AdverseEventMitigation) =>
            this.form.controls.mitigations.push(this.#mitigationForm(initialData))
        );
    });

    //Definition for the dynamic subform constructor
    #suspectedCauseForm = (initialData: AdverseEventSuspectedCause) => this.#fb.group({
        id: this.#fb.control<string | null>(
            initialData?.id
        ),
        cause: this.#fb.control<string | null>(
            initialData?.medicationId || 
            initialData?.radiotherapyId || 
            initialData?.surgeryId || 
            initialData?.systemicTherapyId ||
            null,
            Validators.required
        ),
        causality: this.#fb.control<AdverseEventSuspectedCauseCausalityChoices | null>(
            initialData?.causality ?? null,
        )
    })

    //Definition for the dynamic subform constructor
    #mitigationForm = (initialData: AdverseEventMitigation) => this.#fb.group({
        id: this.#fb.control<string | null>(
            initialData?.id,
        ),
        category: this.#fb.control<string | null>(
            initialData?.category, Validators.required,
        ),
        adjustment: this.#fb.control<CodedConcept | null>(
            initialData?.adjustment ?? null,
        ),
        drug: this.#fb.control<CodedConcept | null>(
            initialData?.drug ?? null,
        ),
        procedure: this.#fb.control<CodedConcept | null>(
            initialData?.procedure ?? null,
        ),
        management: this.#fb.control<CodedConcept | null>(
            initialData?.management ??  null,
        )
    })

    // API Payload construction function s
    readonly payload = (): AdverseEventCreate => {    
        const data = this.form.getRawValue();
        return {
            caseId: this.caseId(),
            date: data.date!,
            event: data.event!,
            grade: data.grade!,
            outcome: data.outcome as AdverseEventOutcomeChoices,
            dateResolved: (data.outcome === AdverseEventOutcomeChoices.Resolved || data.outcome === AdverseEventOutcomeChoices.ResolvedWithSequelae) ?  (data.dateResolved ?? undefined) : undefined,
        }
    }
    suspectedCausesPayloads (): AdverseEventSuspectedCauseCreate[] {
        const data = this.form.controls['suspectedCauses'].value;
        return data.map((subformData: any) => {return {
            id: subformData.id,
            causality: subformData.causality,            
            medicationId: this.#suspectedMedicationsIds().includes(subformData.cause) ? subformData.cause : null,
            radiotherapyId: this.#suspectedRadiotherapiesIds().includes(subformData.cause) ? subformData.cause : null,
            surgeryId: this.#suspectedSurgeriesIds().includes(subformData.cause) ? subformData.cause : null,
            systemicTherapyId: this.#suspectedSystemicTherapiesIds().includes(subformData.cause) ? subformData.cause : null,
        }})
    }
    mitigationsPayloads(): AdverseEventMitigationCreate[] {
        const data = this.form.controls['mitigations'].value;
        return data.map((subformData: any) => {return {
            id: subformData.id,
            category: subformData.category,
            adjustment: subformData.category === AdverseEventMitigationCategoryChoices.Adjustment ?  subformData.adjustment : null, 
            drug: subformData.category === AdverseEventMitigationCategoryChoices.Pharmacological ? subformData.drug : null, 
            procedure: subformData.category === AdverseEventMitigationCategoryChoices.Procedure ?  subformData.procedure : null, 
            management: subformData.management, 
        }})
    }
    
    // All potiential suspected causes of the adverse event
    public relatedSuspectedCauses = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => forkJoin([
            this.#systemicTherapiesService.getSystemicTherapies(request).pipe(map((response) => response.items)),
            this.#systemicTherapiesService.getSystemicTherapies(request).pipe(map((response) => response.items.flatMap(therapy => {
                return therapy.medications
        }))),
            this.#radiotherapiesService.getRadiotherapies(request).pipe(map((response) => response.items)),
            this.#surgeriesService.getSurgeries(request).pipe(map((response) => response.items)),
        ]).pipe(
            map(([systemicTherapies, medications, radiotherapies, surgeries]) => {
                return [...systemicTherapies, ...medications,...radiotherapies, ...surgeries];
            })
        )
    })

    public readonly AdverseEventOutcomeChoices = AdverseEventOutcomeChoices;
    public readonly outcomeChoices: RadioChoice[] = [
        {name: 'Resolved', value: AdverseEventOutcomeChoices.Resolved},
        {name: 'Resolved with sequelae', value: AdverseEventOutcomeChoices.ResolvedWithSequelae},
        {name: 'Ongoing', value: AdverseEventOutcomeChoices.Ongoing},
        {name: 'Recovering', value: AdverseEventOutcomeChoices.Recovering},
        {name: 'Fatal', value: AdverseEventOutcomeChoices.Fatal},
        {name: 'Unknown', value: AdverseEventOutcomeChoices.Unknown},
    ]

    public readonly AdverseEventSuspectedCauseCausalityChoices = AdverseEventSuspectedCauseCausalityChoices;
    public readonly causalityChoices: RadioChoice[] = [
        {name: 'Definitely related', value: AdverseEventSuspectedCauseCausalityChoices.DefinitelyRelated},
        {name: 'Probably related', value: AdverseEventSuspectedCauseCausalityChoices.ProbablyRelated},
        {name: 'Possibly related', value: AdverseEventSuspectedCauseCausalityChoices.PossiblyRelated},
        {name: 'Unrelated', value: AdverseEventSuspectedCauseCausalityChoices.Unrelated},
        {name: 'Unlikely related', value: AdverseEventSuspectedCauseCausalityChoices.UnlikelyRelated},
        {name: 'Conditionally related', value: AdverseEventSuspectedCauseCausalityChoices.ConditionallyRelated},
    ]

    public readonly AdverseEventMitigationCategoryChoices = AdverseEventMitigationCategoryChoices;
    public readonly mitigationCategoryChoices: RadioChoice[] = [
        {name: 'Adjustment of the systemic anti-neoplastic treatment', value: AdverseEventMitigationCategoryChoices.Adjustment},
        {name: 'Pharmacological treatment of the adverse event', value: AdverseEventMitigationCategoryChoices.Pharmacological},
        {name: 'Non-pharmacological treatment of the adverse event', value: AdverseEventMitigationCategoryChoices.Procedure},
    ]

    public addSuspectedCause() {
        const suspectedCauses: FormArray = this.form.controls['suspectedCauses']
        suspectedCauses.push(this.#suspectedCauseForm({} as AdverseEventSuspectedCause));
    }

    public addMitigation() {
        const mitigations: FormArray = this.form.controls['mitigations']
        mitigations.push(this.#mitigationForm({} as AdverseEventMitigation));
    }

    public removeSuspectedCause(index: number) {
        const suspectedCauses: FormArray = this.form.controls['suspectedCauses']
        const settingValue = suspectedCauses.value[index];
        if (settingValue?.id) {
            this.#deletedSuspectedCauses.push(settingValue.id);
        }
        suspectedCauses.removeAt(index);
    }

    public removeMitigation(index: number) {
        const mitigations: FormArray = this.form.controls['mitigations']
        const settingValue = mitigations.value[index];
        if (settingValue?.id) {
            this.#deletedMitigations.push(settingValue.id);
        }
        mitigations.removeAt(index);
    }

    getdeletedSuspectedCauses(): string[] {
        return this.#deletedSuspectedCauses;
    }

    getdeletedMitigations(): string[] {
        return this.#deletedMitigations;
    }


        #suspectedSystemicTherapiesIds = computed( () => this.relatedSuspectedCauses.value()!.filter((entry) => this.#isSystemicTherapy(entry))?.map((entry) => entry.id))
        #suspectedMedicationsIds = computed( () => this.relatedSuspectedCauses.value()!.filter((entry) => this.#isSystemicTherapyMedication(entry))?.map((entry) => entry.id))
        #suspectedSurgeriesIds = computed( () => this.relatedSuspectedCauses.value()!.filter((entry) => this.#isSurgery(entry))?.map((entry) => entry.id))
        #suspectedRadiotherapiesIds = computed( () => this.relatedSuspectedCauses.value()!.filter((entry) => this.#isRadiotherapy(entry))?.map((entry) => entry.id))
        #isSystemicTherapy(obj: any): obj is SystemicTherapy {
            return typeof obj === 'object' && obj !== null
              && obj.hasOwnProperty('medications') && obj.hasOwnProperty('period');
        }
        #isSystemicTherapyMedication(obj: any): obj is SystemicTherapyMedication {
            return typeof obj === 'object' && obj !== null
            && obj.hasOwnProperty('drug') && obj.hasOwnProperty('route');
        }
        #isSurgery(obj: any): obj is Surgery {
            return typeof obj === 'object' && obj !== null
            && obj.hasOwnProperty('date') && obj.hasOwnProperty('procedure');
        }
        #isRadiotherapy(obj: any): obj is Radiotherapy {
            return typeof obj === 'object' && obj !== null
            && obj.hasOwnProperty('dosages') && obj.hasOwnProperty('settings');
        }
    

}