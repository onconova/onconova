import { Component, computed, effect, inject, input } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
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
} from 'onconova-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  RadioChoice,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { SelectButton } from 'primeng/selectbutton';

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
        SelectButton,
        ToggleSwitchModule,
        ButtonModule,
        ConceptSelectorComponent,
        FormControlErrorComponent,
    ]
})
export class ComorbiditiesAssessmentFormComponent extends AbstractFormBase {

  // Input signal for initial data passed to the form
  initialData = input<ComorbiditiesAssessment>();

  // Service injections
  readonly #comorbiditiesService: ComorbiditiesAssessmentsService = inject(ComorbiditiesAssessmentsService);
  readonly #neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
  readonly #fb = inject(FormBuilder);

  // Create and update service methods for the form data
  readonly createService = (payload: ComorbiditiesAssessmentCreate) => this.#comorbiditiesService.createComorbiditiesAssessment({comorbiditiesAssessmentCreate: payload});
  readonly updateService = (id: string, payload: ComorbiditiesAssessmentCreate) => this.#comorbiditiesService.updateComorbiditiesAssessment({comorbiditiesAssessmentId: id, comorbiditiesAssessmentCreate: payload});

  // Reactive form definition
  public form = this.#fb.group({
    date: this.#fb.nonNullable.control<string | null>(null, Validators.required),
    indexCondition: this.#fb.control<string | null>(null, Validators.required),
    panel: this.#fb.control<ComorbiditiesAssessmentPanelChoices | null>(null),
    presentConditions: this.#fb.control<CodedConcept[]>([]),
    absentConditions: this.#fb.control<CodedConcept[]>([]),
  });

  readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;
  
    this.form.patchValue({
      date: data.date ?? null,
      indexCondition: data.indexConditionId ?? null,
      panel: data.panel ?? null,
      presentConditions: data.presentConditions ?? [],
      absentConditions: data.absentConditions ?? [],
    });
  });

  // Build the final API payload based on form data and selected panel state
  payload = (): ComorbiditiesAssessmentCreate => {    
    const data = this.form.value;
    const panelData = this.comorbiditiesPanelToPayload()
    return {
      caseId: this.caseId(),
      indexConditionId: data.indexCondition!,
      date: data.date!,
      panel: data.panel || undefined,
      // Use panel form state if present; fallback to form control values
      presentConditions: (panelData ? panelData.present : data.presentConditions) ?? undefined,
      absentConditions: (panelData ? panelData.absent : data.absentConditions) ?? undefined,
    };
  }

  // Signal to track the selected panel name from form changes
  #selectedPanelName = toSignal(this.form.controls['panel'].valueChanges, { initialValue: this.initialData()?.panel! })

  // Resource to load comorbidity panels based on selected panel name
  #selectedPanel = rxResource({
    request: () => ({panel: this.#selectedPanelName()!}),
    loader: ({request}) => this.#comorbiditiesService.getComorbiditiesPanelsByName(request)
  })

  // Effect to reset condition selections when the selected panel name changes
  readonly #resetPanelConditions = effect( () => {
    if (this.#selectedPanelName()) {
      this.form.get('presentConditions')!.setValue(null)
      this.form.get('absentConditions')!.setValue(null)  
    }
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
    request: () => ({caseId: this.caseId()}),
    loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(data => data.items)),
  }); 
  
  // Radio button options for panel choices
  public comorbiditiesAssessmentPanelChoices: RadioChoice[] = [
      {name: 'No panel', value: null},
      {name: 'Charlson', value: ComorbiditiesAssessmentPanelChoices.Charlson},
      {name: 'NCI', value: ComorbiditiesAssessmentPanelChoices.Nci},
      {name: 'Elixhauser', value: ComorbiditiesAssessmentPanelChoices.Elixhauser},
  ]

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

}