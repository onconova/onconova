import { Component, inject, input, computed, signal, Resource  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { map, first, of, catchError, tap } from 'rxjs';

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
import { rxResource } from '@angular/core/rxjs-interop';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormHeaderComponent } from '../../forms/modal-form-header.component';
import { ConceptSelectorComponent } from 'src/app/shared/components';
import { ButtonGroup } from 'primeng/buttongroup';
import { PopoverFilterButtonComponent } from 'src/app/shared/components/popover-filter-button/popover-filter-button.component';
import { SelectButton } from 'primeng/selectbutton';


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
      InputIconModule,
      InputTextModule,
      SelectButton,
      PopoverModule,
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
  public readonly manager = input<string>();
  
  // Injected services  
  readonly #patientCasesService = inject(PatientCasesService)
  readonly #authService = inject(AuthService)
  readonly #messageService = inject(MessageService) 
  readonly #dialogservice = inject(DialogService)
  #modalFormRef: DynamicDialogRef | undefined;

  // Computed properties
  public readonly isUserPage = computed(() => this.manager() !== undefined);
  public readonly currentUser = computed(() => this.#authService.user());

  // Pagination and search settings
  public readonly pageSizeChoices: number[] = [15, 30, 45];
  public pagination = signal({limit: this.pageSizeChoices[0], offset: 0});
  public totalCases= signal(0);
  public searchQuery = signal('');

  protected selectedAgeRange = signal<number[] | undefined>(undefined)
  protected selectedGender = signal<CodedConcept | undefined>(undefined)
  protected selectedVitalStatus = signal<any | undefined>(undefined)

  protected vitalStatusChoices = [
    {value: false, label: 'Alive'},
    {value: true, label: 'Deceased'},
  ]


  // Resources
  public cases: Resource<PatientCase[] | undefined> = rxResource({
    request: () => ({
      pseudoidentifierContains: this.searchQuery() || undefined, 
      contributorsOverlaps: this.manager() ? [this.manager() as string] : undefined,
      ageBetween: this.selectedAgeRange(),
      gender: this.selectedGender()?.code || undefined,
      isDeceased: this.selectedVitalStatus()?.value || undefined,
      limit: this.pagination().limit, 
      offset: this.pagination().offset
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
    return value!.display!
  }
  showAgeRangeFilter(range: any[]): string {
    return `${range[0]}-${range[1]} years`
  }
  showSelectedChoiceFilter(choice: {label: string, value: any}): string {
    return choice.label
  }
}