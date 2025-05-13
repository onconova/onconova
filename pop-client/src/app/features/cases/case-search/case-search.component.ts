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

// Project dependencies
import { PatientCase, PatientCasesService} from 'src/app/shared/openapi';
import { CaseSearchItemCardComponent } from './components/case-search-item/case-search-item.component';
import { PatientFormComponent } from 'src/app/features/forms';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { rxResource } from '@angular/core/rxjs-interop';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormHeaderComponent } from '../../forms/modal-form-header.component';


@Component({
  templateUrl: './case-search.component.html',
  imports: [
      CaseSearchItemCardComponent,
      NgxCountAnimationDirective,
      CommonModule,
      FormsModule,
      ReactiveFormsModule,
      IconFieldModule,
      OverlayBadgeModule,
      InputIconModule,
      InputTextModule,
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
  public readonly pageSizeChoices: number[] = [15, 30, 45, 60];
  public pagination = signal({limit: this.pageSizeChoices[0], offset: 0});
  public totalCases= signal(0);
  public searchQuery = signal('');

  // Resources
  public cases: Resource<PatientCase[] | undefined> = rxResource({
    request: () => ({pseudoidentifierContains: this.searchQuery() || undefined, manager: this.manager(), limit: this.pagination().limit, offset: this.pagination().offset}),
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
}