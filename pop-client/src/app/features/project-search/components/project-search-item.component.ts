import { CommonModule } from '@angular/common';
import { Component, computed, inject, input, output} from '@angular/core';

import { Cohort, CohortsService, CohortTraitCounts, CohortTraitMedian, Project, ProjectStatusChoices } from 'src/app/shared/openapi';
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
import { UserBadgeComponent } from "../../../shared/components/user-badge/user-badge.component";
import { TagModule } from 'primeng/tag';
import { OverlayBadgeModule } from 'primeng/overlaybadge';

@Component({
    selector: 'pop-project-search-item',
    templateUrl: './project-search-item.component.html',
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
    AvatarGroupModule,
    DividerModule,
    SplitButtonModule,
    ConfirmDialogModule,
    ChipModule,
    SkeletonModule,
    UserBadgeComponent,
    TagModule,
    OverlayBadgeModule,
]
})
export class ProjectSearchItemComponent {

    // Component input/output signals
    public project = input.required<Project>();    
    public onDelete = output<void>();
    public onEdit = output<Project>();

    // Injected services
    readonly #authService = inject(AuthService);
    readonly #router = inject(Router);
    readonly #confirmationService = inject(ConfirmationService);
    readonly #downloadService = inject(DownloadService);
    readonly #messageService = inject(MessageService);
    readonly #cohortsService = inject(CohortsService);


    // Other properties
    public readonly currentUser = computed(() => this.#authService.user());

    // Other properties
    public readonly actionItems = [
        {
            label: 'Edit',
            icon: 'pi pi-pencil',
            disabled: !this.currentUser().canManageProjects,
            command: (event: any) => this.onEdit.emit(this.project()),
        },
    ];
    

    openProjectManagement() {
        this.#router.navigate(['projects/',this.project().id, 'management'])
    }

    parseStatus(status: ProjectStatusChoices): {value: string, icon: string, severity: string} {
        switch (status) {
            case ProjectStatusChoices.Planned:
                return {value: 'Planned', icon: 'pi pi-info', severity: 'secondary'}
            case ProjectStatusChoices.Ongoing:
                return {value: 'Ongoing', icon: 'pi pi-info', severity: 'info'}
            case ProjectStatusChoices.Completed:
                return {value: 'Completed', icon: 'pi pi-check', severity: 'success'}
            case ProjectStatusChoices.Aborted:
                return {value: 'Aborted', icon: 'pi pi-times', severity: 'danger'}
            default: 
                throw new Error(`Unknown status: ${status}`);
        }
    }
}