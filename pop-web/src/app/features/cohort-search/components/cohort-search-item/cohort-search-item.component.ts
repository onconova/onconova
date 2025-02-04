import { CommonModule } from '@angular/common';
import { Component, Input, Output, inject, EventEmitter, ViewEncapsulation} from '@angular/core';

import { PatientCase, AuthService, NeoplasticEntity, AnyStaging, StagingsService, NeoplasticEntitiesService, CohortsService, CohortStatisticsSchema } from 'src/app/shared/openapi';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Observable, map, of } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';
import { SplitButtonModule } from 'primeng/splitbutton';
import { ConfirmationService } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { SkeletonModule } from 'primeng/skeleton';
import { Knob } from 'primeng/knob';

import { Users } from 'lucide-angular';
import { LucideAngularModule } from 'lucide-angular';

import { NgxJdenticonModule } from "ngx-jdenticon";

import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';

@Component({
    standalone: true,
    selector: 'pop-cohort-search-item',
    templateUrl: './cohort-search-item.component.html',
    styleUrl: './cohort-search-item.component.css',
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
        Knob,
        SkeletonModule,
        CancerIconComponent,
    ],
    encapsulation: ViewEncapsulation.None,
})
export class CohortSearchItemComponent {

    private readonly router = inject(Router);
    private readonly cohortsService = inject(CohortsService);

    @Input() cohort: any;
    @Output() delete = new EventEmitter<string>();
    public statistics$: Observable<CohortStatisticsSchema> = of({})
    public readonly populationIcon = Users;

    ngOnInit() {
        this.statistics$ = this.cohortsService.getCohortStatistics({cohortId: this.cohort.id})
    }


    actionItems = [
        {
            label: 'Export',
            icon: 'pi pi-file-export',
            command: (event: any) => {
                console.log('export', this.cohort.id)
            },
        },
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            styleClass: 'delete-action',
            command: (event: any) => {
                console.log('delete', this.cohort.id)
                // this.confirmDelete(event);
            },
        },
    ];
    
    openCohortManagement() {
        this.router.navigate(['cohorts/',this.cohort.id, 'management'])
    }


}