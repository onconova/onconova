import { CommonModule } from '@angular/common';
import { Component, computed, inject, input, output} from '@angular/core';

import { Cohort, CohortsService, CohortTraitCounts, CohortTraitMedian } from 'pop-api-client';
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

@Component({
    selector: 'pop-cohort-search-item',
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
    ]
})
export class CohortSearchItemComponent {

    // Component input/output signals
    public cohort = input.required<Cohort>();    
    public onDelete = output<void>();

    // Injected services
    readonly #authService = inject(AuthService);
    readonly #router = inject(Router);
    readonly #confirmationService = inject(ConfirmationService);
    readonly #downloadService = inject(DownloadService);
    readonly #messageService = inject(MessageService);
    readonly #cohortsService = inject(CohortsService);

    // Resources
    public ageStats = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'age'}),
        loader: ({request}) => this.#cohortsService.getCohortTraitMedian(request)
    })
    public dataCompletionStats = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'dataCompletionRate'}),
        loader: ({request}) => this.#cohortsService.getCohortTraitMedian(request)
    })
    public predominantSite = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'neoplasticEntities.topographyGroup.display'}),
        loader: ({request}) => this.#cohortsService.getCohortTraitCounts(request).pipe(map(
            (response) => response.sort((a,b) => b.counts - a.counts)[0]
        ))
    })
    public predominantGender = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'gender'}),
        loader: ({request}) => this.#cohortsService.getCohortTraitCounts(request).pipe(map(
            (response) => response.sort((a,b) => b.counts - a.counts)[0]
        ))
    })


    // Other properties
    public readonly currentUser = computed(() => this.#authService.user());
    public readonly populationIcon = Users;
    public readonly actionItems = [
        // {
        //     label: 'Export',
        //     icon: 'pi pi-file-export',
        //     disabled: !this.currentUser().canExportData,
        //     command: (event: any) => {
        //         console.log('export', this.cohort().id)
        //     },
        // },
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            styleClass: 'delete-action',
            disabled: !this.currentUser().canManageCases,
            command: (event: any) => {
                console.log('delete', this.cohort().id)
                // this.confirmDelete(event);
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
                <div class="mt-2 font-bold text-secondary">
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

}