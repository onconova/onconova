import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map, of } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { DiamondPlus } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { Select } from 'primeng/select';
import { ToggleSwitchModule } from 'primeng/toggleswitch';

import { 
    NeoplasticEntity, 
    NeoplasticEntitiesService,
    CodedConceptSchema,
    ComorbidityPanelCategory,
    ComorbiditiesAssessmentCreateSchema,
    ComorbiditiesAssessmentsService,
    ComorbiditiesAssessmentPanelChoices,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
  RadioChoice,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { Observable } from 'rxjs';

@Component({
  standalone: true,
  selector: 'comorbidities-form',
  templateUrl: './comorbidities-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    DatePickerComponent,
    Fluid,
    Select,
    ToggleSwitchModule,
    InputNumber,
    ButtonModule,
    ConceptSelectorComponent,
    MultiReferenceSelectComponent,
    FormControlErrorComponent,
  ],
})
export class ComorbiditiesAssessmentFormComponent extends AbstractFormBase implements OnInit {

    private readonly comorbiditiesASsessmentService: ComorbiditiesAssessmentsService = inject(ComorbiditiesAssessmentsService);
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    public readonly formBuilder = inject(FormBuilder);

    public readonly createService = (payload: ComorbiditiesAssessmentCreateSchema) => this.comorbiditiesASsessmentService.createComorbiditiesAssessment({comorbiditiesAssessmentCreateSchema: payload});
    public readonly updateService = (id: string, payload: ComorbiditiesAssessmentCreateSchema) => this.comorbiditiesASsessmentService.updateComorbiditiesAssessment({comorbiditiesAssessmentId: id, comorbiditiesAssessmentCreateSchema: payload});

    public readonly title: string = 'Comorbidities Assessment';
    public readonly subtitle: string = 'Add new comorbidities assessment';
    public readonly icon = DiamondPlus;

    private caseId!: string;
    public initialData: ComorbiditiesAssessmentCreateSchema | any = {};
    public relatedEntities: NeoplasticEntity[] = []; 
    public panelCategories: ComorbidityPanelCategory[] | undefined = []; 
    public resultsType: string[] = [];
    public panelForm: any = [];

    public comorbiditiesAssessmentPanelChoices: RadioChoice[] = [
        {name: 'No panel', value: null},
        {name: 'Charlson', value: ComorbiditiesAssessmentPanelChoices.Charlson},
        {name: 'NCI', value: ComorbiditiesAssessmentPanelChoices.Nci},
        {name: 'Elixhauser', value: ComorbiditiesAssessmentPanelChoices.Elixhauser},
    ]

  ngOnInit() {
    this.constructForm()
    this.getRelatedEntities()
    this.getComorbiditiesPanel(this.initialData?.panel)
    this.form.get('panel')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: (panel) => {
            this.getComorbiditiesPanel(panel);
            this.form.get('presentConditions')?.setValue(null)
            this.form.get('absentConditions')?.setValue(null)
        }
    })
  }

  constructForm(): void {
    this.form = this.formBuilder.group({
        date: [this.initialData?.date, Validators.required],
        indexCondition: [this.initialData?.indexConditionId, Validators.required],
        panel: [this.initialData?.panel],
        presentConditions: [this.initialData?.presentConditions],
        absentConditions: [this.initialData?.absentConditions],
    });
  }
  
  getComorbiditiesPanel(panel: ComorbiditiesAssessmentPanelChoices | null): void {
    if (panel) {
        this.comorbiditiesASsessmentService.getComorbiditiesPanelsByName({panel: panel})
        .pipe(takeUntilDestroyed(this.destroyRef))   
        .subscribe({
            next: (response) => {
                this.panelCategories = response.categories || [];
                this.panelForm = this.panelCategories.map((category) => {
                    const initialCondition = this.initialData?.presentConditions?.find((condition: CodedConceptSchema) => category.conditions.map(cond=>cond.code).includes(condition.code));
                    return {
                        label: category.label,
                        checked: this.initialData ? category.conditions.some((condition) => this.initialData?.presentConditions?.map((cond: any)=>cond.code).includes(condition.code)) : false,
                        selected: initialCondition || category.default,
                        conditions: category.conditions,
                    };
                });
            } 
        })
    } else {
        this.panelForm = [];
    }
  }

  comorbiditiesPanelToPayload() {
    let presentConditions: CodedConceptSchema[] = [];
    let absentConditions: CodedConceptSchema[] = [];
    if (!this.panelForm || this.panelForm.length==0){
        return null
    }
    this.panelForm.forEach(
        (category: any) => {
            if (category.checked) {
                presentConditions.push(category.selected)
            } else {
                absentConditions.push(category.selected)
            }
        }
    )
    return {present: presentConditions, absent: absentConditions}
  }

  constructAPIPayload(data: any): ComorbiditiesAssessmentCreateSchema {    
    const panelData = this.comorbiditiesPanelToPayload()
    return {
      caseId: this.caseId,
      indexconditionId: data.indexCondition,
      date: data.date,
      panel: data.panel,
      presentConditions: panelData ? panelData.present : data.presentConditions,
      absentConditions: panelData ? panelData.absent : data.absentConditions,
    };
  }

  private getRelatedEntities(): void {
    this.neoplasticEntitiesService.getNeoplasticEntities({caseId: this.caseId, relationship: 'primary'})
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(
      (response) => {
          this.relatedEntities = response.items
      }
    )
  }


}