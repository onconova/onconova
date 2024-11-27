import { Component } from '@angular/core';
import { PatientCasesService } from '../../../openapi/api/cancer-patients.service'
import { PatientCaseCreateSchema } from '../../../openapi/model/cancer-patient-create-schema'
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { CodedConceptSchema } from '../../../openapi/model/coded-concept-schema'
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
    date_of_birth: new FormControl<Date|null>(null, [
        Validators.required,
      ])
  });

  constructor (
    private patientService: PatientCasesService,
    private messageService: MessageService ) { }

  createPatient(data: any): void {
    this.loading = true;  
    console.log(data.date_of_birth.toISOString().substring(0, 10))
    const cancerPatientData: PatientCaseCreateSchema = {
      gender: data.gender,
      date_of_birth: data.date_of_birth.toISOString().substring(0, 10),
    };
    this.patientService.createPatientCase(cancerPatientData).subscribe(
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