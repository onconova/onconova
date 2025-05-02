import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { Form, FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule, FormArray } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { Radiation } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { Fieldset } from 'primeng/fieldset';

import { 
    CodedConcept,
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    RadiotherapyCreate,
    RadiotherapyDosage,
    RadiotherapyDosageCreate,
    RadiotherapySetting,
    RadiotherapySettingCreate,
    RadiotherapiesService,
    Radiotherapy,
    RadiotherapyIntentChoices
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
    selector: 'radiotherapy-form',
    templateUrl: './radiotherapy-form.component.html',
    encapsulation: ViewEncapsulation.None,
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
    ]
})
export class RadiotherapyFormComponent extends AbstractFormBase implements OnInit {

    private readonly radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService)
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = (payload: RadiotherapyCreate) => this.radiotherapiesService.createRadiotherapy({radiotherapyCreate: payload});
    public readonly updateService = (id: string, payload: RadiotherapyCreate) => this.radiotherapiesService.updateRadiotherapy({radiotherapyId: id, radiotherapyCreate: payload})
    override readonly subformsServices = [
        {
            payloads: this.constructDosagePayloads.bind(this),
            deletedEntries: this.getDeletedDosages.bind(this),
            delete: (parentId: string, id: string) => this.radiotherapiesService.deleteRadiotherapyDosage({radiotherapyId: parentId, dosageId: id}),
            create: (parentId: string, payload: RadiotherapyDosageCreate) => this.radiotherapiesService.createRadiotherapyDosage({radiotherapyId: parentId, radiotherapyDosageCreate: payload}),
            update: (parentId: string, id: string, payload: RadiotherapyDosageCreate) => this.radiotherapiesService.updateRadiotherapyDosage({radiotherapyId: parentId, dosageId: id, radiotherapyDosageCreate: payload}),
        },
        {
            payloads: this.constructSettingsPayloads.bind(this),
            deletedEntries: this.getDeletedSettings.bind(this),
            delete: (parentId: string, id: string) => this.radiotherapiesService.deleteRadiotherapySetting({radiotherapyId: parentId, settingId: id}),
            create: (parentId: string, payload: RadiotherapySettingCreate) => this.radiotherapiesService.createRadiotherapySetting({radiotherapyId: parentId, radiotherapySettingCreate: payload}),
            update: (parentId: string, id: string, payload: RadiotherapySettingCreate) => this.radiotherapiesService.updateRadiotherapySetting({radiotherapyId: parentId, settingId: id, radiotherapySettingCreate: payload}),
        }
    ]
    
    public readonly title: string = 'Radiotherapy'
    public readonly subtitle: string = 'Add new radiotherapy'
    public readonly icon = Radiation;

    private caseId!: string;
    public dosageFormArray!: FormArray;
    public settingsFormArray!: FormArray;
    public initialData: Radiotherapy | any = {};
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
    }

    constructForm(): void {

        this.dosageFormArray = this.formBuilder.array((this.initialData?.dosages || [null])?.map(
            (initialDosage: RadiotherapyDosage) => {
                return this.constructDosageSubform(initialDosage)
            }
        ))
        this.settingsFormArray = this.formBuilder.array((this.initialData?.settings || [])?.map(
            (initialSetting: RadiotherapySetting) => {
                return this.constructSettingsSubform(initialSetting)
            }
        ))
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

    constructDosageSubform(initalData: RadiotherapyDosage | null ) {
        return this.formBuilder.group({
            id: [initalData?.id],
            fractions: [initalData?.fractions, Validators.required],
            dose: [initalData?.dose, Validators.required],
            irradiatedVolume: [initalData?.irradiatedVolume],
            irradiatedVolumeMorphology: [initalData?.irradiatedVolumeMorphology],
            irradiatedVolumeQualifier: [initalData?.irradiatedVolumeQualifier]
        })
    }

    constructSettingsSubform(initalData: RadiotherapySetting) {
        return this.formBuilder.group({
            id: [initalData.id],
            modality: [initalData.modality],
            technique: [initalData.technique],
        })
    }


    constructAPIPayload(data: any): RadiotherapyCreate {    
        return {
            caseId: this.caseId,
            targetedEntitiesIds: data.targetedEntities,
            period: {
                start: data.period.start? data.period.start: data.period.split(' - ')[0],
                end: data.period.end? data.period.end: data.period.split(' - ')[1],
            },
            sessions: data.sessions,
            intent: data.intent,
            terminationReason: data.terminationReason,
        };
    }

    private constructDosagePayloads(data: any): RadiotherapyDosageCreate {
        return data.dosages.map((subformData: any) => {return {
            id: subformData.id,
            fractions: subformData.fractions,
            dose: subformData.dose, 
            irradiatedVolume: subformData.irradiatedVolume,
            irradiatedVolumeMorphology: subformData.irradiatedVolumeMorphology,
            irradiatedVolumeQualifier: subformData.irradiatedVolumeQualifier
        }})
    }

    private constructSettingsPayloads(data: any): RadiotherapyDosageCreate {
        return data.settings.map((subformData: any) => {return {
            id: subformData.id,
            modality: subformData.modality,
            technique: subformData.technique, 
        }})
    }

    public addSetting() {
        this.settingsFormArray.push(this.constructSettingsSubform({} as RadiotherapySetting));
    }

    public removeSetting(index: number) {
        const settingValue = this.settingsFormArray.value[index];
        if (settingValue?.id) {
            this.deletedRadiotherapySettings.push(settingValue.id);
        }
        this.settingsFormArray.removeAt(index);
    }

    public addDosage() {
        this.dosageFormArray.push(this.constructDosageSubform({} as RadiotherapyDosage));
    }

    public removeDosage(index: number) {
        const dosageValue = this.dosageFormArray.value[index];
        if (dosageValue?.id) {
            this.deletedRadiotherapyDosages.push(dosageValue.id);
        }
        this.dosageFormArray.removeAt(index);
    }

    private getDeletedDosages(): string[] {
        return this.deletedRadiotherapyDosages;
    }

    private getDeletedSettings(): string[] {
        return this.deletedRadiotherapySettings;
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