import { Component, computed, effect, inject, input } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { Select } from 'primeng/select';
import { ToggleSwitchModule } from 'primeng/toggleswitch';

import { 
    NeoplasticEntitiesService,
    CodedConcept,
    ComorbiditiesAssessmentCreate,
    ComorbiditiesAssessmentsService,
    ComorbiditiesAssessmentPanelChoices,
    ComorbiditiesAssessment,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  RadioChoice,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
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
        ButtonModule,
        ConceptSelectorComponent,
        FormControlErrorComponent,
    ]
})
export class ComorbiditiesAssessmentFormComponent extends AbstractFormBase {

  // Input signal for initial data passed to the form
  initialData = input<ComorbiditiesAssessment>();

  // Service injections using Angular's `inject()` API
  readonly #comorbiditiesService: ComorbiditiesAssessmentsService = inject(ComorbiditiesAssessmentsService);
  readonly #neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
  readonly #formBuilder = inject(FormBuilder);

  // Create and update service methods for the form data
  readonly createService = (payload: ComorbiditiesAssessmentCreate) => this.#comorbiditiesService.createComorbiditiesAssessment({comorbiditiesAssessmentCreate: payload});
  readonly updateService = (id: string, payload: ComorbiditiesAssessmentCreate) => this.#comorbiditiesService.updateComorbiditiesAssessment({comorbiditiesAssessmentId: id, comorbiditiesAssessmentCreate: payload});

  // Reactive form definition
  override form: FormGroup = this.#formBuilder.group({
    date: [Validators.required],
    indexCondition: [Validators.required],
    panel: [],
    presentConditions: [],
    absentConditions: [],
  })

  // Effect to initialize form data when input changes
  readonly #initializeFormEffect = effect(() => this.initializeFormData(this.initialData()));

  // Signal to track the selected panel name from form changes
  #selectedPanelName = toSignal(this.form.controls['panel'].valueChanges, { initialValue: this.initialData()?.panel })

  // Resource to load comorbidity panels based on selected panel name
  #selectedPanel = rxResource({
    request: () => ({panel: this.#selectedPanelName()}),
    loader: ({request}) => this.#comorbiditiesService.getComorbiditiesPanelsByName(request)
  })

  // Effect to reset condition selections when the selected panel name changes
  readonly #resetPanelConditions = effect( () => {
    this.#selectedPanelName()
    this.form.get('presentConditions')?.setValue(null)
    this.form.get('absentConditions')?.setValue(null)
  })

  // Computed property transforming panel categories into a UI-friendly structure
  public panelForm = computed( () => (this.#selectedPanel.value()?.categories || []).map((category) => {
    const initialCondition = this.initialData()?.presentConditions?.find((condition: CodedConcept) => category.conditions.map(cond=>cond.code).includes(condition.code));
    return {
        label: category.label,
        checked: this.initialData ? category.conditions.some((condition) => this.initialData()?.presentConditions?.map((cond: any)=>cond.code).includes(condition.code)) : false,
        selected: initialCondition || category.default,
        conditions: category.conditions,
    };
  }));

  // Resource to load related neoplastic entities for a case
  public relatedEntities = rxResource({
    request: () => ({caseId: this.caseId(), limit: 100}),
    loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(data => data.items)),
  }); 
  
  // Radio button options for panel choices
  public comorbiditiesAssessmentPanelChoices: RadioChoice[] = [
      {name: 'No panel', value: null},
      {name: 'Charlson', value: ComorbiditiesAssessmentPanelChoices.Charlson},
      {name: 'NCI', value: ComorbiditiesAssessmentPanelChoices.Nci},
      {name: 'Elixhauser', value: ComorbiditiesAssessmentPanelChoices.Elixhauser},
  ]

  // Populate form controls with initial data
  initializeFormData(data: ComorbiditiesAssessment | undefined) {
    this.form.patchValue({
      date: data?.date,
      indexCondition: data?.indexConditionId,
      panel: data?.panel,
      presentConditions: data?.presentConditions,
      absentConditions: data?.absentConditions,
    })
  }

  // Transform panel form selections into a payload for API submission
  comorbiditiesPanelToPayload() {
    const presentConditions: CodedConcept[] = [];
    const absentConditions: CodedConcept[] = [];
    // Return null if no panel categories exist
    if (!this.panelForm()?.length) return null;
    // Iterate over each category and assign selected conditions to present/absent
    this.panelForm().forEach(
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

  // Build the final API payload based on form data and selected panel state
  constructAPIPayload(data: any): ComorbiditiesAssessmentCreate {    
    const panelData = this.comorbiditiesPanelToPayload()
    return {
      caseId: this.caseId(),
      indexConditionId: data.indexCondition,
      date: data.date,
      panel: data.panel,
      // Use panel form state if present; fallback to form control values
      presentConditions: panelData ? panelData.present : data.presentConditions,
      absentConditions: panelData ? panelData.absent : data.absentConditions,
    };
  }
}