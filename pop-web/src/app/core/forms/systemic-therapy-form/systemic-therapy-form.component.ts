import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { Form, FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule, FormArray } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { Tablets } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { Fieldset } from 'primeng/fieldset';

import { 
    CodedConceptSchema,
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    SystemicTherapyCreateSchema,
    SystemicTherapyMedicationSchema,
    SystemicTherapyMedicationCreateSchema,
    SystemicTherapiesService,
    SystemicTherapySchema,
    SystemicTherapyIntentChoices
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent ,
  ReferenceMultiSelect,
  RadioChoice,
  RadioSelectComponent,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'systemic-therapy-form',
  templateUrl: './systemic-therapy-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    Fieldset,
    CodedConceptSelectComponent,
    ReferenceMultiSelect,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class SystemicTherapyFormComponent extends AbstractFormBase implements OnInit {

    private readonly systemicTherapiesService: SystemicTherapiesService = inject(SystemicTherapiesService)
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = this.systemicTherapiesService.createSystemicTherapy.bind(this.systemicTherapiesService)
    public readonly updateService = this.systemicTherapiesService.updateSystemicTherapy.bind(this.systemicTherapiesService)
    override readonly subformsServices = [{
        payloads: this.constructMedicationPayloads.bind(this),
        deletedEntries: this.getDeletedMedications.bind(this),
        delete: this.systemicTherapiesService.deleteSystemicTherapyMedication.bind(this.systemicTherapiesService),
        create: this.systemicTherapiesService.createSystemicTherapyMedication.bind(this.systemicTherapiesService),
        update: this.systemicTherapiesService.updateSystemicTherapyMedication.bind(this.systemicTherapiesService),
}]
    
    public readonly title: string = 'Systemic Therapy'
    public readonly subtitle: string = 'Add new systemic therapy'
    public readonly icon = Tablets;

    private caseId!: string;
    public initialData: SystemicTherapySchema | any = {};
    public relatedEntities: NeoplasticEntity[] = []; 

    public readonly intentChoices: RadioChoice[] = [
        {name: 'Curative', value: SystemicTherapyIntentChoices.Curative},
        {name: 'Palliative', value: SystemicTherapyIntentChoices.Palliative},
    ]

    public medicationFormArray!: FormArray;

    private deletedMedications: string[] = [];

    ngOnInit() {
        // Fetch any primary neoplastic entities that could be related to a new entry 
        this.getRelatedEntities()
        // Construct the form 
        this.constructForm()
    }

    ngAfterViewInit() {
        this.form.get('drugs')?.valueChanges.subscribe((drugs: CodedConceptSchema[]) => {
            // Add subforms for new drugs
            drugs.forEach((drug: CodedConceptSchema) => {
                if (!this.medicationFormArray.value.map( (medication: SystemicTherapyMedicationSchema) => medication.drug ).includes(drug) ){
                    this.medicationFormArray.push(this.constructMedicationSubform({drug: drug} as SystemicTherapyMedicationSchema));    
                }
            });
            // Remove subforms for drugs that are no longer selected
            this.medicationFormArray.value.forEach((medication: SystemicTherapyMedicationSchema, index: number) => {
                if (!drugs.includes(medication.drug)) {
                    if (medication.id) {
                        console.log('DELETE MEDICATION', medication.id)
                        this.deletedMedications.push(medication.id);
                    }
                    this.medicationFormArray.removeAt(index);
                }
            })
        })
    }

    constructForm(): void {

        this.medicationFormArray = this.formBuilder.array((this.initialData?.medications || [])?.map(
            (initialMedication: SystemicTherapyMedicationSchema) => {
                return this.constructMedicationSubform(initialMedication)
            }
        ))
        console.log('this.initialData', this.initialData)
        this.form = this.formBuilder.group({
            period: [this.initialData?.period, Validators.required],
            targetedEntities: [this.initialData?.targetedEntitiesIds, Validators.required],
            cycles: [this.initialData?.cycles,Validators.required],
            intent: [this.initialData?.intent,Validators.required],
            role: [this.initialData?.role],
            terminationReason: [this.initialData?.terminationReason],
            drugs: [this.initialData?.medications?.map((med:any) => med.drug),Validators.required],
            medications: this.medicationFormArray,
        });
    }

    constructMedicationSubform(initalData: SystemicTherapyMedicationSchema) {
        return this.formBuilder.group({
            id: [initalData.id],
            drug: [initalData.drug, Validators.required],
            route: [initalData.route],
        })
    }

    meditcationSubforms(): any[] {
        const formarray: FormArray = this.form.get('medications') as FormArray;
        if (formarray){
            return formarray.controls;
        }
        return [];
    }

    constructAPIPayload(data: any): SystemicTherapyCreateSchema {    
        console.log('constructAPIPayload', data)
        return {
            caseId: this.caseId,
            targetedEntitiesIds: data.targetedEntities,
            period: {
            start: data.period.start? data.period.start: moment(data.period.split(' - ')[0], ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
            end: data.period.end? data.period.end: moment(data.period.split(' - ')[1], ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
            },
            cycles: data.cycles,
            intent: data.intent,
        };
    }

    private constructMedicationPayloads(data: any): SystemicTherapyMedicationCreateSchema {
        return data.medications.map((subformData: any) => {return {
            id: subformData.id,
            drug: subformData.drug,
            route: subformData.route,
        }})
    }

    private getDeletedMedications(): string[] {
        console.log('GET DELETED MEDS', this.deletedMedications)
        return this.deletedMedications;
    }

    private getRelatedEntities(): void {
        this.neoplasticEntitiesService.getNeoplasticEntities(this.caseId)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe(
            (response) => {
                this.relatedEntities = response.items
            }
        )
    }


}