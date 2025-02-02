import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { Ribbon } from 'lucide-angular';

import { 
  NeoplasticEntity, 
  NeoplasticEntitiesService,
  NeoplasticEntityRelationshipChoices, 
  NeoplasticEntityCreate
} from '../../../shared/openapi'

import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { Fluid } from 'primeng/fluid';

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent 
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { EmptyObject } from 'chart.js/dist/types/basic';

@Component({
  standalone: true,
  selector: 'neoplastic-entity-form',
  templateUrl: './neoplastic-entity-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    DatePickerComponent,
    Fluid,
    Select,
    ButtonModule,
    ConceptSelectorComponent,
    FormControlErrorComponent,
  ],
})
export class NeoplasticEntityFormComponent extends AbstractFormBase implements OnInit{

  private readonly neoplasticEntitiesService = inject(NeoplasticEntitiesService)
  public readonly formBuilder = inject(FormBuilder)

    
  public readonly createService = (payload: NeoplasticEntityCreate) => this.neoplasticEntitiesService.createNeoplasticEntity({neoplasticEntityCreate: payload})
  public readonly updateService = (id: string, payload: NeoplasticEntityCreate) => this.neoplasticEntitiesService.updateNeoplasticEntityById({entityId: id, neoplasticEntityCreate: payload})


  public readonly title: string = 'Neoplastic Entity'
  public readonly subtitle: string = 'Add new neoplastic entity'
  public readonly icon = Ribbon;

  private caseId!: string;
  public initialData: any = {};
  public requiresPrimary!: boolean;
  public morphologyTerminology!: string;
  public relatedPrimaries!: NeoplasticEntity[];
  public relationshipOptions = [
    { name: 'Primary', code: NeoplasticEntityRelationshipChoices.Primary },
    { name: 'Metastatic', code: NeoplasticEntityRelationshipChoices.Metastatic },
    { name: 'Local recurrence', code: NeoplasticEntityRelationshipChoices.LocalRecurrence },
    { name: 'Regional recurrence', code: NeoplasticEntityRelationshipChoices.RegionalRecurrence },
  ]

  ngOnInit() {
    // Construct the form 
    this.constructForm()
    // Fetch any primary neoplastic entities that could be related to a new entry 
    this.getRelatedPrimaries()
    // Setup the dynamic fields of the form based on initial conditions
    this.onNeoplastiCRelationshipChange(this.form.value.relationship)
    this.requiresPrimary = ['metastatic', 'local_recurrence', 'regional_recurrence'].includes(this.initialData?.relationship)
    // Subscribe to changes in the neoplastic relationship form control 
    this.form.get('relationship')?.valueChanges.subscribe(relationship => {
      this.onNeoplastiCRelationshipChange(relationship)
    })
  }

  constructForm() {
    this.form = this.formBuilder.group({
        relationship: [this.initialData?.relationship || NeoplasticEntityRelationshipChoices.Primary, Validators.required],
        assertionDate: [this.initialData?.assertionDate, Validators.required],
        relatedPrimary: [this.initialData?.relatedPrimaryId, Validators.required],
        topography: [this.initialData?.topography,Validators.required],
        morphology: [this.initialData?.morphology,Validators.required],
        laterality: [this.initialData?.laterality],
        differentiation: [this.initialData?.differentitation],
    });
  }

  constructAPIPayload(data: any): NeoplasticEntityCreate {    
    return {
      caseId: this.caseId,
      relationship: data.relationship,
      topography: data.topography,
      relatedPrimaryId: data.relatedPrimary,
      assertionDate: data.assertionDate,
      morphology: data.morphology,
      laterality: data.laterality,
      differentitation: data.differentiation,
    };
  }

  private onNeoplastiCRelationshipChange(relationship: string): void {
    // Update base filter for morphology codes     
    if (relationship === NeoplasticEntityRelationshipChoices.Metastatic) {
      this.morphologyTerminology = 'CancerMorphologyMetastatic'
    } else {
      this.morphologyTerminology = 'CancerMorphologyPrimary'
    }  
    this.requiresPrimary = relationship !== NeoplasticEntityRelationshipChoices.Primary

    const relatedPrimary = this.form.get('relatedPrimary')
    if (relationship === NeoplasticEntityRelationshipChoices.Primary) {
      relatedPrimary?.removeValidators(Validators.required);
      console.log('relatedPrimary not required')
    } else {
      relatedPrimary?.addValidators(Validators.required);
    }  
    relatedPrimary?.updateValueAndValidity();
  };

  private getRelatedPrimaries() {
    this.neoplasticEntitiesService.getNeoplasticEntities({caseId: this.caseId, relationship: NeoplasticEntityRelationshipChoices.Primary}).subscribe(
      (response) => {
          this.relatedPrimaries = response.items
      }
    )
  }

}