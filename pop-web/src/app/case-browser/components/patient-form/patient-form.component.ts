import { Component, Output, EventEmitter } from '@angular/core';
import { PatientCaseCreateSchema, PatientCasesService, CodedConceptSchema } from '../../../core/modules/openapi/'
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import * as moment from 'moment';

@Component({
  selector: 'patient-form',
  templateUrl: './patient-form.component.html',
})
export class PatientFormComponent {

  form!: FormGroup;
  @Output() save = new EventEmitter<void>();

  loading: boolean = false

  ngOnInit() {
    this.form = new FormGroup({
    gender: new FormControl<CodedConceptSchema|null>(null,Validators.required),
    dateOfBirth: new FormControl<Date|null>(null, [
        Validators.required,
      ])
    });
  }

  constructor (
    private caseService: PatientCasesService,
    private messageService: MessageService ) { }
    
  onSave(): void {
    if (this.form.valid) {
      const data = this.form.value
      this.loading = true;  
      console.log(data.dateOfBirth)
      const cancerPatientData: PatientCaseCreateSchema = {
        gender: data.gender,
        dateOfBirth: moment(data.dateOfBirth, 'MM/YYYY').format('YYYY-MM-DD'),
      };
      this.caseService.createPatientCase(cancerPatientData).subscribe(
        (response) => {
          this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Saved patient: ' + response.id });
          this.loading = false;  
          this.save.emit();
        },
        (error) => {
          this.loading = false;  
          if (error.status == 401) {
              this.messageService.add({ severity: 'error', summary: 'Error', detail: 'The patient could not be saved' });
          }
        }
      )
    }
  }

}