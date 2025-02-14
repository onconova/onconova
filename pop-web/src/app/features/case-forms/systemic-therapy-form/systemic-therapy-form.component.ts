import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { Form, FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule, FormArray } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { Tablets } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { Fieldset } from 'primeng/fieldset';

import { 
    CodedConcept,
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    SystemicTherapyCreate,
    SystemicTherapyMedication,
    SystemicTherapyMedicationCreate,
    SystemicTherapiesService,
    SystemicTherapy,
    SystemicTherapyIntentChoices
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
  RadioChoice,
  RadioSelectComponent,
  MeasureInputComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'systemic-therapy-form',
  templateUrl: './systemic-therapy-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    DatePickerComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    Fieldset,
    MeasureInputComponent,
    ConceptSelectorComponent,
    MultiReferenceSelectComponent,
    RadioSelectComponent,
    FormControlErrorComponent,
  ],
})
export class SystemicTherapyFormComponent extends AbstractFormBase implements OnInit {

    private readonly systemicTherapiesService: SystemicTherapiesService = inject(SystemicTherapiesService)
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = (payload: SystemicTherapyCreate) => this.systemicTherapiesService.createSystemicTherapy({systemicTherapyCreate: payload});
    public readonly updateService = (id: string, payload: SystemicTherapyCreate) => this.systemicTherapiesService.updateSystemicTherapy({systemicTherapyId: id, systemicTherapyCreate: payload})
    override readonly subformsServices = [{
        payloads: this.constructMedicationPayloads.bind(this),
        deletedEntries: this.getDeletedMedications.bind(this),
        delete: (parentId: string, id: string) => this.systemicTherapiesService.deleteSystemicTherapyMedication({systemicTherapyId: parentId, medicationId: id}),
        create: (parentId: string, payload: SystemicTherapyMedicationCreate) => this.systemicTherapiesService.createSystemicTherapyMedication({systemicTherapyId: parentId, systemicTherapyMedicationCreate: payload}),
        update: (parentId: string, id: string, payload: SystemicTherapyMedicationCreate) => this.systemicTherapiesService.updateSystemicTherapyMedication({systemicTherapyId: parentId, medicationId: id, systemicTherapyMedicationCreate: payload}),
    }]

    public readonly title: string = 'Systemic Therapy'
    public readonly subtitle: string = 'Add new systemic therapy'
    public readonly icon = Tablets;

    private caseId!: string;
    public medicationFormArray!: FormArray;
    public initialData: SystemicTherapy | any = {};
    public relatedEntities: NeoplasticEntity[] = []; 

    public readonly intentChoices: RadioChoice[] = [
        {name: 'Curative', value: SystemicTherapyIntentChoices.Curative},
        {name: 'Palliative', value: SystemicTherapyIntentChoices.Palliative},
    ]

    public readonly dosageTypeChoices: RadioChoice[] = [
        {name: 'Mass', value: 'Mass'},
        {name: 'Volume', value: 'Volume'},
        {name: 'Mass Concentration', value: 'MassConcentration'},
        {name: 'Mass per surface', value: 'MassPerSurface'},
    ]


    private deletedMedications: string[] = [];

    ngOnInit() {
        // Fetch any neoplastic entities that could be related to a new entry 
        this.getRelatedEntities()
        // Construct the form 
        this.constructForm()
    }

    ngAfterViewInit() {
        this.form.get('drugs')?.valueChanges.subscribe((drugs: CodedConcept[]) => {
            // Add subforms for new drugs
            drugs.forEach((drug: CodedConcept) => {
                if (!this.medicationFormArray.value.map( (medication: SystemicTherapyMedication) => medication.drug ).includes(drug) ){
                    this.medicationFormArray.push(this.constructMedicationSubform({drug: drug} as SystemicTherapyMedication));    
                }
            });
            // Remove subforms for drugs that are no longer selected
            this.medicationFormArray.value.forEach((medication: SystemicTherapyMedication, index: number) => {
                if (!drugs.includes(medication.drug)) {
                    if (medication.id) {
                        this.deletedMedications.push(medication.id);
                    }
                    this.medicationFormArray.removeAt(index);
                }
            })
        })
    }

    constructForm(): void {

        this.medicationFormArray = this.formBuilder.array((this.initialData?.medications || [])?.map(
            (initialMedication: SystemicTherapyMedication) => {
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

    constructMedicationSubform(initalData: SystemicTherapyMedication) {
        return this.formBuilder.group({
            id: [initalData.id],
            drug: [initalData.drug, Validators.required],
            route: [initalData.route],
            dosageType: [this.getInitialDosageType(initalData)],
            dosageMass: [initalData.dosageMass],
            dosageMassConcentration: [initalData.dosageMassConcentration],
            dosageVolume: [initalData.dosageVolume],
            dosageMassSurface: [initalData.dosageRateMassSurface],
            dosageRateMass: [initalData.dosageRateMass],
            dosageRateMassConcentration: [initalData.dosageRateMassConcentration],
            dosageRateVolume: [initalData.dosageRateVolume],
            dosageRateMassSurface: [initalData.dosageRateMassSurface],
        })
    }

    getInitialDosageType(data: SystemicTherapyMedication) {
        if (data.dosageMass || data.dosageRateMass) {
            return 'Mass'
        } else if (data.dosageMassConcentration || data.dosageRateMassConcentration) {
            return 'MassConcentration'
        }  else if (data.dosageMassSurface || data.dosageRateMassSurface) {
            return 'MassPerSurface'
        }  else if (data.dosageVolume || data.dosageRateVolume) {
            return 'Volume'
        }
        return null
    }

    meditcationSubforms(): any[] {
        const formarray: FormArray = this.form.get('medications') as FormArray;
        if (formarray){
            return formarray.controls;
        }
        return [];
    }

    constructAPIPayload(data: any): SystemicTherapyCreate {    
        console.log('constructAPIPayload', data)
        return {
            caseId: this.caseId,
            targetedEntitiesIds: data.targetedEntities,
            period: {
                start: data.period.start? data.period.start: data.period.split(' - ')[0],
                end: data.period.end? data.period.end: data.period.split(' - ')[1],
            },
            cycles: data.cycles,
            intent: data.intent,
            terminationReason: data.terminationReason,
        };
    }

    private constructMedicationPayloads(data: any): SystemicTherapyMedicationCreate {
        return data.medications.map((subformData: any) => {return {
            id: subformData.id,
            drug: subformData.drug,
            route: subformData.route,
            dosageMass: subformData.dosageMass,
            dosageMassConcentration: subformData.dosageMassConcentration,
            dosageVolume: subformData.dosageVolume,
            dosageMassSurface: subformData.dosageRateMassSurface,
            dosageRateMass: subformData.dosageRateMass,
            dosageRateMassConcentration: subformData.dosageRateMassConcentration,
            dosageRateVolume: subformData.dosageRateVolume,
            dosageRateMassSurface: subformData.dosageRateMassSurface,
        }})
    }

    private getDeletedMedications(): string[] {
        return this.deletedMedications;
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