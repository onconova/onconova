import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { TestTubeDiagonal } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';

import { 
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    RiskAssessmentCreate,
    RiskAssessmentsService,
} from '../../modules/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent ,
  ReferenceMultiSelect,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'risk-assessment-form',
  templateUrl: './risk-assessment-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    CodedConceptSelectComponent,
    ReferenceMultiSelect,
    ControlErrorComponent,
  ],
})
export class RiskAssessmentFormComponent extends AbstractFormBase implements OnInit {

  private readonly riskAssessmentsService: RiskAssessmentsService = inject(RiskAssessmentsService)
  private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
  public readonly formBuilder = inject(FormBuilder)

  public readonly createService = this.riskAssessmentsService.createRiskAssessment.bind(this.riskAssessmentsService)
  public readonly updateService = this.riskAssessmentsService.updateRiskAssessmentById.bind(this.riskAssessmentsService)

  public readonly title: string = 'Tumor Marker'
  public readonly subtitle: string = 'Add new tumor marker'
  public readonly icon = TestTubeDiagonal;

  private caseId!: string;
  public initialData: RiskAssessmentCreate | any = {};
  public relatedEntities: NeoplasticEntity[] = []; 
  public resultsType: string[] = [];


  ngOnInit() {
    // Construct the form 
    this.constructForm()
    // Fetch any primary neoplastic entities that could be related to a new entry 
    this.getRelatedEntities()
  }

  constructForm(): void {
    this.form = this.formBuilder.group({
        date: [this.initialData?.date, Validators.required],
        assessedEntities: [this.initialData?.assessedEntitiesIds, Validators.required],
        methodology: [this.initialData?.methodology,Validators.required],
        risk: [this.initialData?.risk,Validators.required],
        score: [this.initialData?.score],
    });
  }
  

  constructAPIPayload(data: any): RiskAssessmentCreate {    
    return {
      caseId: this.caseId,
      assessedEntitiesIds: data.assessedEntities,
      date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
      methodology: data.methodology,
      risk: data.risk,
      score: data.score,
    };
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