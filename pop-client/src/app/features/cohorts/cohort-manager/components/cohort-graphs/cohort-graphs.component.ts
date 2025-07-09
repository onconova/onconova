import { CommonModule } from '@angular/common';
import { Component, computed, inject, input, Resource, ResourceRef, signal } from '@angular/core';
import { Card } from 'primeng/card';
import { SelectButtonModule } from 'primeng/selectbutton';

import { map } from 'rxjs';
import { ChartModule } from 'primeng/chart';
import { SplitterModule } from 'primeng/splitter';
import { PanelModule } from 'primeng/panel';

import { Cohort, CohortsService, CohortTraitCounts, CohortTraits, DataAnalysisService } from 'pop-api-client';
import { KapplerMeierCurveComponent } from './components/kappler-meier-curve/kappler-meier-curve.component';
import { FormsModule } from '@angular/forms';
import { DoughnutGraphComponent } from './components/doughnut-graph/doughnut-graph.component';
import { DistributionGraphComponent } from './components/distribution-graph/distribution-graph.component';
import { BoxPlotComponent } from './components/box-plot/box-plot.component';
import { Skeleton } from 'primeng/skeleton';
import { OncoplotComponent } from './components/oncoplot/oncoplot.component';
import { MessageModule } from 'primeng/message';
import { rxResource } from '@angular/core/rxjs-interop';

@Component({
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
        MessageModule,
        Card,
        SplitterModule,
        SelectButtonModule
    ],
    selector: 'pop-cohort-graphs',
    templateUrl: './cohort-graphs.component.html'
})
export class CohortGraphsComponent {

    // Component input signals
    public cohort = input.required<Cohort>();
    public traits = input.required<ResourceRef<CohortTraits | undefined>>();
    public loading = input<boolean>(false);

    // Injected services
    readonly #analysisService = inject(DataAnalysisService);

    // Resources    
    public overallSurvivalCurve = rxResource({
        request: () => ({cohortId: this.cohort().id}),
        loader: ({request}) => this.#analysisService.getCohortOverallSurvivalCurve(request)
    })
    public cohortGenomics = rxResource({
        request: () => ({cohortId: this.cohort().id}),
        loader: ({request}) => this.#analysisService.getCohortOncoplot(request)
    })    
    public ageCount = computed(() => this.traits().value()?.ages)
    public ageAtDiagnosisCount = computed(() => this.traits().value()?.agesAtDiagnosis)
    public genderCount = computed(() => this.traits().value()?.genders)
    public neoplasticSitesCount = computed(() => this.traits().value()?.neoplasticSites)
    public vitalStatusCount = computed(() => this.traits().value()?.vitalStatus.map(item => ({...item, category: item.category === 'true' ? 'Alive' : 'Dead'})))
    public therapyLinesCount = computed(() => this.traits().value()?.therapyLines)
    public therapyLineOptions = computed<string[]>(
        () => this.therapyLinesCount()?.map(item=>item.category).filter(label=>label!='None').sort((a, b) => a.localeCompare(b)) || []
    )
    public therapyLineCohortFractionCount = computed((): CohortTraitCounts[] => {
        const cohortFractionCount = this.therapyLinesCount()?.find(item=>item.category==this.selectedTherapyLine())?.counts || 0
        return [{
            category: 'Not included',
            counts: this.cohort().population - cohortFractionCount,
            percentage: (this.cohort().population - cohortFractionCount) / this.cohort().population
        }, {
            category: 'Included',
            counts: cohortFractionCount,
            percentage: cohortFractionCount / this.cohort().population
        }]
    })
    public selectedTherapyLine = signal<string>('CLoT1');
    public therapyLineDrugCombinations = rxResource({
        request: () => ({cohortId: this.cohort().id, therapyLine: this.selectedTherapyLine(), categorization: 'drugs'}),
        loader: ({request}) => this.#analysisService.getCohortLineProgressionFreeSurvivalsByCategories(request)
    })
    public therapyLineTherapyClassifications = rxResource({
        request: () => ({cohortId: this.cohort().id, therapyLine: this.selectedTherapyLine(), categorization: 'therapies'}),
        loader: ({request}) => this.#analysisService.getCohortLineProgressionFreeSurvivalsByCategories(request)
    })
    public therapyLineSurvivalCurve = rxResource({
        request: () => ({cohortId: this.cohort().id, therapyLine: this.selectedTherapyLine()}),
        loader: ({request}) => this.#analysisService.getCohortLineProgressionFreeSurvivalCurve(request)
    })
    public therapyLineResponsesCount = rxResource({
        request: () => ({cohortId: this.cohort().id, therapyLine: this.selectedTherapyLine()}),
        loader: ({request}) => this.#analysisService.getCohortTherapyLineResponsesCounts(request)
    })
}
