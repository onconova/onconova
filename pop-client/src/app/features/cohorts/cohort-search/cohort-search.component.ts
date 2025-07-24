import { Component, inject, input, computed, signal, Resource, Signal, linkedSignal, effect  } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { map, of, catchError, tap } from 'rxjs';

import { Users } from 'lucide-angular';

import { MessageService } from 'primeng/api';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { DataViewModule } from 'primeng/dataview';
import { SkeletonModule } from 'primeng/skeleton';

import { Cohort, CohortsService} from 'pop-api-client';
import { CohortSearchItemComponent } from './components/cohort-search-item/cohort-search-item.component';
import { CohortFormComponent } from 'src/app/features/forms/cohort-form/cohort-form.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormHeaderComponent } from '../../forms/modal-form-header.component';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { Toolbar } from 'primeng/toolbar';
import { NgxCountAnimationDirective } from 'ngx-count-animation';
import { driver } from 'driver.js';
import TourDriverConfig from './cohort-search.tour';
import { Select } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { SelectButton } from 'primeng/selectbutton';
import { ActivatedRoute, Router } from '@angular/router';

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
  readonly #activatedRoute = inject(ActivatedRoute);
  readonly #router = inject(Router);
  readonly #location = inject(Location);
  #modalFormRef: DynamicDialogRef | undefined;

  // Query parameters
  readonly #inputQueryParams = toSignal(this.#activatedRoute.queryParams);
  protected readonly queryParams = {
      sort:  linkedSignal(() => this.#inputQueryParams()?.['sort'] || '-createdAt'),
      limit: linkedSignal(() => this.#inputQueryParams()?.['limit'] || this.pageSizeChoices[0]),
      offset:  linkedSignal(() => this.#inputQueryParams()?.['offset'] || 0),
      layout:  linkedSignal(() => this.#inputQueryParams()?.['layout'] || 'grid'),
      title:  linkedSignal(() => this.#inputQueryParams()?.['title']) || undefined,
  }


  public readonly contributor = input<string>();
  public readonly isUserPage = computed(() => this.contributor() !== undefined);
  public readonly currentUser = computed(() => this.#authService.user());

  // Pagination settings
  public readonly pageSizeChoices: number[] = [15, 30, 45];
  public totalCohorts= signal(0);
  protected orderingChoices = [
        {label: 'Newest', value: '-createdAt'},
        {label: 'Oldest', value: 'createdAt'},
        {label: 'Newest updates', value: '-updatedAt'},
        {label: 'Oldest updates', value: 'updatedAt'},
        {label: 'Population - Largest', value: '-population'},
        {label: 'Population - Smallest', value: 'population'},
        {label: 'Cohort title - A to Z', value: '-title'},
        {label: 'Cohort title - Z to A', value: 'title'},
  ]
  // Resources
  public cohorts: Resource<Cohort[] | undefined> = rxResource({
    request: () => ({
      createdBy: this.contributor(), 
      limit: this.queryParams.limit(), 
      offset: this.queryParams.offset(), 
      nameContains: this.queryParams.title() || undefined,
      ordering: this.queryParams.sort(),
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

  #updateRouteParameters = effect(() => {
      const urlTree = this.#router.createUrlTree([], {
      relativeTo: this.#activatedRoute,
      queryParams: {
          title: this.queryParams.title() || undefined,
          sort: this.queryParams.sort() !== '-createdAt' ? this.queryParams.sort() : undefined,
          limit: this.queryParams.limit() !== this.pageSizeChoices[0] ? this.queryParams.sort() : undefined,
          layout: this.queryParams.layout() !== 'grid' ? this.queryParams.layout() : undefined,
          offset: this.queryParams.offset() || undefined,
      },
      queryParamsHandling: 'merge',
      });
      //Update route with Query Params
      this.#location.go(urlTree.toString());
  })
  
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