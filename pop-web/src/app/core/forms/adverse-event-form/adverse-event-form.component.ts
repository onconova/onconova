import { Component, inject, OnInit, Pipe, PipeTransform} from '@angular/core';
import { FormBuilder, Validators, FormArray, FormControl } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { flatMap, forkJoin, map, mergeMap, Observable } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { ShieldAlert } from 'lucide-angular';

import { Fieldset } from 'primeng/fieldset';
import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputMaskModule } from 'primeng/inputmask';
import { RadioButton } from 'primeng/radiobutton';


import { 
    CodedConceptSchema,
    SystemicTherapiesService,
    SystemicTherapySchema,
    SystemicTherapyMedicationSchema,
    RadiotherapiesService,
    RadiotherapySchema,
    SurgeriesService,
    Surgery,
    AdverseEventOutcomeChoices,
    AdverseEventSuspectedCauseCausalityChoices,
    AdverseEventMitigationCategoryChoices,
    AdverseEventsService,
    AdverseEventSchema,
    AdverseEventCreateSchema,
    AdverseEventSuspectedCauseCreateSchema,
    AdverseEventSuspectedCauseSchema,
    AdverseEventMitigationSchema,
    AdverseEventMitigationCreateSchema,
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent,
  RadioChoice,
  ReferenceMultiSelect,
  RadioSelectComponent
} from '../../forms/components';
import { AbstractFormBase } from '../abstract-form-base.component';



@Pipe({
    standalone: true,
    name: 'getEventGrades'
  })
export class getEventGradesPipe implements PipeTransform {
  
    transform(concept: CodedConceptSchema) {
        const grades = Array.from({length: 5}, (_, i) => i+1);
        let gradeChoices = grades.map((grade: number) => {
            const properties = concept.properties as { [key: string]: any };
            return {
                grade: grade,
                description: properties[`grade${grade}`].trim(),                
            }
        })
        console.log(gradeChoices)
        return gradeChoices.filter((choice) => choice.description !== '-')
    }
}



@Component({
  standalone: true,
  selector: 'adverse-event-form',
  templateUrl: './adverse-event-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    SelectModule,
    MultiSelectModule,
    RadioButton,
    MaskedCalendarComponent,
    Fluid,
    Fieldset,
    ReferenceMultiSelect,
    InputNumber,
    InputMaskModule,
    ButtonModule,
    getEventGradesPipe,
    CodedConceptSelectComponent,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class AdverseEventFormComponent extends AbstractFormBase implements OnInit {

    private readonly systemicTherapiesService: SystemicTherapiesService = inject(SystemicTherapiesService);
    private readonly radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService);
    private readonly surgeriesService: SurgeriesService = inject(SurgeriesService);
    private readonly adverseEventsService: AdverseEventsService = inject(AdverseEventsService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: AdverseEventCreateSchema) => this.adverseEventsService.createAdverseEvent({adverseEventCreateSchema: payload});
    public readonly updateService = (id: string, payload: AdverseEventCreateSchema) => this.adverseEventsService.updateAdverseEvent({adverseEventId: id, adverseEventCreateSchema: payload});
    override readonly subformsServices = [
        {
            payloads: this.constructSuspectedCausePayloads.bind(this),
            deletedEntries: this.getdeletedSuspectedCauses.bind(this),
            delete: (parentId: string, id: string) => this.adverseEventsService.deleteAdverseEventSuspectedCause({adverseEventId: parentId, causeId: id}),
            create: (parentId: string, payload: AdverseEventSuspectedCauseCreateSchema) => this.adverseEventsService.createAdverseEventSuspectedCause({adverseEventId: parentId, adverseEventSuspectedCauseCreateSchema: payload}),
            update: (parentId: string, id: string, payload: AdverseEventSuspectedCauseCreateSchema) => this.adverseEventsService.updateAdverseEventSuspectedCause({adverseEventId: parentId, causeId: id, adverseEventSuspectedCauseCreateSchema: payload}),
        },
        {
            payloads: this.constructMitigationsPayloads.bind(this),
            deletedEntries: this.getdeletedMitigations.bind(this),
            delete: (parentId: string, id: string) => this.adverseEventsService.deleteAdverseEventMitigation({adverseEventId: parentId, mitigationId: id}),
            create: (parentId: string, payload: AdverseEventMitigationCreateSchema) => this.adverseEventsService.createAdverseEventMitigation({adverseEventId: parentId, adverseEventMitigationCreateSchema: payload}),
            update: (parentId: string, id: string, payload: AdverseEventMitigationCreateSchema) => this.adverseEventsService.updateAdverseEventMitigation({adverseEventId: parentId, mitigationId: id, adverseEventMitigationCreateSchema: payload}),
        },
    ]
    private deletedMitigations: string[] = [];
    private deletedSuspectedCauses: string[] = [];

    public readonly title: string = 'Adverse Event';
    public readonly subtitle: string = 'Add new adverse event';
    public readonly icon = ShieldAlert;

    private caseId!: string;
    public suspectedCausesFormArray!: FormArray;
    public mitigationsFormArray!: FormArray;
    public initialData: AdverseEventSchema | any = {};
    public relatedSuspectedCauses$!: Observable<(SystemicTherapySchema | SystemicTherapyMedicationSchema | RadiotherapySchema | Surgery)[]>;

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
        this.relatedSuspectedCauses$ = forkJoin([
            this.systemicTherapiesService.getSystemicTherapies({caseId:this.caseId}).pipe(map((response) => response.items)),
            this.systemicTherapiesService.getSystemicTherapies({caseId:this.caseId}).pipe(map((response) => response.items.flatMap(therapy => {
                return therapy.medications
        }))),
            this.radiotherapiesService.getRadiotherapies({caseId:this.caseId}).pipe(map((response) => response.items)),
            this.surgeriesService.getSurgeries({caseId:this.caseId}).pipe(map((response) => response.items)),
        ]).pipe(
            map(([systemicTherapies, medications, radiotherapies, surgeries]) => {
                return [...systemicTherapies, ...medications,...radiotherapies, ...surgeries];
            })
        )
    }

    constructForm(): void {

        this.suspectedCausesFormArray = this.formBuilder.array((this.initialData?.suspectedCauses || [])?.map(
            (initialSuspectedCause: AdverseEventSuspectedCauseSchema) => this.constructSuspectedCauseSubForm(initialSuspectedCause)
        ))
        this.mitigationsFormArray = this.formBuilder.array((this.initialData?.mitigations || [])?.map(
            (initialMitigation: AdverseEventMitigationSchema) => this.constructMitigationSubform(initialMitigation)
        ))

        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            event: [this.initialData?.event, Validators.required],
            grade: [this.initialData?.grade, Validators.required],
            outcome: [this.initialData?.outcome, Validators.required],
            dateResolved: [this.initialData?.dateResolved],
            suspectedCauses: this.suspectedCausesFormArray,
            mitigations: this.mitigationsFormArray,
        });
    }


    constructSuspectedCauseSubForm(initalData: AdverseEventSuspectedCauseSchema | null ) {
        return this.formBuilder.group({
            id: [initalData?.id],
            cause:[initalData?.medicationId || initalData?.radiotherapyId || initalData?.surgeryId || initalData?.systemicTherapyId, Validators.required],
            causality: [initalData?.causality],
        })
    }

    constructMitigationSubform(initalData: AdverseEventMitigationSchema | null ) {
        return this.formBuilder.group({
            id: [initalData?.id],
            category: [initalData?.category, Validators.required],
            adjustment: [initalData?.adjustment],
            drug: [initalData?.drug],
            procedure: [initalData?.procedure],
            management: [initalData?.management],
        })
    }

    constructAPIPayload(data: any): AdverseEventCreateSchema {    
        return {
            caseId: this.caseId,
            date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
            event: data.event,
            grade: data.grade,
            outcome: data.outcome,
            dateResolved: data.outcome === AdverseEventOutcomeChoices.Resolved || data.outcome === AdverseEventOutcomeChoices.ResolvedWithSequelae ?  moment(data.dateResolved, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD') : null,
        }
    }

    private constructSuspectedCausePayloads(data: any): AdverseEventSuspectedCauseCreateSchema {
        return data.suspectedCauses.map((subformData: any) => {return {
            id: subformData.id,
            causality: subformData.causality,            
            medicationId: subformData.cause.includes('Medication') ? subformData.cause : null,
            radiotherapyId: subformData.cause.includes('Radiotherapy') ? subformData.cause : null,
            surgeryId:  subformData.cause.includes('Surgery') ? subformData.cause : null,
            systemicTherapyId:  subformData.cause.includes('SystemicTherapy-') ? subformData.cause : null,
        }})
    }


    private constructMitigationsPayloads(data: any): AdverseEventMitigationCreateSchema {
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
        this.suspectedCausesFormArray.push(this.constructSuspectedCauseSubForm({} as AdverseEventSuspectedCauseSchema));
    }

    public addMitigation() {
        this.mitigationsFormArray.push(this.constructMitigationSubform({} as AdverseEventMitigationSchema));
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

    private getdeletedSuspectedCauses(): string[] {
        return this.deletedSuspectedCauses;
    }

    private getdeletedMitigations(): string[] {
        return this.deletedMitigations;
    }


}