import { Component, OnInit, inject, Input, ViewEncapsulation  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { map, first, of, Observable, catchError } from 'rxjs';

// PrimeNG dependencies
import { MessageService } from 'primeng/api';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { DataViewModule } from 'primeng/dataview';
import { SkeletonModule } from 'primeng/skeleton';

// Project dependencies
import { PatientCase, PatientCasesService} from 'src/app/shared/openapi';
import { CaseBrowserCardComponent } from './components/case-card/case-browser-item.component';
import { PatientFormComponent } from 'src/app/core/forms';
import { ModalFormComponent } from 'src/app/shared/components/modal-form/modal-form.component';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';


@Component({
  standalone: true,
  templateUrl: './case-browser.component.html',
  styleUrl: './case-browser.component.css',
  encapsulation: ViewEncapsulation.None,
  imports: [
    CaseBrowserCardComponent,
    ModalFormComponent,
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    IconFieldModule,
    InputIconModule,
    InputTextModule,
    ButtonModule,
    DataViewModule,
    SkeletonModule,
  ],
})

export class CaseBrowserComponent implements OnInit {
  
  // Injected services  
  private patientCasesService = inject(PatientCasesService)
  private modalFormService = inject(ModalFormService)
  private messageService = inject(MessageService) 


  @Input() public manager: string | undefined;

  // Pagination settings
  public pageSizeChoices: number[] = [10, 25, 50, 100];
  public pageSize: number = this.pageSizeChoices[0];
  public totalCases: number = 0;

  // Observables
  public cases$!: Observable<PatientCase[]> 

/**
 * Initializes the component by refreshing the list of patient cases.
 */
  ngOnInit() {
    this.refreshCases();
  }

/**
 * Refreshes the list of patient cases.
 *
 * This method fetches patient cases from the PatientCaseService and updates
 * the `cases$` observable with the resulting list of cases. It maps the
 * paginated response to extract the case items and handles any errors that
 * occur during the fetch process by displaying an error message using the
 * MessageService.
 */
  refreshCases() {
    console.log('this.filterByUsername',this.manager)
    this.cases$ = this.patientCasesService
    .getPatientCases(undefined, undefined, undefined, this.manager)
    .pipe(
      map(page => page.items),
      first(),
      catchError(error => {
        // Report any problems
        this.messageService.add({ severity: 'error', summary: 'Error loading cases', detail: error.message });
        return of(error)
      })
    )
   }


  /**
   * Opens a modal form for creating a new patient case.
   *
   * When the user clicks the "New Case" button, this method is called. It
   * opens a modal form using the ModalFormService, passing in the
   * PatientFormComponent as the form component to display, and an empty
   * object as the data to pass to the form.
   */
  openNewCaseForm() {    
    this.modalFormService.open(PatientFormComponent, { /* optional data */ });
  }

}