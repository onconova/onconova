import { CommonModule } from '@angular/common';
import { Component, inject, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Card } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { map, Observable } from 'rxjs';

import { Cohort, CohortContribution, CohortsService, PatientCase } from 'src/app/shared/openapi';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        Card, 
        TableModule
    ],
    selector: 'pop-cohort-contributors',
    templateUrl: './cohort-contributors.component.html',
    styleUrls: ['./cohort-contributors.component.css']
})
export class CohortContributorsComponent{
    @Input() cohortContributions!: CohortContribution[];
    public totalContributions!: number;

    ngOnInit() {
        this.cohortContributions = this.cohortContributions.sort((a, b) => b.contributions - a.contributions)
        this.totalContributions = this.cohortContributions.map(c => c.contributions).reduce((a, b) => a + b, 0)
    }

}
