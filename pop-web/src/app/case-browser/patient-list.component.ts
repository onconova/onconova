import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { CancerPatientService } from '../services/cancerpatient.service';
import { CancerPatientOut } from '../openapi';
import { Observable } from 'rxjs';

@Component({
  templateUrl: './patient-list.component.html',
})

export class PatientListComponent implements OnInit, OnDestroy {
  patients$!: Observable<CancerPatientOut[]>;
  filteredPatients: CancerPatientOut[] = [];
  patients: CancerPatientOut[] = [];
  filterValue: string = '';
  loading: boolean = true;
  subscription!: Subscription;

  constructor(private patientService: CancerPatientService) {}

  ngOnInit() {
    this.patients$ = this.patientService.getCancerPatients();
    this.patients$.subscribe(patients => {
      this.patients = patients;
      this.filteredPatients = patients;
      this.loading = false;
    });
  }
  
  filterPatients(filterValue: string): void {
    if (!filterValue) {
      this.filteredPatients = this.patients;
    } else {
      this.filteredPatients = this.patients.filter(patient =>
        patient.pseudoidentifier.toLowerCase().includes(filterValue.toLowerCase()) ||
        patient.birthdate.toLowerCase().includes(filterValue.toLowerCase())
      );
    }
  };

  ngOnDestroy() {
    if (this.subscription) {
        this.subscription.unsubscribe();
    }
  };
}