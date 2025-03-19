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
import { DividerModule } from 'primeng/divider';

// Project dependencies
import { Cohort, CohortsService} from 'src/app/shared/openapi';
import { ModalFormComponent } from 'src/app/shared/components/modal-form/modal-form.component';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';

import { CohortSearchItemComponent } from './components/cohort-search-item/cohort-search-item.component';
import { CohortFormComponent } from 'src/app/features/case-forms/cohort-form/cohort-form.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';

@Component({
  standalone: true,
  templateUrl: './cohort-search.component.html',
  styles: `
  .p-dataview .p-dataview-content{
    background: none !important;
  }`,
  encapsulation: ViewEncapsulation.None,
  imports: [
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
    DividerModule,
    CohortSearchItemComponent,
  ],
})

export class CohortSearchComponent implements OnInit {
  
  // Injected services  
  public authService = inject(AuthService)
  private cohortsService = inject(CohortsService)
  private modalFormService = inject(ModalFormService)
  private messageService = inject(MessageService) 


  @Input() public currentUser: string | undefined;

  // Pagination settings
  public pageSizeChoices: number[] = [15, 30, 45, 60];
  public pageSize: number = this.pageSizeChoices[0];
  public totalCohorts: number = 0;
  public currentOffset: number = 0;
  public loadingCohorts: boolean = true;
  public searchQuery: string = "";

  // Observables
  public cohorts$!: Observable<Cohort[]> 

  ngOnInit() {
    this.refreshCohorts();
  }

  refreshCohorts() {
    this.loadingCohorts=true;
    this.cohorts$ = this.cohortsService
    .getCohorts({createdBy: this.currentUser, limit: this.pageSize, offset: this.currentOffset})
    .pipe(
      map(page => {
        this.loadingCohorts=false;
        this.totalCohorts = page.count;
        return page.items
      }),
      first(),
      catchError(error => {
        // Report any problems
        this.messageService.add({ severity: 'error', summary: 'Error loading cohorts', detail: error.error.detail });
        return of(error)
      })
    )
   }

   setPaginationAndRefresh(event: any) {
      this.currentOffset = event.first;
      this.pageSize = event.rows;
      this.refreshCohorts()
   }
   
  openNewCohortForm() {    
    this.modalFormService.open(CohortFormComponent, { /* optional data */ });
  }


  deleteCohort(id: string) {
    this.cohortsService.deleteCohortById({cohortId:id}).pipe(first()).subscribe({
        complete: () => {
            this.refreshCohorts()
            this.messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: id })
        },
        error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error deleting cohort', detail: error.error.detail })
    })
}

}