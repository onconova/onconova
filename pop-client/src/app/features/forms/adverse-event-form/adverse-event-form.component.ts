import { Component, inject, input, OnInit, Pipe, PipeTransform} from '@angular/core';
import { FormBuilder, Validators, FormArray, FormControl } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { forkJoin, map, Observable } from 'rxjs';

import { ShieldAlert } from 'lucide-angular';

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
    SystemicTherapy,
    SystemicTherapyMedication,
    RadiotherapiesService,
    Radiotherapy,
    SurgeriesService,
    Surgery,
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
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent
} from '../../../shared/components';
import { AbstractFormBase } from '../abstract-form-base.component';
import { ModalFormHeaderComponent } from '../modal-form-header.component';
import { rxResource } from '@angular/core/rxjs-interop';



@Pipe({
    standalone: true,
    name: 'getEventGrades'
  })
export class getEventGradesPipe implements PipeTransform {
  
    transform(concept: CodedConcept) {
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
export class AdverseEventFormComponent extends AbstractFormBase implements OnInit {

    public initialData = input<AdverseEvent>();

    readonly #systemicTherapiesService: SystemicTherapiesService = inject(SystemicTherapiesService);
    readonly #radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService);
    readonly #surgeriesService: SurgeriesService = inject(SurgeriesService);
    readonly #adverseEventsService: AdverseEventsService = inject(AdverseEventsService);
    readonly #formBuilder = inject(FormBuilder);

    public readonly createService = (payload: AdverseEventCreate) => this.#adverseEventsService.createAdverseEvent({adverseEventCreate: payload});
    public readonly updateService = (id: string, payload: AdverseEventCreate) => this.#adverseEventsService.updateAdverseEvent({adverseEventId: id, adverseEventCreate: payload});

    override subformsServices = [
        {
            payloads: this.constructSuspectedCausePayloads.bind(this),
            deletedEntries: this.getdeletedSuspectedCauses.bind(this),
            delete: (parentId: string, id: string) => this.#adverseEventsService.deleteAdverseEventSuspectedCause({adverseEventId: parentId, causeId: id}),
            create: (parentId: string, payload: AdverseEventSuspectedCauseCreate) => this.#adverseEventsService.createAdverseEventSuspectedCause({adverseEventId: parentId, adverseEventSuspectedCauseCreate: payload}),
            update: (parentId: string, id: string, payload: AdverseEventSuspectedCauseCreate) => this.#adverseEventsService.updateAdverseEventSuspectedCause({adverseEventId: parentId, causeId: id, adverseEventSuspectedCauseCreate: payload}),
        },
        {
            payloads: this.constructMitigationsPayloads.bind(this),
            deletedEntries: this.getdeletedMitigations.bind(this),
            delete: (parentId: string, id: string) => this.#adverseEventsService.deleteAdverseEventMitigation({adverseEventId: parentId, mitigationId: id}),
            create: (parentId: string, payload: AdverseEventMitigationCreate) => this.#adverseEventsService.createAdverseEventMitigation({adverseEventId: parentId, adverseEventMitigationCreate: payload}),
            update: (parentId: string, id: string, payload: AdverseEventMitigationCreate) => this.#adverseEventsService.updateAdverseEventMitigation({adverseEventId: parentId, mitigationId: id, adverseEventMitigationCreate: payload}),
        },
    ]
    public mitigationsFormArray!: FormArray;
    private deletedMitigations: string[] = [];
    public suspectedCausesFormArray!: FormArray;
    private deletedSuspectedCauses: string[] = [];
    

    public relatedSuspectedCauses = rxResource({
        request: () => ({caseId: this.caseId(), limit: 100}),
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

    ngOnInit() {
        // Construct the form 
        this.constructForm()
    }

    constructForm(): void {

        this.suspectedCausesFormArray = this.#formBuilder.array((this.initialData()?.suspectedCauses || [])?.map(
            (initialSuspectedCause: AdverseEventSuspectedCause) => this.constructSuspectedCauseSubForm(initialSuspectedCause)
        ))
        this.mitigationsFormArray = this.#formBuilder.array((this.initialData()?.mitigations || [])?.map(
            (initialMitigation: AdverseEventMitigation) => this.constructMitigationSubform(initialMitigation)
        ))

        this.form = this.#formBuilder.group({
            date: [this.initialData()?.date, Validators.required],
            event: [this.initialData()?.event, Validators.required],
            grade: [this.initialData()?.grade, Validators.required],
            outcome: [this.initialData()?.outcome, Validators.required],
            dateResolved: [this.initialData()?.dateResolved],
            suspectedCauses: this.suspectedCausesFormArray,
            mitigations: this.mitigationsFormArray,
        });
    }


    constructSuspectedCauseSubForm(initalData: AdverseEventSuspectedCause | null ) {
        return this.#formBuilder.group({
            id: [initalData?.id],
            cause:[initalData?.medicationId || initalData?.radiotherapyId || initalData?.surgeryId || initalData?.systemicTherapyId, Validators.required],
            causality: [initalData?.causality],
        })
    }

    constructMitigationSubform(initalData: AdverseEventMitigation | null ) {
        return this.#formBuilder.group({
            id: [initalData?.id],
            category: [initalData?.category, Validators.required],
            adjustment: [initalData?.adjustment],
            drug: [initalData?.drug],
            procedure: [initalData?.procedure],
            management: [initalData?.management],
        })
    }

    constructAPIPayload(data: any): AdverseEventCreate {    
        return {
            caseId: this.caseId(),
            date: data.date,
            event: data.event,
            grade: data.grade,
            outcome: data.outcome,
            dateResolved: data.outcome === AdverseEventOutcomeChoices.Resolved || data.outcome === AdverseEventOutcomeChoices.ResolvedWithSequelae ?  data.dateResolved : null,
        }
    }

    constructSuspectedCausePayloads(data: any): AdverseEventSuspectedCauseCreate[] {
        return data.suspectedCauses.map((subformData: any) => {return {
            id: subformData.id,
            causality: subformData.causality,            
            medicationId: subformData.cause.includes('Medication') ? subformData.cause : null,
            radiotherapyId: subformData.cause.includes('Radiotherapy') ? subformData.cause : null,
            surgeryId:  subformData.cause.includes('Surgery') ? subformData.cause : null,
            systemicTherapyId:  subformData.cause.includes('SystemicTherapy-') ? subformData.cause : null,
        }})
    }


    constructMitigationsPayloads(data: any): AdverseEventMitigationCreate[] {
        return data.mitigations.map((subformData: any) => {return {
            id: subformData.id,
            category: subformData.category,
            adjustment: subformData.category === AdverseEventMitigationCategoryChoices.Adjustment ?  subformData.adjustment : null, 
            drug: subformData.category === AdverseEventMitigationCategoryChoices.Pharmacological ? subformData.drug : null, 
            procedure: subformData.category === AdverseEventMitigationCategoryChoices.Procedure ?  subformData.procedure : null, 
            management: subformData.management, 
        }})
    }

    public addSuspectedCause() {
        this.suspectedCausesFormArray.push(this.constructSuspectedCauseSubForm({} as AdverseEventSuspectedCause));
    }

    public addMitigation() {
        this.mitigationsFormArray.push(this.constructMitigationSubform({} as AdverseEventMitigation));
    }

    public removeSuspectedCause(index: number) {
        const settingValue = this.suspectedCausesFormArray.value[index];
        if (settingValue?.id) {
            this.deletedSuspectedCauses.push(settingValue.id);
        }
        this.suspectedCausesFormArray.removeAt(index);
    }

    public removeMitigation(index: number) {
        const settingValue = this.mitigationsFormArray.value[index];
        if (settingValue?.id) {
            this.deletedMitigations.push(settingValue.id);
        }
        this.mitigationsFormArray.removeAt(index);
    }

    getdeletedSuspectedCauses(): string[] {
        return this.deletedSuspectedCauses;
    }

    getdeletedMitigations(): string[] {
        return this.deletedMitigations;
    }


}