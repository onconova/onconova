import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef, DestroyRef} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { HeartPulse } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';

import { 
    NeoplasticEntity, 
    NeoplasticEntitiesService, 
    RiskAssessmentCreate,
    RiskAssessmentsService,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
    selector: 'risk-assessment-form',
    templateUrl: './risk-assessment-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        InputNumber,
        ButtonModule,
        ConceptSelectorComponent,
        MultiReferenceSelectComponent,
        FormControlErrorComponent,
    ]
})
export class RiskAssessmentFormComponent extends AbstractFormBase implements OnInit {

  private readonly riskAssessmentsService: RiskAssessmentsService = inject(RiskAssessmentsService)
  private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
  public readonly formBuilder = inject(FormBuilder)

  public readonly createService = (payload: RiskAssessmentCreate) => this.riskAssessmentsService.createRiskAssessment({riskAssessmentCreate: payload})
  public readonly updateService = (id: string, payload: RiskAssessmentCreate) => this.riskAssessmentsService.updateRiskAssessmentById({riskAssessmentId: id, riskAssessmentCreate: payload})

  public readonly title: string = 'Risk Assessment'
  public readonly subtitle: string = 'Add new risk assessment'
  public readonly icon = HeartPulse;

  public initialData: RiskAssessmentCreate | any = {};
  public relatedEntities: NeoplasticEntity[] = []; 
  public resultsType: string[] = [];

  destroyRef = inject(DestroyRef);

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
      caseId: this.caseId(),
      assessedEntitiesIds: data.assessedEntities,
      date: data.date,
      methodology: data.methodology,
      risk: data.risk,
      score: data.score,
    };
  }

  private getRelatedEntities(): void {
    this.neoplasticEntitiesService.getNeoplasticEntities({caseId:this.caseId()})
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(
      (response) => {
          this.relatedEntities = response.items
      }
    )
  }


}