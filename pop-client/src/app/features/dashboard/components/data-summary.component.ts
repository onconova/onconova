import { Component, effect, inject } from '@angular/core';

import { SkeletonModule } from 'primeng/skeleton';

import { DataPlatformStatisticsSchema, DashboardService, CasesPerMonthSchema } from 'pop-api-client';
import { ChartModule } from 'primeng/chart';
import { LayoutService } from 'src/app/core/layout/app.layout.service';
import { map, Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { DataSummaryCounterComponent } from "./data-summary-counter.component";
import { rxResource } from '@angular/core/rxjs-interop';

@Component({
    selector: 'pop-data-summary',
    imports: [
        CommonModule,
        SkeletonModule,
        ChartModule,
        DataSummaryCounterComponent
    ],
    template: `
    <div class="flex flex-wrap gap-5 mx-4">
        <pop-data-summary-counter [count]="statistics.value()?.cases" title="Patient cases" [loading]="statistics.isLoading()"/>
        <pop-data-summary-counter [count]="statistics.value()?.entries" title="Data entries" [loading]="statistics.isLoading()"/>
        <pop-data-summary-counter [count]="statistics.value()?.primarySites" title="Primary Sites" [loading]="statistics.isLoading()"/>
        <pop-data-summary-counter [count]="statistics.value()?.mutations" title="Mutations" [loading]="statistics.isLoading()"/>
        <pop-data-summary-counter [count]="statistics.value()?.contributors" title="Contributors" [loading]="statistics.isLoading()"/>
        <pop-data-summary-counter [count]="statistics.value()?.cohorts" title="Cohorts" [loading]="statistics.isLoading()"/>
        <pop-data-summary-counter [count]="statistics.value()?.projects" title="Projects" [loading]="statistics.isLoading()"/>
        <pop-data-summary-counter [count]="statistics.value()?.clinicalCenters" title="Clinical Centers" [loading]="statistics.isLoading()"/>
    </div>
    <div class="mt-4 mb-2">
        <h6 class="mb-0 font-semibold">Growth over time</h6>
    </div>
    <div class="w-full" >
        @if (casesOverTime.isLoading()) {
            <p-skeleton height="15rem" class="w-full"/>
        } @else {
            <p-chart type="line" [data]="chartData" [options]="chartOptions" [responsive]="true" height="23rem"/>
        }
    </div>
    `
})
export class DataSummaryComponent {
    readonly #dashboardService = inject(DashboardService);
    readonly #layoutService = inject(LayoutService);

    public statistics = rxResource({
        request: () => ({}),
        loader: () => this.#dashboardService.getFullCohortStatistics()
    })
    
    public chartOptions: any;
    public chartData: any;
    public casesOverTime = rxResource({
        request: () => ({}),
        loader: () => this.#dashboardService.getCasesOverTime()
    })    
    // Create effect after theme is changed to update chart colors
    #redrawChartEffect = effect(() => {
        this.#layoutService.config.theme();
        this.#layoutService.config.darkMode();
        const data = this.casesOverTime.value();
        if (data) {
            this.initChart(data);
        }
    });

    initChart(data: CasesPerMonthSchema[]) {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        this.chartData = { 
            labels: data.map((item:CasesPerMonthSchema) => {
                const date = new Date(item.month)
                return date.toLocaleString('default', { month: 'short', year: 'numeric' });
            }),
            datasets: [{
                label: 'Cases',
                data: data.map((item:CasesPerMonthSchema) => item.cumulativeCount),
                fill: true,
                tension: 0.5,
                borderColor: documentStyle.getPropertyValue('--p-primary-500'),
                backgroundColor: documentStyle.getPropertyValue('--p-primary-color-transparent'),
            }]
        }
    
        this.chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            elements: {
                point: {radius: 0}
            },
            plugins: {
                legend: {display: false}
            },
            scales: {
                x: {
                    ticks: {
                        color: textColorSecondary
                    },
                    grid: {
                        display: false,
                        color: surfaceBorder
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Cases',
                        color: textColorSecondary
                    },
                    ticks: {
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder
                    }
                }
            }
        };
    }
}
