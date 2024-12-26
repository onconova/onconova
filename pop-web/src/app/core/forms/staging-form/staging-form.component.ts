import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule, FormGroupDirective } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { Tags } from 'lucide-angular';

import { 
  TNMStaging, TNMStagingCreate, 
  FIGOStaging, FIGOStagingCreate,
  BinetStaging, BinetStagingCreate,
  RaiStaging, RaiStagingCreate,
  BreslowDepth, BreslowDepthCreate,
  ClarkStaging, ClarkStagingCreate,
  ISSStaging, ISSStagingCreate,
  RISSStaging, RISSStagingCreate,
  GleasonGrade, GleasonGradeCreate,
  INSSStage, INSSStageCreate,
  INRGSSStage, INRGSSStageCreate,
  WilmsStage, WilmsStageCreate,
  RhabdomyosarcomaClinicalGroup, RhabdomyosarcomaClinicalGroupCreate,
  LymphomaStaging, LymphomaStagingCreate,  
  StagingsService,
  NeoplasticEntity,
  NeoplasticEntitiesService,
} from '../../../shared/openapi'

import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { Fluid } from 'primeng/fluid';
import { RadioButton } from 'primeng/radiobutton';
import { InputNumber } from 'primeng/inputnumber';

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent,
  ReferenceMultiSelect,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { EmptyObject } from 'chart.js/dist/types/basic';

type Staging = TNMStaging 
            | FIGOStaging
            | BinetStaging
            | RaiStaging
            | BreslowDepth
            | ClarkStaging
            | ISSStaging
            | RISSStaging
            | GleasonGrade
            | INSSStage
            | INRGSSStage
            | WilmsStage
            | RhabdomyosarcomaClinicalGroup
            | LymphomaStaging

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
  standalone: true,
  selector: 'staging-form',
  templateUrl: './staging-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    Select,
    InputNumber,
    RadioButton,
    ReferenceMultiSelect,
    ButtonModule,
    CodedConceptSelectComponent,
    ControlErrorComponent,
    
  ],  
})
export class StagingFormComponent extends AbstractFormBase implements OnInit{

    private readonly stagingsService = inject(StagingsService)
    private readonly neoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = this.stagingsService.createStaging.bind(this.stagingsService)
    public readonly updateService = this.stagingsService.updateStagingById.bind(this.stagingsService)

    public readonly title: string = 'Staging'
    public readonly subtitle: string = 'Add new staging'
    public readonly icon = Tags;

    private caseId!: string;
    public initialData: Staging | EmptyObject = {};

    public currentStagingForm!: string;
    public relatedEntities: NeoplasticEntity[] = []; 
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
        {value: 'rhabdo', label: 'Rhabdomyosarcoma Clinical Group Staging'},
        {value: 'wilms', label: 'Wilms Tumor Staging'},
        {value: 'lymphoma', label: 'Lymphoma Staging'},
    ]

    public optionsYesNoUnknown = [
        {value: null, label: 'Unknwon'},
        {value: true, label: 'Yes'},
        {value: false, label: 'Noe'},
    ]
    
    ngOnInit() {
        this.currentStagingForm = this.initialData?.stagingDomain || 'tnm'
        // Construct the form 
        this.constructForm()
        this.getRelatedEntities()
    }

    currentFormExtras: any | null= null

    constructForm() {
        let data = this.initialData as any;
        this.form = this.formBuilder.group({
            date: [data?.date,Validators.required],
            stagedEntities: [data?.stagedEntitiesIds, Validators.required],
            stage: [data?.stage, Validators.required],
        });
        this.updateForm()
    }
    updateForm() {
        let additionalControlers: any | null = null;
        let data = this.initialData as any
        switch (this.currentStagingForm) {
            case 'tnm':
                additionalControlers = {
                    pathological: new FormControl(data?.pathological),                 
                    methodology: new FormControl(data?.methodology),
                    primaryTumor: new FormControl(data?.primaryTumor),  
                    regionalNodes: new FormControl(data?.regionalNodes),  
                    distantMetastases: new FormControl(data?.distantMetastases),  
                    grade: new FormControl(data?.grade),  
                    residualTumor: new FormControl(data?.residualTumor),  
                    lymphaticInvasion: new FormControl(data?.lymphaticInvasion),  
                    venousInvasion: new FormControl(data?.venousInvasion),  
                    perineuralInvasion: new FormControl(data?.perineuralInvasion),   
                    serumTumorMarkerLevel: new FormControl(data?.serumTumorMarkerLevel),   
                }
                break;
            case 'figo':
                additionalControlers = {
                    methodology: new FormControl(data?.methodology),
                }
                break;
            case 'rai':
                additionalControlers = {
                    methodology: new FormControl(data?.methodology),
                }
                break;
            case 'breslow':
                additionalControlers = {
                    depth: new FormControl(data?.depth,[Validators.required]),
                    isUlcered: new FormControl(data?.isUlcered),
                }
                break;
            case 'lymphoma':
                additionalControlers = {
                    methodology: new FormControl(data?.methodology),
                    bulky: new FormControl(data?.bulky),
                    pathological: new FormControl(data?.pathological),
                    modifiers: new FormControl(data?.modifiers),
                }
                break;
            default:
                additionalControlers = {}
                break;
        }
        if (this.currentFormExtras) {
            Object.entries(this.currentFormExtras).forEach(            
                control =>  {
                    if (!(control[0] in additionalControlers)) {
                        this.form.removeControl(control[0])
                    }
                }
            )
        }
        Object.entries(additionalControlers).forEach(
            control =>  {
                this.form.addControl(control[0], control[1])
            }
        )
        this.currentFormExtras = additionalControlers

    }

    constructAPIPayload(data: any): StagingCreate {    
        const sharedValues = {
            stagingDomain: this.currentStagingForm,
            caseId: this.caseId,
            date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
            stagedEntitiesIds: data.stagedEntities,
            stage: data.stage,
        }
        let additionalValues: any;
        switch (this.currentStagingForm) {
            case 'tnm':
                additionalValues = {
                    methodology: data.methodology,
                    pathological: data.pathological,
                    primaryTumor: data.primaryTumor,
                    regionalNodes: data.regionalNodes,
                    distantMetastases: data.distantMetastases,
                    grade: data.grade,
                    residualTumor: data.residualTumor,
                    lymphaticInvasion: data.lymphaticInvasion,
                    venousInvasion: data.venousInvasion,
                    perineuralInvasion: data.perineuralInvasion,
                    serumTumorMarkerLevel: data.serumTumorMarkerLevel,
                };
                break;
            case 'figo':
                additionalValues = {
                    methodology: data.methodology,
                };
                break;
            case 'rai':
                additionalValues = {
                    methodology: data.methodology,
                };
                break;
            case 'breslow':
                additionalValues = {
                    stagingDomain: 'breslow',
                    depth: data.depth,
                    isUlcered: data.isUlcered,
                }
                break;
            case 'lymphoma':
                additionalValues = {
                    methodology: data.methodology,
                    bulky: data.bulky,
                    pathological: data.pathological,
                    modifiers: data.modifiers,
                }
                break;
            default:
                additionalValues = {}
                break;
        }
        return {
            ...sharedValues,
            ...additionalValues,
        }
    }


    private getRelatedEntities() {
        this.neoplasticEntitiesService.getNeoplasticEntities(this.caseId)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe(
          (response) => {
              this.relatedEntities = response.items
          }
        )
    }

}