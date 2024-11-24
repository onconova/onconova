import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { CancerPatientService } from '../services/cancerpatient.service';
import { CancerPatientSchema, NinjaPaginationResponseSchemaCancerPatientSchema } from '../openapi';
import { Observable } from 'rxjs';
import { PatientFormComponent } from './components/patient-form/patient-form.component';

@Component({
  templateUrl: './patient-list.component.html',
})

export class PatientListComponent implements OnInit, OnDestroy {
  patients$!: Observable<NinjaPaginationResponseSchemaCancerPatientSchema>;
  filteredPatients: CancerPatientSchema[] = [];
  patients: CancerPatientSchema[] = [];
  filterValue: string = '';
  loading: boolean = true;
  subscription!: Subscription;
  patientFormVisible: boolean = false;

  constructor(private patientService: CancerPatientService) {}

  ngOnInit() {
    this.patients$ = this.patientService.getCancerPatients();
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
        patient.birthdate.toLowerCase().includes(filterValue.toLowerCase())
      );
    }
  };

  ngOnDestroy() {
    if (this.subscription) {
        this.subscription.unsubscribe();
    }
  };

  showDialog() {
    this.patientFormVisible = true;
}
}