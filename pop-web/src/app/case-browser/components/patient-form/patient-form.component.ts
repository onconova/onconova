import { Component } from '@angular/core';
import { PatientCaseCreateSchema, PatientCasesService, CodedConceptSchema } from '../../../core/modules/openapi/'
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'patient-form',
  templateUrl: './patient-form.component.html',
  providers: [MessageService]
})
export class PatientFormComponent {

  loading: boolean = false

  patientForm = new FormGroup({
    gender: new FormControl<CodedConceptSchema|null>(null,Validators.required),
    dateOfBirth: new FormControl<Date|null>(null, [
        Validators.required,
      ])
  });

  constructor (
    private caseService: PatientCasesService,
    private messageService: MessageService ) { }

  createPatient(data: any): void {
    this.loading = true;  
    console.log(data.dateOfBirth.toISOString().substring(0, 10))
    const cancerPatientData: PatientCaseCreateSchema = {
      gender: data.gender,
      dateOfBirth: data.dateOfBirth.toISOString().substring(0, 10),
    };
    this.caseService.createPatientCase(cancerPatientData).subscribe(
      (response) => {
        this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Saved patient' + response.id });
        this.loading = false;  
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