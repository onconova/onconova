import { Component, OnInit, OnDestroy, ViewChild, inject, ViewEncapsulation  } from '@angular/core';
import { Subscription } from 'rxjs';
import { PatientCaseService } from '../services/cancerpatient.service';
import { PatientCase, PatientCasesService, PaginatedPatientCase, PatientCasesServiceInterface} from '../core/modules/openapi';
import { Observable } from 'rxjs';
import { PatientFormComponent } from './components/patient-form/patient-form.component';
import { ModalFormComponent } from '../core/components/modal-form/modal-form.component';
import { ModalFormService } from '../core/components/modal-form/modal-form.service';
import { FormGroup } from '@angular/forms';
import { MessageService } from 'primeng/api';


@Component({
  templateUrl: './patient-list.component.html',
  styleUrl: './patient-list.component.css',
  encapsulation: ViewEncapsulation.None
})

export class PatientListComponent implements OnInit, OnDestroy {
  
  public cases!: PatientCase[];

  filteredPatients: PatientCase[] = [];
  patients: PatientCase[] = [];
  filterValue: string = '';
  loading: boolean = true;
  total: number = 0;
  ageRangeValues = [0,100];

  public pageSizeChoices: number[] = [10, 25, 50, 100];
  public pageSize: number = this.pageSizeChoices[0];
  public totalCases: number = 0;

  subscription!: Subscription;
  users: any = {};
  
  private patientCasesService = inject(PatientCasesService)
  private modalFormService = inject(ModalFormService)
  private messageService = inject(MessageService) 
  public readonly cases$: Observable<PaginatedPatientCase> = this.patientCasesService.getPatientCases();


  @ViewChild('modalComponent') modalComponent!: ModalFormComponent;
  formGroup!: FormGroup;

  public query = {
    ageLte:  100,
    ageGte:  0,
    pseudoidentifier: undefined,
    deceased: undefined, 
    gender: undefined,
    born: undefined,
    limit:  undefined,
    offset:  undefined,
  }

  ngOnInit() {
    this.getPatientList()
  }

  getPatientList(): void{
    this.patientCasesService.getPatientCases(...Object.values(this.query)).subscribe(
      (page) => {
      this.cases = page.items;
      this.filteredPatients = page.items;
      this.loading = false;
      this.total = page.count
    },
    (error) => {
      // Report any problems
      this.loading = false;  
      this.messageService.add({ severity: 'error', summary: 'Error loading cases', detail: error.message });
    });
  }

  getFilteredPatientList(): void{
    // this.patients$ = this.patientCasesService.getFilteredPatientCases(this.ageRangeValues[1], this.ageRangeValues[0]);
    // this.patients$.subscribe(page => {
    //   console.log(page.items[0])
    //   this.patients = page.items;
    //   this.filteredPatients = page.items;
    //   this.loading = false;
    //   this.total = page.items.length
    // });
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


  openModalForm() {    
    this.modalFormService.open(PatientFormComponent, { /* optional data */ });
  }
  ngOnDestroy() {
    if (this.subscription) {
        this.subscription.unsubscribe();
    }
  };

}