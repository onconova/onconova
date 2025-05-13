import { CommonModule } from '@angular/common';
import { Component, computed, inject, input, signal } from '@angular/core';
import { Card } from 'primeng/card';
import { SelectButtonModule } from 'primeng/selectbutton';

import { map } from 'rxjs';
import { ChartModule } from 'primeng/chart';
import { SplitterModule } from 'primeng/splitter';
import { PanelModule } from 'primeng/panel';

import { Cohort, CohortsService } from 'src/app/shared/openapi';
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
    public loading = input<boolean>(false);

    // Injected services
    readonly #cohortService = inject(CohortsService);

    // Resources    
    public overallSurvivalCurve = rxResource({
        request: () => ({cohortId: this.cohort().id}),
        loader: ({request}) => this.#cohortService.getCohortOverallSurvivalCurve(request)
    })
    public cohortGenomics = rxResource({
        request: () => ({cohortId: this.cohort().id}),
        loader: ({request}) => this.#cohortService.getCohortGenomics(request)
    })    
    public ageCount = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'age'}),
        loader: ({request}) => this.#cohortService.getCohortTraitCounts(request)
    })
    public ageAtDiagnosisCount = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'ageAtDiagnosis'}),
        loader: ({request}) => this.#cohortService.getCohortTraitCounts(request)
    })
    public genderCount = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'gender.display'}),
        loader: ({request}) => this.#cohortService.getCohortTraitCounts(request)
    })
    public neoplasticSitesCount = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'neoplasticEntities.topographyGroup.display'}),
        loader: ({request}) => this.#cohortService.getCohortTraitCounts(request)
    })
    public vitalStatusCount = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'isDeceased'}),
        loader: ({request}) => this.#cohortService.getCohortTraitCounts(request).pipe(map(
            response => response.map(item => ({...item, category: item.category === 'true' ? 'Alive' : 'Dead'}))
        ))
    })
    public therapyLinesCount = rxResource({
        request: () => ({cohortId: this.cohort().id, trait: 'therapyLines.label'}),
        loader: ({request}) => this.#cohortService.getCohortTraitCounts(request)
    })
    public therapyLineOptions = computed<string[]>(
        () => this.therapyLinesCount.value()?.map(item=>item.category).filter(label=>label!='None').sort((a, b) => a.localeCompare(b)) || []
    )
    public selectedTherapyLine = signal<string>('CLoT1');
    public therapyLineDrugCombinations = rxResource({
        request: () => ({cohortId: this.cohort().id, therapyLine: this.selectedTherapyLine()}),
        loader: ({request}) => this.#cohortService.getCohortProgressionFreeSurvivalCurveByDrugCombinations(request)
    })
    public therapyLineTherapyClassifications = rxResource({
        request: () => ({cohortId: this.cohort().id, therapyLine: this.selectedTherapyLine()}),
        loader: ({request}) => this.#cohortService.getCohortProgressionFreeSurvivalCurveByTherapyClassifications(request)
    })
    public therapyLineSurvivalCurve = rxResource({
        request: () => ({cohortId: this.cohort().id, therapyLine: this.selectedTherapyLine()}),
        loader: ({request}) => this.#cohortService.getCohortProgressionFreeSurvivalCurve(request)
    })
}
