import {Component, inject} from '@angular/core';
import {FormBuilder} from '@angular/forms';

@Component({
  selector: 'patient-form',
  templateUrl: './patient-form.component.html',
})
export class PatientFormComponent {

  private formBuilder = inject(FormBuilder);
  patientForm = this.formBuilder.group({
    'gender': [''],
    'birthdate': [''],
  });
}