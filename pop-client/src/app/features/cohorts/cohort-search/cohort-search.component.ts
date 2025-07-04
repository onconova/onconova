import { Component, inject, input, computed, signal, Resource, Signal  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { map, first, of, catchError, tap } from 'rxjs';

import { Users } from 'lucide-angular';

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
import { Cohort, CohortsService} from 'pop-api-client';
import { CohortSearchItemComponent } from './components/cohort-search-item/cohort-search-item.component';
import { CohortFormComponent } from 'src/app/features/forms/cohort-form/cohort-form.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormHeaderComponent } from '../../forms/modal-form-header.component';
import { rxResource } from '@angular/core/rxjs-interop';
import { Toolbar } from 'primeng/toolbar';
import { PopoverFilterButtonComponent } from 'src/app/shared/components/popover-filter-button/popover-filter-button.component';
import { NgxCountAnimationDirective } from 'ngx-count-animation';
import { driver } from 'driver.js';
import TourDriverConfig from './cohort-search.tour';
import { Select } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { SelectButton } from 'primeng/selectbutton';

@Component({
    templateUrl: './cohort-search.component.html',
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        TableModule,
        IconFieldModule,
        InputIconModule,
        InputTextModule,
        SelectButton,
        ButtonModule,
        DataViewModule,
        SkeletonModule,
        Select,
        Toolbar,
        NgxCountAnimationDirective,
        CohortSearchItemComponent,
    ]
})

export class CohortSearchComponent {
  
  // Injected services  
  readonly #cohortsService = inject(CohortsService);
  readonly #authService = inject(AuthService);
  readonly #messageService = inject(MessageService); 
  readonly #dialogservice = inject(DialogService);
  #modalFormRef: DynamicDialogRef | undefined;


  public readonly author = input<string>();
  public readonly isUserPage = computed(() => this.author() !== undefined);
  public readonly currentUser = computed(() => this.#authService.user());

  // Pagination settings
  public readonly pageSizeChoices: number[] = [15, 30, 45];
  public pagination = signal({limit: this.pageSizeChoices[0], offset: 0});
  public layout: Signal<'grid' | 'list'> = signal('grid');
  public totalCohorts= signal(0);
  public searchQuery = signal('');
  protected orderingFields = [
      {label: 'Creation date', value: 'createdAt'},
      {label: 'Last Updated', value: 'updatedAt'},
      {label: 'Title', value: 'name'},
      {label: 'Population', value: 'population'},
  ]
  protected orederingDirections = [
      {label: 'Descending', value: '-'},
      {label: 'Ascending', value: ''},
  ]
  protected orderingField = signal<string>(this.orderingFields[0].value)
  protected orderingDirection = signal<string>(this.orederingDirections[0].value)
  protected ordering = computed(() => this.orderingDirection() + this.orderingField()) 

  // Resources
  public cohorts: Resource<Cohort[] | undefined> = rxResource({
    request: () => ({
      createdBy: this.author(), 
      limit: this.pagination().limit, 
      offset: this.pagination().offset, 
      nameContains: this.searchQuery() || undefined,
      ordering: this.ordering() || '-createdAt',
    }),
    loader: ({request}) => this.#cohortsService.getCohorts(request).pipe(
      tap(page => this.totalCohorts.set(page.count)),
      map(page => page.items),
      catchError((error: any) => {
        this.#messageService.add({ severity: 'error', summary: 'Error loading cohorts', detail: error?.error?.detail });
        return of([] as Cohort[]) 
      })
    )
  })
  protected tour = TourDriverConfig;

  openNewCohortForm() {    
      this.#modalFormRef = this.#dialogservice.open(CohortFormComponent, {
        data: {
            title: 'Cohort registration',
            subtitle: 'Add a new cohort',
            icon: Users,
        },
        templates: {
            header: ModalFormHeaderComponent,
        },   
        modal: true,
        closable: true,
        width: '45vw',
        styleClass: 'pop-modal-form',
        breakpoints: {
            '1700px': '50vw',
            '960px': '75vw',
            '640px': '90vw'
        },
      })
      this.reloadDataIfClosedAndSaved(this.#modalFormRef)
  }


  reloadDataIfClosedAndSaved(modalFormRef: DynamicDialogRef) {
    modalFormRef.onClose.subscribe((data: any) => {
        if (data?.saved) {
            this.cohorts.reload()
        }
      })    
  }
  
  startTour() {
      driver(this.tour).drive()    
  }

}