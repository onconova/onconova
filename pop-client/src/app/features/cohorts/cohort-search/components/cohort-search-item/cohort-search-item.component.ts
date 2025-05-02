import { CommonModule } from '@angular/common';
import { Component, Input, Output, inject, EventEmitter, ViewEncapsulation} from '@angular/core';

import { CohortsService, CohortTraitCounts, CohortTraitMedian } from 'src/app/shared/openapi';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Observable, catchError, first, map, of } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';
import { SplitButtonModule } from 'primeng/splitbutton';
import { ConfirmationService } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { SkeletonModule } from 'primeng/skeleton';

import { Users } from 'lucide-angular';
import { LucideAngularModule } from 'lucide-angular';

import { NgxJdenticonModule } from "ngx-jdenticon";

import { AuthService } from 'src/app/core/auth/services/auth.service';

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
        AvatarGroupModule,
        DividerModule,
        SplitButtonModule,
        ConfirmDialogModule,
        ChipModule,
        SkeletonModule,
    ]
})
export class CohortSearchItemComponent {

    public authService = inject(AuthService)
    private readonly router = inject(Router);
    private readonly cohortsService = inject(CohortsService);

    @Input() cohort: any;
    @Output() delete = new EventEmitter<string>();
    public cohortAgeStats$: Observable<CohortTraitMedian | null> = of(null)
    public cohortDataCompletionStats$: Observable<CohortTraitMedian | null> = of(null)
    public cohortPredominantSite$: Observable<CohortTraitCounts | null> = of(null)
    public cohortPredominantGender$: Observable<CohortTraitCounts | null> = of(null)
    public readonly populationIcon = Users;

    ngOnInit() {
        if (this.cohort.population) {
            this.cohortPredominantGender$ = this.cohortsService.getCohortTraitCounts({cohortId: this.cohort.id, trait: 'gender'}).pipe(
                first(),
                map((response: CohortTraitCounts[]) => response.sort((a,b) => b.counts - a.counts)[0]),
                catchError(() => of(null))
            )
            this.cohortPredominantSite$ = this.cohortsService.getCohortTraitCounts({cohortId: this.cohort.id, trait: 'neoplasticEntities.topographyGroup.display'}).pipe(
                first(),
                map((response: CohortTraitCounts[]) => response.sort((a,b) => b.counts - a.counts)[0]),
                catchError(() => of(null))
            )
            this.cohortAgeStats$ = this.cohortsService.getCohortTraitMedian({cohortId: this.cohort.id, trait: 'age'}).pipe(first(),catchError(() => of(null)))
            this.cohortDataCompletionStats$ = this.cohortsService.getCohortTraitMedian({cohortId: this.cohort.id, trait: 'dataCompletionRate'}).pipe(first(),catchError(() => of(null)))    
        }
    }


    actionItems = [
        {
            label: 'Export',
            icon: 'pi pi-file-export',
            command: (event: any) => {
                console.log('export', this.cohort.id)
            },
        },
        // {
        //     label: 'Delete',
        //     icon: 'pi pi-trash',
        //     styleClass: 'delete-action',
        //     command: (event: any) => {
        //         console.log('delete', this.cohort.id)
        //         // this.confirmDelete(event);
        //     },
        // },
    ];
    
    openCohortManagement() {
        this.router.navigate(['cohorts/',this.cohort.id, 'management'])
    }


}