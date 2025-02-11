import { Component, inject, ViewEncapsulation } from '@angular/core';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { InlineSVGModule } from 'ng-inline-svg-2';

import { DialogModule } from 'primeng/dialog';
import { Button } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { RandomPaperComponent } from './components/random-paper/random-paper.component';
import { ChartModule } from 'primeng/chart';


import { PrimaryEntitiesTableComponent } from './components/primary-entities-table/primary-entities-table.component';
import { DataSummaryComponent } from './components/data-summary/data-summary.component';
import { PatientCasesService } from 'src/app/shared/openapi';

import { CommonModule } from '@angular/common';
import { map } from 'rxjs';

@Component({
    standalone: true,
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule,
        InlineSVGModule,
        CardModule,
        Button,
        DialogModule,
        ChartModule,
        RandomPaperComponent,
        DataSummaryComponent,
        PrimaryEntitiesTableComponent,
    ],
})
export class DashboardComponent {
    public readonly authService = inject(AuthService);
    public readonly caseService = inject(PatientCasesService);
    public readonly illustration: string = 'assets/images/landing/researcher.svg';
    public disclaimerDialogVisible: boolean = false;
    public today = new Date();
    private hours = this.today.getHours()
    public greet =  (this.hours >= 5 && this.hours < 12) ? "Morning" : (this.hours >= 12 && this.hours < 17) ? "Afternoon" : (this.hours >= 17 && this.hours < 20) ? "Evening" : "Night";

    
}
