import { Component, Output, EventEmitter, inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { InputMaskModule } from 'primeng/inputmask';

import { CodedConceptSchema } from '../../modules/openapi'
import { NeoplasticEntity, NeoplasticEntityCreate, NeoplasticEntitiesService } from '../../modules/openapi'
import { CodedConceptSelectComponent } from '../../components/coded-concept-select/coded-concept-select.component';
import { ControlErrorComponent } from '../../components/control-error/control-error.component';
import { DateMaskDirective } from '../../components/directives/date-mask-directive';

import { CalendarModule } from 'primeng/calendar';
import { DropdownModule } from 'primeng/dropdown';
import { MessageService } from 'primeng/api';
import { DatePipe } from '@angular/common';

import { Ribbon } from 'lucide-angular';


@Component({
  selector: 'neoplastic-entity-form',
  templateUrl: './neoplastic-entity-form.component.html',
  imports: [
    CommonModule,
    InputMaskModule,
    ReactiveFormsModule,
    FormsModule,
    CalendarModule,
    DropdownModule,
    CodedConceptSelectComponent,
    ControlErrorComponent,
    DateMaskDirective,
  ],
  providers: [
    DatePipe,
  ],
  standalone: true,
})
export class NeoplasticEntityFormComponent {

    form!: FormGroup;
    @Output() save = new EventEmitter<void>();

    loading: boolean = false;
    title: string = 'Neoplastic Entity'
    subtitle: string = 'Add new neoplastic entity'
    readonly icon = Ribbon;

    private caseId!: string;
    public requiresPrimary: boolean = false;
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
    this.onNeoplastiCRelationshipChange()
    this.getRelatedPrimaries()
  }

  private constructForm() {
    this.form = new FormGroup({
        relationship: new FormControl<string>('primary',Validators.required),
        assertionDate: new FormControl<Date|null>(null, Validators.required),
        relatedPrimary: new FormControl<string|null>(null, Validators.required),
        topography: new FormControl<CodedConceptSchema|null>(null,Validators.required),
        morphology: new FormControl<CodedConceptSchema|null>(null,Validators.required),
    });
  }


  private onNeoplastiCRelationshipChange(): void {
    // Subscribe to changes in the neoplastic relationship form control 
    this.form.get('relationship')?.valueChanges.subscribe(relationship => {
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
    });
  }

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
        assertionDate: this.datePipe.transform(data.assertionDate, 'yyyy-MM-dd') || data.assertionDate,
        morphology: data.morphology,
      };
      // Send the data to the server's API
      this.neoplasticEntitiesService.createNeoplasticEntity(payload).subscribe(
        (response) => {
          // Report the successful creation of the resource
          this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Saved: '+ this.title.toLowerCase() + response.id });
          this.loading = false;  
          this.save.emit();
        },
        (error) => {
          // Report any problems
          this.loading = false;  
          this.messageService.add({ severity: 'error', summary: 'Error ocurred during saving', detail: error.message });
        }
      )
    }
  }
}