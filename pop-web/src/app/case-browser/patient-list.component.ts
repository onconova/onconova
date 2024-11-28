import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { Subscription } from 'rxjs';
import { PatientCaseService } from '../services/cancerpatient.service';
import { PatientCaseSchema, NinjaPaginationResponseSchemaPatientCaseSchema } from '../core/modules/openapi';
import { Observable } from 'rxjs';
import { ModalFormComponent } from '../core/components/modal-form/modal-form.component';
import { FormGroup } from '@angular/forms';

@Component({
  templateUrl: './patient-list.component.html',
})

export class PatientListComponent implements OnInit, OnDestroy {
  patients$!: Observable<NinjaPaginationResponseSchemaPatientCaseSchema>;
  filteredPatients: PatientCaseSchema[] = [];
  patients: PatientCaseSchema[] = [];
  filterValue: string = '';
  loading: boolean = true;
  subscription!: Subscription;

  @ViewChild('modalComponent') modalComponent!: ModalFormComponent;
  formGroup!: FormGroup;


  constructor(private patientService: PatientCaseService,
  ) {}

  ngOnInit() {
    this.patients$ = this.patientService.getPatientCases();
    this.patients$.subscribe(page => {
      this.patients = page.items;
      this.filteredPatients = page.items;
      this.loading = false;
    });
  }
  
  filterPatients(filterValue: string): void {
    if (!filterValue) {
      this.filteredPatients = this.patients;
    } else {
      this.filteredPatients = this.patients.filter(patient =>
        patient.pseudoidentifier.toLowerCase().includes(filterValue.toLowerCase()) ||
        patient.date_of_birth.toLowerCase().includes(filterValue.toLowerCase())
      );
    }
  };


  openModal() {
    this.modalComponent.openModal();
  }
  ngOnDestroy() {
    if (this.subscription) {
        this.subscription.unsubscribe();
    }
  };

}