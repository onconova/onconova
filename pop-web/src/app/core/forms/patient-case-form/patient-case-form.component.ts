import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PatientCaseCreate, PatientCasesService, CodedConceptSchema } from '../../modules/openapi'
import { FormsModule, ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';

import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { Fluid } from 'primeng/fluid';

import * as moment from 'moment';

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent 
} from '../components';

import { User } from 'lucide-angular';

@Component({
  standalone: true,
  selector: 'patient-form',
  templateUrl: './patient-case-form.component.html',
  imports: [
    CommonModule,
    FormsModule, 
    ReactiveFormsModule,
    CodedConceptSelectComponent,
    MaskedCalendarComponent,
    ControlErrorComponent,
    ButtonModule,
    ToggleSwitch,
    Fluid,
  ]
})
export class PatientFormComponent implements OnInit {

  form!: FormGroup;
  @Output() save = new EventEmitter<void>();

  loading: boolean = false;
  title: string = 'Accesionning'
  subtitle: string = 'Add new patient case'
  readonly icon = User;

  ngOnInit() {
    this.constructForm()
    this.onIsAliveChange()
  }

  private constructForm() {
    this.form = new FormGroup({
      gender: new FormControl<CodedConceptSchema|null>(null,Validators.required),
      dateOfBirth: new FormControl<Date|null>(null,Validators.required),
      isAlive: new FormControl<boolean>(true,Validators.required),
      dateOfDeath: new FormControl<Date|null>(null, []),
      causeOfDeath: new FormControl<CodedConceptSchema|null>(null),
    });
  }

  private onIsAliveChange(): void {
    this.form.get('isAlive')?.valueChanges.subscribe(isAlive => {
      const dateOfDeathControl = this.form.get('dateOfDeath');
      const causeOfDeathControl = this.form.get('causeOfDeath');
      const requiredValidator = [Validators.required];
  
      if (isAlive) {
        dateOfDeathControl?.removeValidators(requiredValidator);
        causeOfDeathControl?.removeValidators(requiredValidator);
      } else {
        dateOfDeathControl?.addValidators(requiredValidator);
        causeOfDeathControl?.addValidators(requiredValidator);
      }  
      dateOfDeathControl?.updateValueAndValidity();
      causeOfDeathControl?.updateValueAndValidity();
    });
  }

  constructor (
    private caseService: PatientCasesService,
    private messageService: MessageService ) { }
    
  onSave(): void {
    if (this.form.valid) {
      this.loading = true;  
      // Prepare the data according to the API scheme
      const data = this.form.value
      const cancerPatientData: PatientCaseCreate = {
        gender: data.gender,
        dateOfBirth: moment(data.dateOfBirth, 'MM/YYYY').format('YYYY-MM-DD'),
        dateOfDeath: !data.isAlive?  moment(data.dateOfDeath, 'MM/YYYY').format('YYYY-MM-DD'): null,
        causeOfDeath: !data.isAlive? data.causeOfDeath: null,
      };
      // Send the data to the server's API
      this.caseService.createPatientCase(cancerPatientData).subscribe(
        (response) => {
          // Report the successful creation of the resource
          this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Saved patient: ' + response.id });
          this.loading = false;  
          this.save.emit();
        },
        (error) => {
          // Report any problems
          this.loading = false;  
          this.messageService.add({ severity: 'error', summary: 'Error', detail: 'The patient could not be saved' });
        }
      )
    }
  }
  get f() {
    return this.form.controls;
  }
}