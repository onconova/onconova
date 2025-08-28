import { Component, effect, inject } from '@angular/core';
import { TableModule } from 'primeng/table';
import { RatingModule } from 'primeng/rating';
import { AvatarModule } from 'primeng/avatar';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { SkeletonModule } from 'primeng/skeleton';
import { DashboardService, PatientCaseDataCategories, CountsPerMonth } from 'onconova-api-client';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { rxResource } from '@angular/core/rxjs-interop';
import { ChartModule } from "primeng/chart";
import { LayoutService } from 'src/app/core/layout/app.layout.service';
import { ProgressBarModule } from 'primeng/progressbar';

@Component({
    selector: 'onconova-data-completion-stats',
    imports: [
    CommonModule,
    FormsModule,
    AvatarModule,
    AvatarGroupModule,
    ProgressBarModule,
    RatingModule,
    TableModule,
    SkeletonModule,
    ChartModule
],
    template: `
    @if (data.isLoading()) {

    } @else {
        @if (data.value(); as stats) {
            <div class="flex ml-4">
                <div class="w-10">
                    <div class="flex justify-content-between mb-2 text-muted">
                        <div class="p-progressbar-tick-label">0%</div>
                        <div class="p-progressbar-tick-label">25%</div>
                        <div class="p-progressbar-tick-label">50%</div>
                        <div class="p-progressbar-tick-label">75%</div>
                        <div class="p-progressbar-tick-label">100%</div>
                    </div>
                    <p-progressbar [value]="stats.overallCompletion" [showValue]="true">
                        <ng-template #content let-value>
                        </ng-template>
                    </p-progressbar>
                </div>
                <div class="mx-auto text-center">
                    <div class="font-semibold text-4xl">{{stats.overallCompletion}}%</div>
                    <div class="text-muted">Completion</div>
                </div>
            </div>

            <div class="mt-4 mb-2">
                <h6 class="mb-0 font-semibold">Completion Over Time</h6>
            </div>
            <p-chart type="line" [data]="chartData" [options]="chartOptions" [responsive]="true" height="18rem"/>

            <div class="mt-4 mb-2">
                <h6 class="mb-0 font-semibold">Most Incomplete Data Categories</h6>
            </div>
            <p-table [value]="stats.mostIncompleteCategories">
                <ng-template pTemplate="header">
                    <tr>
                        <th>Category</th>
                        <th class="text-center">Cases Where Missing</th>
                        <th>Most Affected Primary Sites</th>
                    </tr>
                </ng-template>
                <ng-template pTemplate="body" let-entry>
                    <tr>
                        <td>{{ entry.category | titlecase }}</td>
                        <td class="text-center">{{ entry.cases }} ({{ entry.cases / (stats.totalCases ) *100 | number:'1.0-0'}}%)</td>
                        <td>
                            @for (site of entry.affectedSites; track $index) {
                                {{site.display}}, 
                            }
                        </td>
                    </tr>
                </ng-template>
            </p-table>
        } @else if (data.error()) {
            <div class="text-muted">
                An error ocurred while loading the data
            </div>

        }
    }
    `
})
export class DataCompletionStatsComponent {
    readonly #layoutService = inject(LayoutService);
    readonly #dashboardService = inject(DashboardService);
    readonly totalCategories = Object.keys(PatientCaseDataCategories).length;
    public data = rxResource({
        request: () => ({}),
        loader: () => this.#dashboardService.getDataCompletionStats()
    });
    public chartOptions: any;
    public chartData: any;


    // Create effect after theme is changed to update chart colors
    #redrawChartEffect = effect(() => {
        this.#layoutService.config.theme();
        this.#layoutService.config.darkMode();
        const data = this.data.value()?.completionOverTime;
        if (data) {
            this.initChart(data);
        }
    });

    initChart(data: CountsPerMonth[]) {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        this.chartData = { 
            labels: data.map((item:CountsPerMonth) => {
                const date = new Date(item.month)
                return date.toLocaleString('default', { month: 'short', year: 'numeric' });
            }),
            datasets: [{
                label: 'Completion',
                data: data.map((item:CountsPerMonth) => item.cumulativeCount/(this.totalCategories * this.data.value()!.totalCases) * 100),
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
                        text: 'Completion %',
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
