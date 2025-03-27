import { Component, OnInit, inject, Input, ViewEncapsulation  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { map, first, of, Observable, catchError } from 'rxjs';

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
import { CaseBrowserCardComponent } from './components/case-card/case-search-item.component';
import { PatientFormComponent } from 'src/app/features/forms';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';
import { AuthService } from 'src/app/core/auth/services/auth.service';


@Component({
  standalone: true,
  templateUrl: './case-search.component.html',
  styleUrl: './case-search.component.css',
  encapsulation: ViewEncapsulation.None,
  imports: [
    CaseBrowserCardComponent,
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
})

export class CaseBrowserComponent implements OnInit {
  
  // Injected services  
  private readonly patientCasesService = inject(PatientCasesService)
  private readonly modalFormService = inject(ModalFormService)
  public readonly authService = inject(AuthService)
  private readonly messageService = inject(MessageService) 


  @Input() public manager: string | undefined;

  // Pagination settings
  public pageSizeChoices: number[] = [15, 30, 45, 60];
  public pageSize: number = this.pageSizeChoices[0];
  public totalCases: number = 0;
  public currentOffset: number = 0;
  public loadingCases: boolean = true;
  public searchQuery: string = "";

  // Observables
  public cases$!: Observable<PatientCase[]> 

  ngOnInit() {
    this.refreshCases();
  }

  refreshCases() {
    this.loadingCases=true;
    this.cases$ = this.patientCasesService
    .getPatientCases({pseudoidentifierContains: this.searchQuery || undefined, manager: this.manager, limit: this.pageSize, offset: this.currentOffset})
    .pipe(
      map(page => {
        this.loadingCases=false;
        this.totalCases = page.count;
        return page.items
      }),
      first(),
      catchError((error: any) => {
        // Report any problems
        this.messageService.add({ severity: 'error', summary: 'Error loading cases', detail: error.error.detail });
        return of(error)
      })
    )
   }

   setPaginationAndRefresh(event: any) {
      this.currentOffset = event.first;
      this.pageSize = event.rows;
      this.refreshCases()
   }
   
  openNewCaseForm() {    
    this.modalFormService.open(PatientFormComponent, {}, this.refreshCases.bind(this));
  }


  deleteCase(id: string) {
    this.patientCasesService.deletePatientCaseById({caseId:id}).pipe(first()).subscribe({
        complete: () => {
            this.refreshCases()
            this.messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: id })
        },
        error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error.error.detail })
    })
}

}