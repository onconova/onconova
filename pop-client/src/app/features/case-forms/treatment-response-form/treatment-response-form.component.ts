import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';

import { HeartPulse } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';

import { 
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    TreatmentResponseCreate,
    TreatmentResponsesService,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
  RadioSelectComponent,
  RadioChoice,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
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
  ],
})
export class TreatmentResponseFormComponent extends AbstractFormBase implements OnInit {

    private readonly treatmentResponsesService: TreatmentResponsesService = inject(TreatmentResponsesService)
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = (payload: TreatmentResponseCreate) => this.treatmentResponsesService.createTreatmentResponse({treatmentResponseCreate: payload});
    public readonly updateService = (id: string, payload: TreatmentResponseCreate) => this.treatmentResponsesService.updateTreatmentResponse({treatmentRresponseId: id, treatmentResponseCreate: payload});

    public readonly title: string = 'Risk Assessment'
    public readonly subtitle: string = 'Add new risk assessment'
    public readonly icon = HeartPulse;

    private caseId!: string;
    public initialData: TreatmentResponseCreate | any = {};
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
        this.relatedEntities$ = this.neoplasticEntitiesService.getNeoplasticEntities({caseId:this.caseId}).pipe(map(response => response.items));
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
    

    constructAPIPayload(data: any): TreatmentResponseCreate {    
        return {
        caseId: this.caseId,
        assessedEntitiesIds: data.assessedEntities,
        date: data.date,
        recist: data.recist,
        recistInterpreted: data.recistInterpreted,
        assessedBodysites: data.assessedBodysites,
        methodology: data.methodology,
        };
    }


}