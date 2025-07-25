import { Component, inject, input, computed, signal, Resource, Signal, effect, linkedSignal, model  } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { map, of, catchError, tap } from 'rxjs';

import { NgxCountAnimationDirective } from "ngx-count-animation";
import { UserPlus } from 'lucide-angular';

// PrimeNG dependencies
import { MessageService } from 'primeng/api';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { DataViewModule } from 'primeng/dataview';
import { SkeletonModule } from 'primeng/skeleton';
import { DividerModule } from 'primeng/divider';
import { ToolbarModule } from 'primeng/toolbar';
import { OverlayBadgeModule } from 'primeng/overlaybadge';
import { PopoverModule } from 'primeng/popover';
import { SliderModule } from 'primeng/slider';

// Project dependencies
import { CodedConcept, GetPatientCasesRequestParams, PatientCase, PatientCasesService} from 'pop-api-client';
import { CaseSearchItemCardComponent } from './components/case-search-item/case-search-item.component';
import { PatientFormComponent } from 'src/app/features/forms';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormHeaderComponent } from '../../forms/modal-form-header.component';
import { ConceptSelectorComponent } from 'src/app/shared/components';
import { PopoverFilterButtonComponent } from 'src/app/shared/components/popover-filter-button/popover-filter-button.component';
import { SelectButton } from 'primeng/selectbutton';
import TourDriverConfig from './case-search.tour';
import { driver } from 'driver.js';
import { TableModule } from 'primeng/table';
import { SelectModule } from 'primeng/select';
import { ActivatedRoute, Router } from '@angular/router';


@Component({
  templateUrl: './case-search.component.html',
  imports: [
      CaseSearchItemCardComponent,
      NgxCountAnimationDirective,
      CommonModule,
      FormsModule,
      ReactiveFormsModule,
      IconFieldModule,
      ConceptSelectorComponent,
      OverlayBadgeModule,
      TableModule,
      InputIconModule,
      InputTextModule,
      SelectButton,
      PopoverModule,
      SelectModule,
      SliderModule,
      PopoverFilterButtonComponent,
      ButtonModule,
      DataViewModule,
      SkeletonModule,
      DividerModule,
      ToolbarModule,
  ],
  animations: [
      trigger('fadeAnimation', [
          state('void', style({ opacity: 0 })), // Initial state (not visible)
          transition(':enter', [animate('500ms ease-in')]), // Fade-in effect
          transition(':leave', [animate('500ms ease-out')]) // Fade-out effect
      ])
  ]
})

export class CaseSearchComponent {
  
  // Reactive input properties
  public readonly contributor = input<string>();
  
  // Injected services  
  readonly #patientCasesService = inject(PatientCasesService);
  readonly #authService = inject(AuthService);
  readonly #messageService = inject(MessageService) ;
  readonly #dialogservice = inject(DialogService);
  readonly #router = inject(Router);
  readonly #location = inject(Location);
  readonly #activatedRoute = inject(ActivatedRoute);
  #modalFormRef: DynamicDialogRef | undefined;

  // Computed properties
  public readonly isUserPage = computed(() => this.contributor() !== undefined);
  public readonly currentUser = computed(() => this.#authService.user());
  
  // Query parameters
  readonly #inputQueryParams = toSignal(this.#activatedRoute.queryParams);
  protected readonly queryParams = {
    sort:  linkedSignal(() => this.#inputQueryParams()?.['sort'] || '-createdAt'),
    limit: linkedSignal(() => this.#inputQueryParams()?.['limit'] || this.pageSizeChoices[0]),
    offset:  linkedSignal(() => this.#inputQueryParams()?.['offset'] || 0),
    gender:  linkedSignal(() => this.#inputQueryParams()?.['gender']),
    layout:  linkedSignal(() => this.#inputQueryParams()?.['layout'] || 'grid'),
    deceased:  linkedSignal(() => this.#inputQueryParams()?.['deceased']),
    age:  linkedSignal(() => {
      const age = this.#inputQueryParams()?.['age'];
      if (age && age.includes('-')) {
        return age.split('-')
      } return undefined
    }),
    dataCompletion:  linkedSignal(() => {
      const dataCompletion = this.#inputQueryParams()?.['age'];
      if (dataCompletion && dataCompletion.includes('-')) {
        return dataCompletion.split('-')
      } return undefined
    }),
    primarySite:  linkedSignal(() => this.#inputQueryParams()?.['primarySite']),
    morphology:  linkedSignal(() => this.#inputQueryParams()?.['morphology']),
    idSearch:  linkedSignal(() => this.#inputQueryParams()?.['idSearch']),
  }

  // Pagination and search settings
  public readonly pageSizeChoices: number[] = [15, 30, 45];
  public totalCases= signal(0);

  protected orderingOptions = [
    {label: 'Newest', value: '-createdAt'},
    {label: 'Oldest', value: 'createdAt'},
    {label: 'Newest updates', value: '-updatedAt'},
    {label: 'Oldest updates', value: 'updatedAt'},
    {label: 'Age - Oldest', value: '-age'},
    {label: 'Age - Youngest', value: 'age'},
    {label: 'Age at diagnosis - Oldest', value: '-ageAtDiagnosis'},
    {label: 'Age at diagnosis - Youngest', value: 'ageAtDiagnosis'},
    {label: 'Date of death - Newest', value: 'dateOfDeath'},
    {label: 'Date of death - Oldest', value: '-dateOfDeath'},
    {label: 'Completion rate - Highest', value: '-dataCompletionRate'},
    {label: 'Completion rate - Lowest', value: 'dataCompletionRate'},
    {label: 'Case ID - A to Z', value: '-pseudoidentifier'},
    {label: 'Case ID - Z to A', value: 'pseudoidentifier'},
  ]
  protected readonly tour = TourDriverConfig;
  protected vitalStatusChoices = [
    {value: false, label: 'Alive'},
    {value: true, label: 'Deceased'},
  ]
  // Resources
  public cases: Resource<PatientCase[] | undefined> = rxResource({
    request: () => ({
      idSearch: this.queryParams.idSearch() || undefined, 
      contributorsOverlaps: this.contributor() ? [this.contributor() as string] : undefined,
      ageBetween: this.queryParams.age(),
      gender: this.queryParams.gender() || undefined,
      dataCompletionRateBetween: this.queryParams.dataCompletion() ,
      primarySite: this.queryParams.primarySite()  || undefined, 
      morphology: this.queryParams.morphology()  || undefined, 
      isDeceased: this.queryParams.deceased() ?? undefined,
      limit: this.queryParams.limit() || 15, 
      offset: this.queryParams.offset() || 0,
      ordering: this.queryParams.sort(),
    } as GetPatientCasesRequestParams),
    loader: ({request}) => this.#patientCasesService.getPatientCases(request).pipe(
      tap(page => this.totalCases.set(page.count)),
      map(page => page.items),
      catchError((error: any) => {
        this.#messageService.add({ severity: 'error', summary: 'Error loading cases', detail: error?.error?.detail });
        return of([] as PatientCase[]) 
      })
    )
  })

  #updateRouteParameters = effect(() => {
    const urlTree = this.#router.createUrlTree([], {
      relativeTo: this.#activatedRoute,
      queryParams: {
        idSearch: this.queryParams.idSearch() || undefined,
        sort: this.queryParams.sort() !== '-createdAt' ? this.queryParams.sort() : undefined,
        limit: this.queryParams.limit() !== this.pageSizeChoices[0] ? this.queryParams.sort() : undefined,
        offset: this.queryParams.offset() || undefined,
        age: this.queryParams.age()?.join('-'),
        gender: this.queryParams.gender(),
        layout: this.queryParams.layout() !== 'grid' ? this.queryParams.layout() : undefined,
        deceased: this.queryParams.deceased(),
        dataCompletion: this.queryParams.dataCompletion()?.join('-'),
        primarySite: this.queryParams.primarySite(),
        morphology: this.queryParams.morphology(),
      },
      queryParamsHandling: 'merge',
    });
    //Update route with Query Params
    this.#location.go(urlTree.toString());
  })

  openNewCaseForm() {    
    this.#modalFormRef = this.#dialogservice.open(PatientFormComponent, {
      data: {
          title: 'Patient case registration',
          subtitle: 'Add a new patient case',
          icon: UserPlus,
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
            this.cases.reload()
        }
      })    
  }

  showSelectedCodedFilter(value: CodedConcept): string {
    return value?.display!
  }
  showAgeRangeFilter(range: any[]): string {
    return `${range[0]}-${range[1]} years`
  }
  showDataCompletionFilter(range: any[]): string {
    return `${range[0]}-${range[1]}%`
  }
  showSelectedVitalStatusFilter(choice: boolean): string {
    return choice ? 'Deceased' : 'Alive'
  }

  startTour() {
      driver(this.tour).drive()    
  }
  
}