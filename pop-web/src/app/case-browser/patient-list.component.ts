import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { Subscription } from 'rxjs';
import { CancerPatientService } from '../services/cancerpatient.service';
import { CancerPatientSchema, NinjaPaginationResponseSchemaCancerPatientSchema } from '../openapi';
import { Observable } from 'rxjs';
import { ModalFormComponent } from '../core/components/modal-form/modal-form.component';
import { FormGroup } from '@angular/forms';

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

  @ViewChild('modalComponent') modalComponent!: ModalFormComponent;
  formGroup!: FormGroup;


  constructor(private patientService: CancerPatientService,
  ) {}

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


  openModal() {
    this.modalComponent.openModal();
  }
  ngOnDestroy() {
    if (this.subscription) {
        this.subscription.unsubscribe();
    }
  };

}