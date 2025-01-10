import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { Form, FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule, FormArray } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { Radiation } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { Fieldset } from 'primeng/fieldset';

import { 
    CodedConceptSchema,
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    RadiotherapyCreateSchema,
    RadiotherapyDosageSchema,
    RadiotherapyDosageCreateSchema,
    RadiotherapySettingSchema,
    RadiotherapySettingCreateSchema,
    RadiotherapiesService,
    RadiotherapySchema,
    RadiotherapyIntentChoices
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent ,
  ReferenceMultiSelect,
  RadioChoice,
  RadioSelectComponent,
  MeasureInputComponent,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'radiotherapy-form',
  templateUrl: './radiotherapy-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    Fieldset,
    MeasureInputComponent,
    CodedConceptSelectComponent,
    ReferenceMultiSelect,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class RadiotherapyFormComponent extends AbstractFormBase implements OnInit {

    private readonly radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService)
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = this.radiotherapiesService.createRadiotherapy.bind(this.radiotherapiesService)
    public readonly updateService = this.radiotherapiesService.updateRadiotherapy.bind(this.radiotherapiesService)
    override readonly subformsServices = [
        {
            payloads: this.constructDosagePayloads.bind(this),
            deletedEntries: this.getDeletedMedications.bind(this),
            delete: this.radiotherapiesService.deleteRadiotherapyDosage.bind(this.radiotherapiesService),
            create: this.radiotherapiesService.createRadiotherapyDosage.bind(this.radiotherapiesService),
            update: this.radiotherapiesService.updateRadiotherapyDosage.bind(this.radiotherapiesService),
        },
        {
            payloads: this.constructSettingsPayloads.bind(this),
            deletedEntries: this.getDeletedMedications.bind(this),
            delete: this.radiotherapiesService.deleteRadiotherapySetting.bind(this.radiotherapiesService),
            create: this.radiotherapiesService.createRadiotherapySetting.bind(this.radiotherapiesService),
            update: this.radiotherapiesService.updateRadiotherapySetting.bind(this.radiotherapiesService),
        }
    ]
    
    public readonly title: string = 'Radiotherapy'
    public readonly subtitle: string = 'Add new radiotherapy'
    public readonly icon = Radiation;

    private caseId!: string;
    public dosageFormArray!: FormArray;
    public settingsFormArray!: FormArray;
    public initialData: RadiotherapySchema | any = {};
    public relatedEntities: NeoplasticEntity[] = []; 

    public readonly intentChoices: RadioChoice[] = [
        {name: 'Curative', value: RadiotherapyIntentChoices.Curative},
        {name: 'Palliative', value: RadiotherapyIntentChoices.Palliative},
    ]

    private deletedRadiotherapyDosages: string[] = [];
    private deletedRadiotherapySettings: string[] = [];

    ngOnInit() {
        // Fetch any neoplastic entities that could be related to a new entry 
        this.getRelatedEntities()
        // Construct the form 
        this.constructForm()
        this.dosageFormArray.push(this.constructDosageSubform(null))
    }

    constructForm(): void {

        this.dosageFormArray = this.formBuilder.array((this.initialData?.dosages || [])?.map(
            (initialDosage: RadiotherapyDosageSchema) => {
                return this.constructDosageSubform(initialDosage)
            }
        ))
        this.settingsFormArray = this.formBuilder.array((this.initialData?.settings || [])?.map(
            (initialSetting: RadiotherapySettingSchema) => {
                return this.constructSettingsSubform(initialSetting)
            }
        ))
        console.log('this.initialData', this.initialData)
        this.form = this.formBuilder.group({
            period: [this.initialData?.period, Validators.required],
            targetedEntities: [this.initialData?.targetedEntitiesIds, Validators.required],
            sessions: [this.initialData?.sessions,Validators.required],
            intent: [this.initialData?.intent,Validators.required],
            terminationReason: [this.initialData?.terminationReason],
            dosages: this.dosageFormArray,
            settings: this.settingsFormArray,
        });
    }

    constructDosageSubform(initalData: RadiotherapyDosageSchema | null ) {
        return this.formBuilder.group({
            id: [initalData?.id],
            fractions: [initalData?.fractions, Validators.required],
            dose: [initalData?.dose, Validators.required],
            irradiatedVolume: [initalData?.irradiatedVolume],
            irradiatedVolumeMorphology: [initalData?.irradiatedVolumeMorphology],
            irradiatedVolumeQualifier: [initalData?.irradiatedVolumeQualifier]
        })
    }

    constructSettingsSubform(initalData: RadiotherapySettingSchema) {
        return this.formBuilder.group({
            id: [initalData.id],
            modality: [initalData.modality],
            technique: [initalData.technique],
        })
    }


    constructAPIPayload(data: any): RadiotherapyCreateSchema {    
        console.log('constructAPIPayload', data)
        return {
            caseId: this.caseId,
            targetedEntitiesIds: data.targetedEntities,
            period: {
                start: data.period.start? data.period.start: moment(data.period.split(' - ')[0], ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
                end: data.period.end? data.period.end: moment(data.period.split(' - ')[1], ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
            },
            sessions: data.sessions,
            intent: data.intent,
            terminationReason: data.terminationReason,
        };
    }

    private constructDosagePayloads(data: any): RadiotherapyDosageCreateSchema {
        return data.dosages.map((subformData: any) => {return {
            id: subformData.id,
            fractions: subformData.fractions,
            dose: subformData.dose, 
            irradiatedVolume: subformData.irradiatedVolume,
            irradiatedVolumeMorphology: subformData.irradiatedVolumeMorphology,
            irradiatedVolumeQualifier: subformData.irradiatedVolumeQualifier
        }})
    }

    private constructSettingsPayloads(data: any): RadiotherapyDosageCreateSchema {
        return data.settings.map((subformData: any) => {return {
            id: subformData.id,
            modality: subformData.modality,
            technique: subformData.technique, 
        }})
    }
    private getDeletedMedications(): string[] {
        return this.deletedRadiotherapyDosages;
    }

    private getDeletedSettings(): string[] {
        return this.deletedRadiotherapySettings;
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