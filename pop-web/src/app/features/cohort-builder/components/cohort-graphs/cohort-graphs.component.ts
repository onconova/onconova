import { CommonModule } from '@angular/common';
import { Component, inject, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { Card } from 'primeng/card';
import { SelectButtonChangeEvent, SelectButtonModule } from 'primeng/selectbutton';

import { first, map, Observable } from 'rxjs';
import { ChartModule } from 'primeng/chart';
import { SplitterModule } from 'primeng/splitter';
import { PanelModule } from 'primeng/panel';

import { Cohort, CohortsService, CohortTraitCounts, KapplerMeierCurve } from 'src/app/shared/openapi';
import { KapplerMeierCurveComponent } from './components/kappler-meier-curve/kappler-meier-curve.component';
import { FormsModule } from '@angular/forms';
import { DoughnutGraphComponent } from './components/doughnut-graph/doughnut-graph.component';
import { DistributionGraphComponent } from './components/distribution-graph/distribution-graph.component';
import { BoxPlotComponent } from './components/box-plot/box-plot.component';
import { Skeleton } from 'primeng/skeleton';
import { OncoplotComponent } from './components/oncoplot/oncoplot.component';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        FormsModule,
        ChartModule,
        PanelModule,
        KapplerMeierCurveComponent,
        OncoplotComponent,
        DoughnutGraphComponent,
        Skeleton,
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
export class CohortGraphsComponent implements OnInit, OnChanges{

    private cohortService = inject(CohortsService);

    @Input() cohort!: Cohort;
    @Input() loading: boolean = false;

    public overallSurvivalCurve$!: Observable<KapplerMeierCurve>;
    public overallSurvivalCurveData!: any;
    public overallSurvivalCurveOptions!: any;
    public genomicsData$!: Observable<any>;

    public ageCount$!: Observable<CohortTraitCounts[]>;
    public ageAtDiagnosisCount$!: Observable<CohortTraitCounts[]>;
    public genderCount$!: Observable<CohortTraitCounts[]>;
    public vitalStatusCount$!: Observable<CohortTraitCounts[]>;
    public therapyLinesCount$!: Observable<CohortTraitCounts[]>

    public therapyLineOptions: string[] = []
    public therapyLineDrugCombinations$!: Observable<any>;    
    public therapyLineTherapyClassifications$!: Observable<any>;    
    public therapyLineSurvivalCurve$!: Observable<KapplerMeierCurve>;    
    public selectedTherapyLine: string = 'CLoT1';

    ngOnInit() {
        this.refreshData()
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes['loading'] && !this.loading) {
            this.refreshData()            
        }
    }

    refreshData() {
        this.overallSurvivalCurve$ = this.cohortService.getCohortOverallSurvivalCurve({cohortId: this.cohort.id})
        this.therapyLinesCount$ = this.cohortService.getCohortTraitCounts({cohortId: this.cohort.id, trait: 'therapyLines.label'}).pipe(
            map((response: CohortTraitCounts[])  => {
                this.therapyLineOptions = response.map(item=>item.category).sort((a, b) => a.localeCompare(b));
                return response
            }),
        )
        this.genomicsData$ = this.cohortService.getCohortGenomics({cohortId: this.cohort.id})
        this.ageCount$ = this.cohortService.getCohortTraitCounts({cohortId: this.cohort.id, trait: 'age'})
        this.ageAtDiagnosisCount$ = this.cohortService.getCohortTraitCounts({cohortId: this.cohort.id, trait: 'ageAtDiagnosis'})
        this.vitalStatusCount$ = this.cohortService.getCohortTraitCounts({cohortId: this.cohort.id, trait: 'isDeceased'}).pipe(map((response: CohortTraitCounts[]) => response.map(
            (item: CohortTraitCounts) => {
                item.category = item.category ? 'Alive' : 'Deceased' 
                return item
            }
        )))
        this.genderCount$ = this.cohortService.getCohortTraitCounts({cohortId: this.cohort.id, trait: 'gender.display'})
        this.therapyLineDrugCombinations$ = this.cohortService.getCohortProgressionFreeSurvivalCurveByDrugCombinations({cohortId: this.cohort.id, therapyLine: this.selectedTherapyLine})
        this.therapyLineTherapyClassifications$ = this.cohortService.getCohortProgressionFreeSurvivalCurveByTherapyClassifications({cohortId: this.cohort.id, therapyLine: this.selectedTherapyLine})
        this.therapyLineSurvivalCurve$ = this.cohortService.getCohortProgressionFreeSurvivalCurve({cohortId: this.cohort.id, therapyLine: this.selectedTherapyLine})
    }

    updateTherapyLineGraphs(event: SelectButtonChangeEvent) {
        this.therapyLineSurvivalCurve$ = this.cohortService.getCohortProgressionFreeSurvivalCurve({cohortId: this.cohort.id, therapyLine: event.value})
        this.therapyLineDrugCombinations$ = this.cohortService.getCohortProgressionFreeSurvivalCurveByDrugCombinations({cohortId: this.cohort.id, therapyLine: event.value})
        this.therapyLineTherapyClassifications$ = this.cohortService.getCohortProgressionFreeSurvivalCurveByTherapyClassifications({cohortId: this.cohort.id, therapyLine:  event.value})
    }

}
