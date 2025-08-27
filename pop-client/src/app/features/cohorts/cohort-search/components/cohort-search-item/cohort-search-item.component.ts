import { CommonModule } from '@angular/common';
import { Component, computed, inject, input, output} from '@angular/core';

import { AccessRoles, Cohort, CohortsService, CohortTraitCounts, CohortTraitMedian, ProjectsService } from 'pop-api-client';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Observable, catchError, first, map, of } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';
import { SplitButtonModule } from 'primeng/splitbutton';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { SkeletonModule } from 'primeng/skeleton';

import { Users } from 'lucide-angular';
import { LucideAngularModule } from 'lucide-angular';

import { NgxJdenticonModule } from "ngx-jdenticon";

import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DownloadService } from 'src/app/shared/services/download.service';
import { rxResource } from '@angular/core/rxjs-interop';
import { ResolveResourcePipe } from 'src/app/shared/pipes/resolve-resource.pipe';
import { ExportConfirmDialogComponent } from "../../../../../shared/components/export-confirm-dialog/export-confirm-dialog.component";

@Component({
    selector: 'pop-cohort-search-item, [pop-cohort-search-item]',
    templateUrl: './cohort-search-item.component.html',
    providers: [
        ConfirmationService,
    ],
    imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    NgxJdenticonModule,
    LucideAngularModule,
    AvatarModule,
    ResolveResourcePipe,
    AvatarGroupModule,
    DividerModule,
    SplitButtonModule,
    ConfirmDialogModule,
    ChipModule,
    SkeletonModule,
    ExportConfirmDialogComponent
]
})
export class CohortSearchItemComponent {

    // Component input/output signals
    public cohort = input.required<Cohort>();
    public layout = input<'card' | 'row'>('card');    
    public onDelete = output<void>();

    // Injected services
    readonly #authService = inject(AuthService);
    readonly #router = inject(Router);
    readonly #confirmationService = inject(ConfirmationService);
    readonly #projectsService = inject(ProjectsService);
    readonly #messageService = inject(MessageService);
    readonly #cohortsService = inject(CohortsService);
    readonly #downloadService = inject(DownloadService);

    // Resources
    public cohortTraits = rxResource({
        request: () => this.cohort().population ? {cohortId: this.cohort().id} : undefined,
        loader: ({request}: any) =>  this.#cohortsService.getCohortTraitsStatistics(request)
    }) 
    // Other properties
    public readonly currentUser = computed(() => this.#authService.user());
    private project = rxResource({
        request: () => ({projectId: this.cohort().projectId as string}),
        loader: ({request}) => this.#projectsService.getProjectById(request)
    })
    public readonly currentUserCanEdit = computed(() => 
        (this.currentUser().role == AccessRoles.ProjectManager && this.project.value()?.leader == this.currentUser().username) 
        || [AccessRoles.PlatformManager, AccessRoles.SystemAdministrator].includes(this.currentUser().role)
    )
    public readonly populationIcon = Users;
    public readonly actionItems = [
        {
            label: 'Export',
            icon: 'pi pi-file-export',
            styleClass: 'export-action',
            disabled: !this.currentUser().canExportData,
            command: () => this.exportCohortDefinition(),
        },
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            styleClass: 'delete-action',
            disabled: !(this.currentUser().role == AccessRoles.SystemAdministrator || this.currentUser().role == AccessRoles.PlatformManager),
            command: (event: any) => {
                this.confirmDelete(event);
            },
        },
    ];
    
    openCohortManagement() {
        this.#router.navigate(['cohorts/',this.cohort().id, 'management'])
    }

    confirmDelete(event: any) {
        this.#confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Danger Zone',
            message: `
                Are you sure you want to delete this cohort? 
                <div class="mt-2 font-medium text-secondary">
                    <small>${this.cohort().name}</small><br>
                </div>
            `,
            icon: 'pi pi-exclamation-triangle',
            rejectButtonProps: {label: 'Cancel', severity: 'secondary', outlined: true},
            acceptButtonProps: {label: 'Delete', severity: 'danger'},
            accept: () => {
                this.#cohortsService.deleteCohortById({cohortId: this.cohort().id}).pipe(first()).subscribe({
                    complete: () => {
                        this.onDelete.emit();
                        this.#messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: this.cohort().name })
                    },
                    error: (error: any) => this.#messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error?.error?.detail })
                })
            }
        });
    }

    getPredominantCount(counts: CohortTraitCounts[]) {
        return counts.sort((a,b) => b.counts - a.counts)[0]
    }


    exportCohortDefinition() {
        this.#confirmationService.confirm({
            key: 'exportConfirmation',
            accept: () => {
                const filename = `POP-cohort-${this.cohort().id}-bundle.json`;
                this.#messageService.add({severity: 'info', summary: 'Export in progress', detail:'Preparing data for download. Please wait.'})
                this.#cohortsService.exportCohortDefinition({cohortId: this.cohort().id}).pipe(first()).subscribe({
                    next: response => this.#downloadService.downloadAsJson(response, filename),
                    complete: () => this.#messageService.add({ severity: 'success', summary: 'Successfully exported', detail: filename }),
                    error: (error: any) => this.#messageService.add({ severity: 'error', summary: 'Error exporting cohort definition', detail: error?.error?.detail })
                })
            }
        })
    }

}