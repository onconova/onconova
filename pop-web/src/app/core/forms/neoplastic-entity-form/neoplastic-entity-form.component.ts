import { Component, Output, EventEmitter, inject, Input } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { InputMaskModule } from 'primeng/inputmask';

import { CodedConceptSchema } from '../../modules/openapi'
import { NeoplasticEntity, NeoplasticEntityCreate, NeoplasticEntitiesService } from '../../modules/openapi'

import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';
import { MessageService } from 'primeng/api';
import { DatePipe } from '@angular/common';
import { Fluid } from 'primeng/fluid';

import { Ribbon } from 'lucide-angular';

import * as moment from 'moment'; 

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent 
} from '../../forms/components';

@Component({
  standalone: true,
  selector: 'neoplastic-entity-form',
  templateUrl: './neoplastic-entity-form.component.html',
  imports: [
    CommonModule,
    InputMaskModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    Select,
    ButtonModule,
    CodedConceptSelectComponent,
    ControlErrorComponent,
  ],
  providers: [
    DatePipe,
  ],
})
export class NeoplasticEntityFormComponent {

    form!: FormGroup;
    @Output() save = new EventEmitter<void>();

    loading: boolean = false;
    title: string = 'Neoplastic Entity'
    subtitle: string = 'Add new neoplastic entity'
    readonly icon = Ribbon;

    private initialData: NeoplasticEntity | any = {};
    private caseId!: string;
    public requiresPrimary!: boolean;
    public morphologyCodeFilter: string = '/3';
    private neoplasticEntitiesService = inject(NeoplasticEntitiesService)
    public relatedPrimaries!: NeoplasticEntity[];

    private messageService = inject(MessageService)
    private datePipe = inject(DatePipe)


    relationships = [
    { name: 'Primary', code: 'primary' },
    { name: 'Metastatic', code: 'metastatic' },
    { name: 'Local recurrence', code: 'local_recurrence' },
    { name: 'Regional recurrence', code: 'regional_recurrence' },
    ]
  ngOnInit() {
    this.constructForm()
    this.getRelatedPrimaries()
    this.onNeoplastiCRelationshipChange(this.initialData?.relationship)
    this.requiresPrimary = ['metastatic', 'local_recurrence', 'regional_recurrence'].includes(this.initialData?.relationship)
    // Subscribe to changes in the neoplastic relationship form control 
    this.form.get('relationship')?.valueChanges.subscribe(relationship => {
      this.onNeoplastiCRelationshipChange(relationship)
    })
  }

  private constructForm() {
    this.form = new FormGroup({
        relationship: new FormControl<string>(this.initialData?.relationship || 'primary',Validators.required),
        assertionDate: new FormControl<Date|null>(this.initialData?.assertionDate, Validators.required),
        relatedPrimary: new FormControl<string|null>(this.initialData?.relatedPrimary, Validators.required),
        topography: new FormControl<CodedConceptSchema|null>(this.initialData?.topography,Validators.required),
        morphology: new FormControl<CodedConceptSchema|null>(this.initialData?.morphology,Validators.required),
        laterality: new FormControl<CodedConceptSchema|null>(this.initialData?.laterality),
        differentiation: new FormControl<CodedConceptSchema|null>(this.initialData?.differentitation),
    });
  }


  private onNeoplastiCRelationshipChange(relationship: string): void {
    // Update base filter for morphology codes     
    if (relationship === 'metastatic') {
      this.morphologyCodeFilter = '/6'
    } else {
      this.morphologyCodeFilter = '/3'
    }  
    this.requiresPrimary = relationship !== 'primary'

    const relatedPrimary = this.form.get('relatedPrimary')
    if (relationship !== 'metastatic') {
      relatedPrimary?.removeValidators(Validators.required);
    } else {
      relatedPrimary?.addValidators(Validators.required);
    }  
    relatedPrimary?.updateValueAndValidity();
  };

  getRelatedPrimaries() {
    this.neoplasticEntitiesService.getNeoplasticEntities(this.caseId, ["primary"]).subscribe(
      (response) => {
          this.relatedPrimaries = response.items
      }
    )
  }


  onSave(): void {
    if (this.form.valid) {
      this.loading = true;  
      // Prepare the data according to the API scheme
      const data = this.form.value
      const payload: NeoplasticEntityCreate = {
        caseId: this.caseId,
        relationship: data.relationship,
        topography: data.topography,
        relatedPrimaryId: data.relatedPrimary,
        assertionDate: moment(data.assertionDate, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
        morphology: data.morphology,
        laterality: data.laterality,
        differentitation: data.differentiation,
      };
      console.log(payload)
      // Send the data to the server's API
      if (this.initialData.id) {
        this.neoplasticEntitiesService.updateNeoplasticEntityById(this.initialData.id, payload).subscribe(
          (response) => {
            // Report the successful creation of the resource
            this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Updated ' + this.initialData.id });
            this.loading = false;  
            this.save.emit();
          },
          (error) => {
            // Report any problems
            this.loading = false;  
            this.messageService.add({ severity: 'error', summary: 'Error ocurred while updating', detail: error.message });
          }
        )
  
      } else {
        this.neoplasticEntitiesService.createNeoplasticEntity(payload).subscribe(
          (response) => {
            // Report the successful creation of the resource
            this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Saved '+ this.title.toLowerCase() + response.id });
            this.loading = false;  
            this.save.emit();
          },
          (error) => {
            // Report any problems
            this.loading = false;  
            this.messageService.add({ severity: 'error', summary: 'Error ocurred while saving', detail: error.message });
          }
        )  
      }
    }
  }
}