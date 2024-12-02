import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { Subscription } from 'rxjs';
import { PatientCaseService } from '../services/cancerpatient.service';
import { PatientCase, PaginatedPatientCase } from '../core/modules/openapi';
import { Observable } from 'rxjs';
import { PatientFormComponent } from './components/patient-form/patient-form.component';
import { ModalFormComponent } from '../core/components/modal-form/modal-form.component';
import { ModalFormService } from '../core/components/modal-form/modal-form.service';
import { FormGroup } from '@angular/forms';
import { AuthService } from '../core/modules/openapi'

@Component({
  templateUrl: './patient-list.component.html',
})

export class PatientListComponent implements OnInit, OnDestroy {
  patients$!: Observable<PaginatedPatientCase>;
  filteredPatients: PatientCase[] = [];
  patients: PatientCase[] = [];
  filterValue: string = '';
  loading: boolean = true;
  total: number = 0;
  ageRangeValues = [0,100];
  subscription!: Subscription;
  users: any = {};
  
  @ViewChild('modalComponent') modalComponent!: ModalFormComponent;
  formGroup!: FormGroup;


  constructor(private patientService: PatientCaseService, private modalFormService: ModalFormService, private authService: AuthService
  ) {}

  ngOnInit() {
    this.getPatientList()
  }

  getPatientList(): void{
    this.patients$ = this.patientService.getPatientCases();
    this.patients$.subscribe(page => {
      console.log(page.items[0])
      this.patients = page.items;
      this.filteredPatients = page.items;
      this.loading = false;
      this.total = page.items.length
    });
  }

  getFilteredPatientList(): void{
    this.patients$ = this.patientService.getFilteredPatientCases(this.ageRangeValues[1], this.ageRangeValues[0]);
    this.patients$.subscribe(page => {
      console.log(page.items[0])
      this.patients = page.items;
      this.filteredPatients = page.items;
      this.loading = false;
      this.total = page.items.length
    });
  }
  filterPatients(filterValue: string): void {
    if (!filterValue) {
      this.filteredPatients = this.patients;
    } else {
      this.filteredPatients = this.patients.filter(patient =>
        patient.pseudoidentifier.toLowerCase().includes(filterValue.toLowerCase()) ||
        patient.dateOfBirth.toLowerCase().includes(filterValue.toLowerCase())
      );
    }
  };

  getUser(userId: number) {
    this.authService.getUserById(userId).subscribe(user => {
      this.users[userId] = {
        initials: user.username[0].toUpperCase(),
        username: user.username,
      }
    })
    return '?'
  }

  openModalForm() {    
    this.modalFormService.open(PatientFormComponent, { /* optional data */ });
  }
  ngOnDestroy() {
    if (this.subscription) {
        this.subscription.unsubscribe();
    }
  };

}