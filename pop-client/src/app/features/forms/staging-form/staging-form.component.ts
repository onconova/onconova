import { Component, computed, effect, inject, input } from '@angular/core';
import { FormBuilder, FormControl, Validators, FormsModule, ReactiveFormsModule  } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';

import { 
  TNMStagingCreate, 
  FIGOStagingCreate,
  BinetStagingCreate,
  RaiStagingCreate,
  BreslowDepthCreate,
  ClarkStagingCreate,
  ISSStagingCreate,
  RISSStagingCreate,
  GleasonGradeCreate,
  INSSStageCreate,
  INRGSSStageCreate,
  WilmsStageCreate,
  RhabdomyosarcomaClinicalGroupCreate,
  LymphomaStagingCreate,  
  StagingsService,
  NeoplasticEntitiesService,
  AnyStaging,
  CodedConcept,
} from '../../../shared/openapi'

import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { Fluid } from 'primeng/fluid';
import { RadioButton } from 'primeng/radiobutton';
import { InputNumber } from 'primeng/inputnumber';

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  MultiReferenceSelectComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { map } from 'rxjs';

type StagingCreate = TNMStagingCreate
            | FIGOStagingCreate
            | BinetStagingCreate
            | RaiStagingCreate
            | BreslowDepthCreate
            | ClarkStagingCreate
            | ISSStagingCreate
            | RISSStagingCreate
            | GleasonGradeCreate
            | INSSStageCreate
            | INRGSSStageCreate
            | WilmsStageCreate
            | RhabdomyosarcomaClinicalGroupCreate
            | LymphomaStagingCreate


@Component({
    selector: 'staging-form',
    templateUrl: './staging-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        Select,
        InputNumber,
        RadioButton,
        MultiReferenceSelectComponent,
        ButtonModule,
        ConceptSelectorComponent,
        FormControlErrorComponent,
    ]
})
export class StagingFormComponent extends AbstractFormBase{

    // Input signal for initial data passed to the form
    initialData = input<AnyStaging>();

    // Service injections
    readonly #stagingsService = inject(StagingsService);
    readonly #neoplasticEntitiesService = inject(NeoplasticEntitiesService);
    readonly #fb = inject(FormBuilder);

    // Create and update service methods for the form data
    public readonly createService = (payload: any) => this.#stagingsService.createStaging({payload: payload})
    public readonly updateService = (id: string, payload: any) => this.#stagingsService.updateStagingById({stagingId: id, payload: payload})

    // Define the form
    public form = this.#fb.group({
        stagingDomain: this.#fb.nonNullable.control<string>('tnm', Validators.required),
        date: this.#fb.control<string | null>(null, Validators.required),
        stagedEntities: this.#fb.control<string[]>([], Validators.required),
        stage: this.#fb.control<CodedConcept | null>(null, Validators.required),
        tnm: this.#fb.group({
            pathological: this.#fb.control<boolean | null>(null),
            methodology: this.#fb.control<CodedConcept | null>(null),
            primaryTumor: this.#fb.control<CodedConcept | null>(null),
            regionalNodes: this.#fb.control<CodedConcept | null>(null),
            distantMetastases: this.#fb.control<CodedConcept | null>(null),
            grade: this.#fb.control<CodedConcept | null>(null),
            residualTumor: this.#fb.control<CodedConcept | null>(null),
            lymphaticInvasion: this.#fb.control<CodedConcept | null>(null),
            venousInvasion: this.#fb.control<CodedConcept | null>(null),
            perineuralInvasion: this.#fb.control<CodedConcept | null>(null),
            serumTumorMarkerLevel: this.#fb.control<CodedConcept | null>(null),
        }),
        figo: this.#fb.group({
            methodology: this.#fb.control<CodedConcept | null>(null),
        }),
        rai: this.#fb.group({
            methodology: this.#fb.control<CodedConcept | null>(null),
        }),
        breslow: this.#fb.group({
            depth: this.#fb.control<number | null>(null, Validators.required),
            isUlcered: this.#fb.control<boolean | null>(null),
        }),
        lymphoma: this.#fb.group({
            methodology: this.#fb.control<CodedConcept | null>(null),
            bulky: this.#fb.control<boolean | null>(null),
            pathological: this.#fb.control<boolean | null>(null),
            modifiers: this.#fb.control<CodedConcept[]>([]),
        }),
    });

  // Effect to patch initial data
    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;
      
        this.form.patchValue({
          stagingDomain: data.stagingDomain ?? 'tnm',
          date: data.date ?? null,
          stagedEntities: data.stagedEntitiesIds ?? [],
          stage: data.stage ?? null,
          tnm: {
            pathological: data.pathological ?? null,
            methodology: data.methodology ?? null,
            primaryTumor: data.primarytumor ?? null,
            regionalNodes: data.regionalnodes ?? null,
            distantMetastases: data.distantmetastases ?? null,
            grade: data.grade ?? null,
            residualTumor: data.residualtumor ?? null,
            lymphaticInvasion: data.lymphaticinvasion ?? null,
            venousInvasion: data.venousinvasion ?? null,
            perineuralInvasion: data.perineuralinvasion ?? null,
            serumTumorMarkerLevel: data.serumtumormarkerlevel ?? null,
          },
          figo: {
            methodology: data.methodology ?? null,
          },
          rai: {
            methodology: data.methodology ?? null,
          },
          breslow: {
            depth: data.depth ?? null,
            isUlcered: data.isUlcered ?? null,
          },
          lymphoma: {
            methodology: data.methodology ?? null,
            bulky: data.bulky ?? null,
            pathological: data.pathological ?? null,
            modifiers: data.modifiers ?? [],
          },
        });
      });

    // All neoplastic entities related to this patient case
    public relatedEntities = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
    }) 

    // Reactive signal for the current staging domain
    #currentStagingDomain = toSignal(this.form.get('stagingDomain')!.valueChanges)
    #stagingDomainChangesEffect = effect(() => {
        if (this.#currentStagingDomain()) {
            this.form.controls['stage'].setValue(null)
        }
        if (this.#currentStagingDomain() === 'breslow') {
            this.form.controls['breslow'].controls['depth'].addValidators([Validators.required])
            this.form.controls['stage'].removeValidators([Validators.required])
        } else {
            this.form.controls['breslow'].controls['depth'].removeValidators([Validators.required])
            this.form.controls['stage'].addValidators([Validators.required])
        }
        this.form.controls['stage'].updateValueAndValidity()
        this.form.controls['breslow'].controls['depth'].updateValueAndValidity()
    })

    // API Payload construction function
    readonly payload = (): StagingCreate => {    
        const data = this.form.value;
        const payload = {
            stagingDomain: data.stagingDomain,
            caseId: this.caseId(),
            date: data.date,
            stagedEntitiesIds: data.stagedEntities,
            stage: data.stage,
        }
        switch (data.stagingDomain) {
            case 'tnm':
                return {
                    ...payload,
                    methodology: data.tnm!.methodology,
                    pathological: data.tnm!.pathological,
                    primaryTumor: data.tnm!.primaryTumor,
                    regionalNodes: data.tnm!.regionalNodes,
                    distantMetastases: data.tnm!.distantMetastases,
                    grade: data.tnm!.grade,
                    residualTumor: data.tnm!.residualTumor,
                    lymphaticInvasion: data.tnm!.lymphaticInvasion,
                    venousInvasion: data.tnm!.venousInvasion,
                    perineuralInvasion: data.tnm!.perineuralInvasion,
                    serumTumorMarkerLevel: data.tnm!.serumTumorMarkerLevel,
                } as TNMStagingCreate;
            case 'figo':
                return {
                    ...payload,
                    methodology: data.figo!.methodology,
                } as FIGOStagingCreate;
            case 'rai':
                return {
                    ...payload,
                    methodology: data.rai!.methodology,
                } as RaiStagingCreate;
            case 'breslow':
                return {
                    ...payload,
                    depth: data.breslow!.depth,
                    isUlcered: data.breslow!.isUlcered,
                } as BreslowDepthCreate;
            case 'lymphoma':
                return {
                    ...payload,
                    methodology: data.lymphoma!.methodology,
                    bulky: data.lymphoma!.bulky,
                    pathological: data.lymphoma!.pathological,
                    modifiers: data.lymphoma!.modifiers ?? [],
                } as LymphomaStagingCreate;
            case 'rhabdo':
                return payload as RhabdomyosarcomaClinicalGroupCreate
            default:
                return payload as StagingCreate
        }
    }

    // Human readable choices for UI elements
    public stagingDomains = [
        {value: 'tnm', label: 'TNM Staging'},
        {value: 'figo', label: 'FIGO Staging'},
        {value: 'binet', label: 'Binet Staging'},
        {value: 'rai', label: 'Rai Staging'},
        {value: 'breslow', label: 'Breslow Staging'},
        {value: 'iss', label: 'Myeloma ISS Staging'},
        {value: 'riss', label: 'Myeloma RISSS Staging'},
        {value: 'inss', label: 'Neuroblastoma INSS Staging'},
        {value: 'inrgss', label: 'Neuroblastoma INRGSS Staging'},
        {value: 'gleason', label: 'Prostate Gleason Staging'},
        {value: 'rhabdomyosarcoma', label: 'Rhabdomyosarcoma Clinical Group Staging'},
        {value: 'wilms', label: 'Wilms Tumor Staging'},
        {value: 'lymphoma', label: 'Lymphoma Staging'},
    ]
    public optionsYesNoUnknown = [
        {value: null, label: 'Unknwon'},
        {value: true, label: 'Yes'},
        {value: false, label: 'No'},
    ]    

}