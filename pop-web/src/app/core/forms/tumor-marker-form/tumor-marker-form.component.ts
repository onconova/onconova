import { Component, inject, OnInit,ViewEncapsulation } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { TestTubeDiagonal } from 'lucide-angular';

import { 
  NeoplasticEntity, 
  NeoplasticEntitiesService, 
  TumorMarkerCreate,
  TumorMarkersService
} from '../../modules/openapi'

import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { Fluid } from 'primeng/fluid';
import { SelectButton } from 'primeng/selectbutton';
import { Tooltip } from 'primeng/tooltip';

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent ,
  ReferenceMultiSelect,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'tumor-marker-form',
  styleUrl: './tumor-marker-form.component.css',
  templateUrl: './tumor-marker-form.component.html',
  encapsulation: ViewEncapsulation.None,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    SelectButton,
    Select,
    Tooltip,
    ButtonModule,
    CodedConceptSelectComponent,
    ReferenceMultiSelect,
    ControlErrorComponent,
  ],
})
export class TumorMarkerFormComponent extends AbstractFormBase implements OnInit{

  private readonly tumorMarkersService: TumorMarkersService = inject(TumorMarkersService)
  private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
  public readonly formBuilder = inject(FormBuilder)

  public readonly createService = this.tumorMarkersService.createTumorMarker.bind(this.tumorMarkersService)
  public readonly updateService = this.tumorMarkersService.updateTumorMarkerById.bind(this.tumorMarkersService)


  public readonly title: string = 'Tumor Marker'
  public readonly subtitle: string = 'Add new tumor marker'
  public readonly icon = TestTubeDiagonal;

    private caseId!: string;
    public initialData: TumorMarkerCreate | any = {};
    public relatedEntities: NeoplasticEntity[] = []; 
    public analytes = [
        'CEA',   
        'CA19-9',
        'CA125',  
        'CA15-3',
        'CA72-4', 
        'CA27-29',
        'NSE',    
        'LDH', 
        'CgA',   
        'S100A1', 
        'S100B',  
        'PSA', 
        'AFP',    
        'β-hCG',  
        'B2M', 
        'CYFRA 21-1', 
        'EBV',  
        'PD-L1 ICS',
        'PD-L1 TPS',
        'PD-L1 CPS',
        'HER2',
        'ER',
        'PR',
        'AR',
        'Ki67', 
        'SSTR2',
        'MLH1',
        'MSH2',
        'MSH6',
        'PMS2',
        'p16',
        'EBV',
        'HPV',
    ]

  ngOnInit() {
    // Construct the form 
    this.constructForm()
    // Fetch any primary neoplastic entities that could be related to a new entry 
    this.getRelatedEntities()
  }

  constructForm() {
    this.form = this.formBuilder.group({
        date: [this.initialData?.date, Validators.required],
        relatedEntities: [this.initialData?.relatedEntities, Validators.required],
        analyte: [this.initialData?.analyte,Validators.required],
    });
  }

  constructAPIPayload(data: any): TumorMarkerCreate {    
    return {
      caseId: this.caseId,
      relatedEntitiesIds: data.relatedEntities,
      date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
      analyte: data.analyte,
    };
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