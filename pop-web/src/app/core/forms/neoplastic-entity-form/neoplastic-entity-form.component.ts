import { Component, Output, EventEmitter, inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { InputMaskModule } from 'primeng/inputmask';

import { CodedConceptSchema } from '../../modules/openapi'
import { NeoplasticEntityCreate, NeoplasticEntitiesService } from '../../modules/openapi'
import { CodedConceptSelectModule } from '../../components/coded-concept-select/coded-concept-select.module';
import { ControlErrorComponent } from '../../components/control-error/control-error.component';

import { CalendarModule } from 'primeng/calendar';
import { DropdownModule } from 'primeng/dropdown';
import { MessageService } from 'primeng/api';
import { DatePipe } from '@angular/common';

import { Ribbon } from 'lucide-angular';


@Component({
  selector: 'neoplastic-entity-form',
  templateUrl: './neoplastic-entity-form.component.html',
  imports: [
    InputMaskModule,
    ReactiveFormsModule,
    FormsModule,
    CalendarModule,
    DropdownModule,
    CodedConceptSelectModule,
    ControlErrorComponent,
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

    caseId!: string;

    private neoplasticEntitiesService = inject(NeoplasticEntitiesService)
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
    console.log('caseId', this.caseId)
  }

  private constructForm() {
    this.form = new FormGroup({
        relationship: new FormControl<string|null>(null,Validators.required),
        assertionDate: new FormControl<Date|null>(null, Validators.required),
        topography: new FormControl<CodedConceptSchema|null>(null,Validators.required),
        morphology: new FormControl<CodedConceptSchema|null>(null,Validators.required),
    });
  }


  onSave(): void {
    if (this.form.valid) {
      this.loading = true;  
      // Prepare the data according to the API scheme
      const data = this.form.value
      const payload: NeoplasticEntityCreate = {
        caseId: this.caseId,
        relationship: data.relationship.code,
        topography: data.topography,
        assertionDate: this.datePipe.transform(data.assertionDate, 'yyyy-MM-dd') || data.assertionDate,
        morphology: data.morphology,
      };
      console.log('POST', payload)
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