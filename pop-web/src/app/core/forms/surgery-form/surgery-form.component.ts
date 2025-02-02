import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { Slice } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    SurgeryCreate,
    SurgeriesService,
    SurgeryIntentChoices
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  DatePickerComponent,
  ControlErrorComponent,
  RadioChoice,
  RadioSelectComponent,
  ReferenceMultiSelect,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'surgery-form',
  templateUrl: './surgery-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    SelectModule,
    DatePickerComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    ReferenceMultiSelect,
    CodedConceptSelectComponent,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class SurgeryFormComponent extends AbstractFormBase implements OnInit {

    private readonly surgeriesService: SurgeriesService = inject(SurgeriesService);
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: SurgeryCreate) => this.surgeriesService.createSurgery({surgeryCreate: payload});
    public readonly updateService = (id: string, payload: SurgeryCreate) => this.surgeriesService.updateSurgeryById({surgeryId: id, surgeryCreate: payload});

    public readonly title: string = 'Surgery';
    public readonly subtitle: string = 'Add new surgery';
    public readonly icon = Slice;

    private caseId!: string;
    public initialData: SurgeryCreate | any = {};
    public relatedEntities: NeoplasticEntity[] = []; 

    public readonly intentChoices: RadioChoice[] = [
        {name: 'Curative', value: SurgeryIntentChoices.Curative},
        {name: 'Palliative', value: SurgeryIntentChoices.Palliative},
    ]

    ngOnInit() {
        // Fetch any neoplastic entities that could be related to a new entry 
        this.getRelatedEntities();
        // Construct the form 
        this.constructForm();
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            targetedEntities: [this.initialData?.targetedEntitiesIds, Validators.required],
            procedure: [this.initialData?.procedure,Validators.required],
            intent: [this.initialData?.intent,Validators.required],
            bodysite: [this.initialData?.bodysite],
            bodysiteQualifier: [this.initialData?.bodysiteQualifier], 
            bodysiteLaterality: [this.initialData?.bodysiteLaterality],
            outcome: [this.initialData?.outcome],           
        });
    }


    constructAPIPayload(data: any): SurgeryCreate {    
        return {
            caseId: this.caseId,
            date: data.date,
            targetedEntitiesIds: data.targetedEntities,
            procedure: data.procedure,
            intent: data.intent,
            bodysite: data.bodysite,
            bodysiteQualifier: data.bodysiteQualifier,
            bodysiteLaterality: data.bodysiteLaterality,
            outcome: data.outcome,
        };
    }

    private getRelatedEntities(): void {
        this.neoplasticEntitiesService.getNeoplasticEntities({caseId:this.caseId})
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe(
            (response) => {
                this.relatedEntities = response.items
            }
        )
    }
}