import { Component, effect, inject, ViewEncapsulation } from '@angular/core';

import { SkeletonModule } from 'primeng/skeleton';

import { DataPlatformStatisticsSchema, DashboardService, CasesPerMonthSchema } from 'src/app/shared/openapi';
import { ChartModule } from 'primeng/chart';
import { LayoutService } from 'src/app/core/layout/app.layout.service';
import { map, Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { DataSummaryCounterComponent } from "./components/statistic-counter/statistic-counter.component";

@Component({
    standalone: true,
    selector: 'pop-data-summary',
    templateUrl: './data-summary.component.html',
    encapsulation: ViewEncapsulation.None,
    imports: [
    CommonModule,
    SkeletonModule,
    ChartModule,
    DataSummaryCounterComponent
],
})
export class DataSummaryComponent {
    public readonly dashboardService = inject(DashboardService);
    public readonly layoutService = inject(LayoutService);

    public statistics$: Observable<DataPlatformStatisticsSchema> = this.dashboardService.getFullCohortStatistics()    

    
    public chartOptions: any;
    public chartData: any;
    public casesOverTimeData$!: Observable<any[]>;
    public casesOverTimeData!: any[]; 
    
    // Create effect after theme is changed to update chart colors
    themeEffect = effect(() => {
        this.layoutService.config.theme();
        this.layoutService.config.darkMode();
        if (this.casesOverTimeData) {
            this.initChart();
        }
    });

    ngOnInit() {
        this.casesOverTimeData$ = this.dashboardService.getCasesOverTime().pipe(
            map(response => {
                this.casesOverTimeData = response;
                this.initChart()
                return response
            })
        )
    }

    initChart() {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        this.chartData = { 
            labels: this.casesOverTimeData.map(item => {
                const date = new Date(item.month)
                return date.toLocaleString('default', { month: 'short', year: 'numeric' });
            }),
            datasets: [{
                label: 'Cases',
                data: this.casesOverTimeData.map(item => item.cumulativeCount),
                fill: true,
                tension: 0.5,
                borderColor: documentStyle.getPropertyValue('--p-primary-500'),
                backgroundColor: documentStyle.getPropertyValue('--p-primary-color-transparent'),
            }]
        }
    
        this.chartOptions = {
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
