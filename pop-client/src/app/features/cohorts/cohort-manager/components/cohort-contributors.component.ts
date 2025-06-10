import { CommonModule } from '@angular/common';
import { Component, computed, inject, input } from '@angular/core';
import { MessageService } from 'primeng/api';
import { Card } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { TableModule } from 'primeng/table';
import { map } from 'rxjs';

import { Cohort, CohortContribution, CohortsService } from 'pop-api-client';
import { UserBadgeComponent } from "../../../../shared/components/user-badge/user-badge.component";
import { rxResource } from '@angular/core/rxjs-interop';
import { Message } from 'primeng/message';

@Component({
    selector: 'pop-cohort-contributors',
    imports: [
        CommonModule,
        Card,
        Skeleton,
        TableModule,
        Message,
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
        @if (loading()|| contributions.isLoading()) {
            <p-skeleton height="40rem"/>
        }
        @if (contributions.hasValue()) {
            <p-table 
            [value]="contributions.value()" 
            [paginator]="true"
            [rows]="10">

            <ng-template #header >
                <tr>
                <th class="text-center">Rank</th>
                <th>Contributor</th>
                <th class="text-center">Cohort Cases</th>
                </tr>
            </ng-template>
            
            <ng-template #body let-entry let-i="rowIndex">
                <tr [ngClass]="{'top-rank-1': 1 === i+1, 'top-rank-2': 2 === i+1, 'top-rank-3': 3 === i+1}">
                <td class="text-center">{{ i + 1 }}</td>
                <td><pop-user-badge [username]="entry.contributor" [showName]="true"/></td>
                <td class="text-center">{{ entry.contributions }} ({{ entry.contributions/totalContributions()*100 | number: '1.0-0' }}%)</td>
                </tr>
            </ng-template>
            
            </p-table>
        } 
        @if (contributions.error()) {
            <p-message severity="error" text="Failed to load cohort contributors"></p-message>
        }
        <div class="mt-3 text-muted">
            *Both the <b>author and contributors</b> of this cohort are 
            to be <b>credited</b> when using this cohort's data for any scienitific publications.   
        </div>
    </p-card>
    `
})
export class CohortContributorsComponent{

    public cohort = input.required<Cohort>();
    public loading = input<boolean>(false);

    readonly #cohortsService = inject(CohortsService);
    readonly #messageService = inject(MessageService);
    
    public contributions = rxResource({
        request: () => ({cohortId: this.cohort().id}),
        loader: ({request}) => this.#cohortsService.getCohortContributors(request).pipe(
            map((contributions: CohortContribution[]) => contributions.sort((a, b) => b.contributions - a.contributions)),
        )
    });
    public totalContributions = computed<number>(() => this.contributions.value()!.map(c => c.contributions).reduce((a, b) => a + b, 0));  

}
