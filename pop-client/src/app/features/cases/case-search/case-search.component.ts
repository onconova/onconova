import { Component, inject, input, computed, signal, Resource  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { map, first, of, catchError, tap } from 'rxjs';

import { NgxCountAnimationDirective } from "ngx-count-animation";

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
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { rxResource } from '@angular/core/rxjs-interop';


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
  
  // Injected services  
  private readonly patientCasesService = inject(PatientCasesService)
  private readonly modalFormService = inject(ModalFormService)
  public readonly authService = inject(AuthService)
  private readonly messageService = inject(MessageService) 


  readonly manager = input<string>();
  public readonly isUserPage = computed(() => this.manager() !== undefined);

  public readonly pageSizeChoices: number[] = [15, 30, 45, 60];
  public pagination = signal({limit: this.pageSizeChoices[0], offset: 0});
  public totalCases= signal(0);
  public searchQuery = signal('');


  public cases: Resource<PatientCase[] | undefined> = rxResource({
    request: () => ({pseudoidentifierContains: this.searchQuery() || undefined, manager: this.manager(), limit: this.pagination().limit, offset: this.pagination().offset}),
    loader: ({request}) => this.patientCasesService.getPatientCases(request).pipe(
      tap(page => this.totalCases.set(page.count)),
      map(page => page.items),
      catchError((error: any) => {
        this.messageService.add({ severity: 'error', summary: 'Error loading cases', detail: error?.error?.detail });
        return of([] as PatientCase[]) 
      })
    )
  })

  openNewCaseForm() {    
    this.modalFormService.open(PatientFormComponent, {}, this.cases.reload.bind(this));
  }

  deleteCase(id: string) {
    this.patientCasesService.deletePatientCaseById({caseId:id}).pipe(first()).subscribe({
        complete: () => {
            this.cases.reload()
            this.messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: id })
        },
        error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error.error.detail })
    })
}

}