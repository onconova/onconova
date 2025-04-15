import { CommonModule } from '@angular/common';
import { Component, inject, Input, SimpleChanges } from '@angular/core';
import { MessageService } from 'primeng/api';
import { Card } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { TableModule } from 'primeng/table';
import { first, map } from 'rxjs';

import { Cohort, CohortContribution, CohortsService } from 'src/app/shared/openapi';
import { UserBadgeComponent } from "../../../../shared/components/user-badge/user-badge.component";

@Component({
    selector: 'pop-cohort-contributors',
    standalone: true,
    imports: [
        CommonModule,
        Card,
        Skeleton,
        TableModule,
        UserBadgeComponent
    ],
    template: `
    <p-card>
        <div>
            <p class="mb-1 text-muted ">
            The following people have contributed to the curation, entry, maintenance, and/or validation of 
            the data encompassed by this cohort.
            </p>
        </div>
        @if (!loading && cohortContributions) {
            <p-table 
            [value]="cohortContributions" 
            [paginator]="true"
            [rows]="10">

            <ng-template #header >
                <tr>
                <th class="text-center">Rank</th>
                <th>Contributor</th>
                <th class="text-center">Cohort Cases</th>
                </tr>
            </ng-template>
            
            <ng-template #body let-contribution let-i="rowIndex">
                <tr [ngClass]="{'top-rank-1': 1 === i+1, 'top-rank-2': 2 === i+1, 'top-rank-3': 3 === i+1}">
                <td class="text-center">{{ i + 1 }}</td>
                <td><pop-user-badge [username]="contribution.contributor" [showName]="true"/></td>
                <td class="text-center">{{ contribution.contributions }} ({{ contribution.contributions/totalContributions*100 | number: '1.0-0' }}%)</td>
                </tr>
            </ng-template>
            
            </p-table>
        } @else { 
            <p-skeleton height="40rem"/>
        }
        <div class="mt-3 text-muted">
            *Both the <b>author and contributors</b> of this cohort are 
            to be <b>credited</b> when using this cohort's data for any scienitific publications.   
        </div>
    </p-card>
    `
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
