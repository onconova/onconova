import { Component, inject, ViewEncapsulation, input, computed, effect} from '@angular/core';
import { FormBuilder, Validators, FormsModule, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs';
import { rxResource } from '@angular/core/rxjs-interop';


import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { Fieldset } from 'primeng/fieldset';

import { 
    CodedConcept,
    NeoplasticEntitiesService, 
    RadiotherapyCreate,
    RadiotherapyDosage,
    RadiotherapyDosageCreate,
    RadiotherapySetting,
    RadiotherapySettingCreate,
    RadiotherapiesService,
    Radiotherapy,
    RadiotherapyIntentChoices,
    Period,
    Measure
} from 'pop-api-client'

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
import { SelectButton } from 'primeng/selectbutton';

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
        SelectButton,
        Fieldset,
        MeasureInputComponent,
        ConceptSelectorComponent,
        MultiReferenceSelectComponent,
        FormControlErrorComponent,
    ]
})
export class RadiotherapyFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    public initialData = input<Radiotherapy>();

    // Service injections
    readonly #radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService)
    readonly #neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    readonly #fb = inject(FormBuilder)

    public readonly createService = (payload: RadiotherapyCreate) => this.#radiotherapiesService.createRadiotherapy({radiotherapyCreate: payload});
    public readonly updateService = (id: string, payload: RadiotherapyCreate) => this.#radiotherapiesService.updateRadiotherapy({radiotherapyId: id, radiotherapyCreate: payload})
    override subformsServices = [
        {
            payloads: this.dosagePayloads.bind(this),
            deletedEntries: this.getDeletedDosages.bind(this),
            delete: (parentId: string, id: string) => this.#radiotherapiesService.deleteRadiotherapyDosage({radiotherapyId: parentId, dosageId: id}),
            create: (parentId: string, payload: RadiotherapyDosageCreate) => this.#radiotherapiesService.createRadiotherapyDosage({radiotherapyId: parentId, radiotherapyDosageCreate: payload}),
            update: (parentId: string, id: string, payload: RadiotherapyDosageCreate) => this.#radiotherapiesService.updateRadiotherapyDosage({radiotherapyId: parentId, dosageId: id, radiotherapyDosageCreate: payload}),
        },
        {
            payloads: this.settingsPayloads.bind(this),
            deletedEntries: this.getDeletedSettings.bind(this),
            delete: (parentId: string, id: string) => this.#radiotherapiesService.deleteRadiotherapySetting({radiotherapyId: parentId, settingId: id}),
            create: (parentId: string, payload: RadiotherapySettingCreate) => this.#radiotherapiesService.createRadiotherapySetting({radiotherapyId: parentId, radiotherapySettingCreate: payload}),
            update: (parentId: string, id: string, payload: RadiotherapySettingCreate) => this.#radiotherapiesService.updateRadiotherapySetting({radiotherapyId: parentId, settingId: id, radiotherapySettingCreate: payload}),
        }
    ]
    #deletedDosages: string[] = [];
    #deletedSettings: string[] = [];

    // Define the main form
    public form = this.#fb.group({
        period: this.#fb.control<Period | string | null>(null, Validators.required),
        targetedEntities: this.#fb.control<string[]>([], Validators.required),
        sessions: this.#fb.control<number | null>(null, Validators.required),
        intent: this.#fb.control<RadiotherapyIntentChoices | null>(null, Validators.required),
        terminationReason: this.#fb.control<CodedConcept | null>(null),
        dosages: this.#fb.array<FormGroup>([]),
        settings: this.#fb.array<FormGroup>([]),
    });

    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;
      
        this.form.patchValue({
          period: data.period ?? null,
          targetedEntities: data.targetedEntitiesIds ?? [],
          sessions: data.sessions ?? null,
          intent: data.intent ?? null,
          terminationReason: data.terminationReason ?? null,
        });      
        (data.dosages ?? []).forEach((initialData: RadiotherapyDosage) => {
            this.form.controls.dosages.push(this.#dosageForm(initialData));
        });
        (data.settings ?? []).forEach((initialData: RadiotherapySetting) => {
            this.form.controls.settings.push(this.#settingsForm(initialData));
        });
      });

    //Definition for the dynamic subform constructor
    #dosageForm = (initialData: RadiotherapyDosage) => this.#fb.group({
        id: this.#fb.control<string | null>(
            initialData?.id  || null
        ),
        fractions: this.#fb.control<number | null>(
            initialData?.fractions || null, 
            Validators.required
        ),
        dose: this.#fb.control<Measure | null>(
            initialData?.dose || null, 
            Validators.required
        ),
        irradiatedVolume: this.#fb.control<CodedConcept | null>(
            initialData?.irradiatedVolume || null
        ),
        irradiatedVolumeMorphology: this.#fb.control<CodedConcept | null>(
            initialData?.irradiatedVolumeMorphology || null
        ),
    })

    //Definition for the dynamic subform constructor
    #settingsForm = (initialData: RadiotherapySetting) => this.#fb.group({
        id: this.#fb.control<string | null>(
            initialData?.id  || null
        ),
        modality: this.#fb.control<CodedConcept | null>(
            initialData?.modality || null, 
            Validators.required
        ),
        technique: this.#fb.control<CodedConcept | null>(
            initialData?.technique || null, 
        ),
    })

    // API Payload construction functions
    readonly payload = (): RadiotherapyCreate => {    
        const data = this.form.value;
        const period = data.period!;
        return {
            caseId: this.caseId(),
            targetedEntitiesIds: data.targetedEntities!,
            period: {
                start: typeof period === 'string' ? period.split(' - ')[0] : period.start,
                end: typeof period === 'string' ? period.split(' - ')[1] : period.end,
            },
            sessions: data.sessions!,
            intent: data.intent!,
            terminationReason: data.terminationReason ?? undefined,
        };
    }
    private dosagePayloads(): RadiotherapyDosageCreate[] {
        const data = this.form.value;
        return data.dosages!.map((subformData: any) => {return {
            id: subformData.id,
            fractions: subformData.fractions,
            dose: subformData.dose, 
            irradiatedVolume: subformData.irradiatedVolume,
            irradiatedVolumeMorphology: subformData.irradiatedVolumeMorphology,
            irradiatedVolumeQualifier: subformData.irradiatedVolumeQualifier
        }})
    }
    private settingsPayloads(): RadiotherapySettingCreate[] {
        const data = this.form.value;
        return data.settings!.map((subformData: any) => {return {
            id: subformData.id,
            modality: subformData.modality,
            technique: subformData.technique, 
        }})
    }

    // Get all neoplastic entities for the current case
    public relatedEntities = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items))
    })

    // Choices for UI elements
    public readonly intentChoices = [
        {label: 'Curative', value: RadiotherapyIntentChoices.Curative},
        {label: 'Palliative', value: RadiotherapyIntentChoices.Palliative},
    ]

    public addSetting() {
        this.form.controls['settings'].push(this.#settingsForm({} as RadiotherapySetting));
    }
    public addDosage() {
        this.form.controls['dosages'].push(this.#dosageForm({} as RadiotherapyDosage));
    }

    public removeSetting(index: number) {
        const settingFormArray = this.form.controls['dosages'];
        const settingValue = settingFormArray.value[index];
        if (settingValue?.id) {
            this.#deletedSettings.push(settingValue.id);
        }
        settingFormArray.removeAt(index);
    }
    public removeDosage(index: number) {
        const dosageFormArray = this.form.controls['dosages'];
        const dosageValue = dosageFormArray.value[index];
        if (dosageValue?.id) {
            this.#deletedDosages.push(dosageValue.id);
        }
        dosageFormArray.removeAt(index);
    }

    private getDeletedDosages(): string[] {
        return this.#deletedDosages;
    }
    private getDeletedSettings(): string[] {
        return this.#deletedSettings;
    }

}