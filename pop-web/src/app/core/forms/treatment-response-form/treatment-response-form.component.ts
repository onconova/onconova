import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { HeartPulse } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';

import { 
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    TreatmentResponseCreateSchema,
    TreatmentResponsesService,
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent ,
  ReferenceMultiSelect,
  RadioSelectComponent,
  RadioChoice,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'treatment-response-form',
  templateUrl: './treatment-response-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    CodedConceptSelectComponent,
    ReferenceMultiSelect,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class TreatmentResponseFormComponent extends AbstractFormBase implements OnInit {

    private readonly treatmentResponsesService: TreatmentResponsesService = inject(TreatmentResponsesService)
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = this.treatmentResponsesService.createTreatmentResponse.bind(this.treatmentResponsesService)
    public readonly updateService = this.treatmentResponsesService.updateTreatmentResponse.bind(this.treatmentResponsesService)

    public readonly title: string = 'Risk Assessment'
    public readonly subtitle: string = 'Add new risk assessment'
    public readonly icon = HeartPulse;

    private caseId!: string;
    public initialData: TreatmentResponseCreateSchema | any = {};
    public relatedEntities$!: Observable<NeoplasticEntity[]>; 
    public resultsType: string[] = [];
    public readonly interpretationChoices: RadioChoice[] = [
        {name: 'Interpreted', value: true},
        {name: 'Reported', value: false},
    ]

    ngOnInit() {
        // Construct the form 
        this.constructForm();
        // Fetch any primary neoplastic entities that could be related to a new entry 
        this.relatedEntities$ = this.neoplasticEntitiesService.getNeoplasticEntities(this.caseId).pipe(map(response => response.items));
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            assessedEntities: [this.initialData?.assessedEntitiesIds, Validators.required],
            methodology: [this.initialData?.methodology,Validators.required],
            recist: [this.initialData?.recist,Validators.required],
            recistInterpreted: [this.initialData?.recistInterpreted],
            assessedBodysites: [this.initialData?.assessedBodysites],
        });
    }
    

    constructAPIPayload(data: any): TreatmentResponseCreateSchema {    
        return {
        caseId: this.caseId,
        assessedEntitiesIds: data.assessedEntities,
        date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
        recist: data.recist,
        recistInterpreted: data.recistInterpreted,
        assessedBodysites: data.assessedBodysites,
        methodology: data.methodology,
        };
    }


}