import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import * as moment from 'moment'; 

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
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent 
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { EmptyObject } from 'chart.js/dist/types/basic';

type MorphologicalBehaviors = '/3' | '/6' | '/1';

@Component({
  standalone: true,
  selector: 'neoplastic-entity-form',
  templateUrl: './neoplastic-entity-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    Select,
    ButtonModule,
    CodedConceptSelectComponent,
    ControlErrorComponent,
  ],
})
export class NeoplasticEntityFormComponent extends AbstractFormBase implements OnInit{

  private readonly neoplasticEntitiesService = inject(NeoplasticEntitiesService)
  public readonly formBuilder = inject(FormBuilder)

  public readonly createService = this.neoplasticEntitiesService.createNeoplasticEntity.bind(this.neoplasticEntitiesService)
  public readonly updateService = this.neoplasticEntitiesService.updateNeoplasticEntityById.bind(this.neoplasticEntitiesService)


  public readonly title: string = 'Neoplastic Entity'
  public readonly subtitle: string = 'Add new neoplastic entity'
  public readonly icon = Ribbon;

  private caseId!: string;
  public initialData: NeoplasticEntity | EmptyObject = {};
  public requiresPrimary!: boolean;
  public morphologyCodeFilter: MorphologicalBehaviors = '/3';
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
    this.onNeoplastiCRelationshipChange(this.initialData?.relationship)
    this.requiresPrimary = ['metastatic', 'local_recurrence', 'regional_recurrence'].includes(this.initialData?.relationship)
    // Subscribe to changes in the neoplastic relationship form control 
    this.form.get('relationship')?.valueChanges.subscribe(relationship => {
      this.onNeoplastiCRelationshipChange(relationship)
    })
  }

  constructForm() {
    this.form = this.formBuilder.group({
        relationship: [this.initialData?.relationship || 'primary',Validators.required],
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
      assertionDate: moment(data.assertionDate, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
      morphology: data.morphology,
      laterality: data.laterality,
      differentitation: data.differentiation,
    };
  }

  private onNeoplastiCRelationshipChange(relationship: string): void {
    // Update base filter for morphology codes     
    if (relationship === NeoplasticEntityRelationshipChoices.Metastatic) {
      this.morphologyCodeFilter = '/6'
    } else {
      this.morphologyCodeFilter = '/3'
    }  
    this.requiresPrimary = relationship !== NeoplasticEntityRelationshipChoices.Primary

    const relatedPrimary = this.form.get('relatedPrimary')
    if (relationship === NeoplasticEntityRelationshipChoices.Primary) {
      relatedPrimary?.removeValidators(Validators.required);
    } else {
      relatedPrimary?.addValidators(Validators.required);
    }  
    relatedPrimary?.updateValueAndValidity();
  };

  private getRelatedPrimaries() {
    this.neoplasticEntitiesService.getNeoplasticEntities(this.caseId, [NeoplasticEntityRelationshipChoices.Primary]).subscribe(
      (response) => {
          this.relatedPrimaries = response.items
      }
    )
  }

}