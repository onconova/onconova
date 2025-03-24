import { CommonModule } from '@angular/common';
import { Component, inject, Input, SimpleChanges } from '@angular/core';
import { MessageService } from 'primeng/api';
import { Card } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { TableModule } from 'primeng/table';
import { first, map } from 'rxjs';

import { Cohort, CohortContribution, CohortsService } from 'src/app/shared/openapi';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        Card, 
        Skeleton,
        TableModule
    ],
    selector: 'pop-cohort-contributors',
    templateUrl: './cohort-contributors.component.html',
    styleUrls: ['./cohort-contributors.component.css']
})
export class CohortContributorsComponent{

    public cohortsService = inject(CohortsService);
    public messageService = inject(MessageService);
    
    @Input() cohort!: Cohort;
    @Input() loading: boolean = false;
    public cohortContributions!: CohortContribution[] | null;
    public totalContributions!: number;


    ngOnChanges(changes: SimpleChanges) {
        if (changes['loading'] && !this.loading) {
            this.updateContributions()
        }
    }

    ngOnInit() {
        this.updateContributions()
    }

    updateContributions() {
        this.cohortContributions = null
        this.cohortsService.getCohortContributors({cohortId: this.cohort.id}).pipe(
            first(),
            map((contributions: CohortContribution[])  => {
                this.cohortContributions = contributions.sort((a, b) => b.contributions - a.contributions)
                this.totalContributions = this.cohortContributions.map(c => c.contributions).reduce((a, b) => a + b, 0)
            }),
        ).subscribe({
            error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort contributors', detail: error.error.detail })
        })
    }

}
