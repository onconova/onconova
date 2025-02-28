import { CommonModule } from '@angular/common';
import { Component, inject, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Card } from 'primeng/card';
import { SelectButtonChangeEvent, SelectButtonModule } from 'primeng/selectbutton';

import { first, map, Observable } from 'rxjs';
import { ChartModule } from 'primeng/chart';
import { SplitterModule } from 'primeng/splitter';
import { PanelModule } from 'primeng/panel';

import { Cohort, CohortsService, KapplerMeierCurve } from 'src/app/shared/openapi';
import { KapplerMeierCurveComponent } from './components/kappler-meier-curve/kappler-meier-curve.component';
import { FormsModule } from '@angular/forms';
import { DoughnutGraphComponent } from './components/doughnut-graph/doughnut-graph.component';
import { DistributionGraphComponent } from './components/distribution-graph/distribution-graph.component';
import { BoxPlotComponent } from './components/box-plot/box-plot.component';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        FormsModule,
        ChartModule,
        PanelModule,
        KapplerMeierCurveComponent,
        DoughnutGraphComponent,
        BoxPlotComponent,
        DistributionGraphComponent,
        Card, 
        SplitterModule,
        SelectButtonModule
    ],
    selector: 'pop-cohort-graphs',
    templateUrl: './cohort-graphs.component.html',
    styleUrls: ['./cohort-graphs.component.css']
})
export class CohortGraphsComponent {

    private cohortService = inject(CohortsService);

    @Input() cohort!: Cohort;

    public overallSurvivalCurve$!: Observable<KapplerMeierCurve>;
    public overallSurvivalCurveData!: any;
    public overallSurvivalCurveOptions!: any;

    public ageCount$!: Observable<any>;
    public ageAtDiagnosisCount$!: Observable<any>;
    public genderCount$!: Observable<any>;
    public vitalStatusCount$!: Observable<any>;
    public therapyLinesCount$!: Observable<any>

    public therapyLineOptions: string[] = []
    public therapyLineDrugCombinations$!: Observable<any>;    
    public therapyLineSurvivalCurve$!: Observable<KapplerMeierCurve>;    
    public selectedTherapyLine: string = 'CLoT1';


    ngOnInit() {
        this.overallSurvivalCurve$ = this.cohortService.getCohortOverallSurvivalCurve({cohortId: this.cohort.id})
        this.therapyLinesCount$ = this.cohortService.getCohortFeatureCounter({cohortId: this.cohort.id, feature: 'therapy_line'}).pipe(
            map((counter: any) => {
                this.therapyLineOptions = Object.keys(counter).sort((a, b) => a.localeCompare(b));
                return counter
            }),
        )
        this.ageCount$ = this.cohortService.getCohortFeatureCounter({cohortId: this.cohort.id, feature: 'age'})
        this.ageAtDiagnosisCount$ = this.cohortService.getCohortFeatureCounter({cohortId: this.cohort.id, feature: 'age_at_diagnosis'})
        this.vitalStatusCount$ = this.cohortService.getCohortFeatureCounter({cohortId: this.cohort.id, feature: 'vital_status'})
        this.genderCount$ = this.cohortService.getCohortFeatureCounter({cohortId: this.cohort.id, feature: 'gender'})
        this.therapyLineDrugCombinations$ = this.cohortService.getCohortProgressionFreeSurvivalCurveByDrugCombinations({cohortId: this.cohort.id, therapyLine: this.selectedTherapyLine})
        this.therapyLineSurvivalCurve$ = this.cohortService.getCohortProgressionFreeSurvivalCurve({cohortId: this.cohort.id, therapyLine: this.selectedTherapyLine})
    }

    updateTherapyLineGraphs(event: SelectButtonChangeEvent) {
        this.therapyLineSurvivalCurve$ = this.cohortService.getCohortProgressionFreeSurvivalCurve({cohortId: this.cohort.id, therapyLine: event.value})
        this.therapyLineDrugCombinations$ = this.cohortService.getCohortProgressionFreeSurvivalCurveByDrugCombinations({cohortId: this.cohort.id, therapyLine: event.value})
    }

}
