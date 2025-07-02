import { ChangeDetectorRef, Component, effect, ElementRef, inject, input, Input, viewChild, ViewChild } from '@angular/core';
import { ChartModule } from 'primeng/chart';

import { CohortTraitCounts } from 'pop-api-client';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { Chart } from 'chart.js';
import { LayoutService } from 'src/app/core/layout/app.layout.service';

@Component({
    imports: [
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-distribution-graph',
    template: `
    <div class="chart-container" style="height: {{height()}}; width: {{width()}}">
        <canvas #histogramCanvas></canvas>
        @if (chart) {
            <pop-cohort-graph-context-menu [target]="histogramCanvas" [chart]="chart" [data]="data()"/>
        }
    </div>`
})
export class DistributionGraphComponent {
    
    readonly #layoutService = inject(LayoutService);

    public data = input.required<CohortTraitCounts[]>()
    public height = input<string>('15rem')
    public width = input<string>('100%')
    public legendPosition = input<"left" | "right" | "bottom" | "top" | "center" | "chartArea">('top')

    public chartRef = viewChild<ElementRef<HTMLCanvasElement>>('histogramCanvas');
    public chart!: Chart;

    #initChart = effect(() => {
        // React to changes in the overall theme settings
        this.#layoutService.config.darkMode();
        this.#layoutService.config.theme();

        const documentStyle = getComputedStyle(document.documentElement);
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        // Convert keys to numbers for proper numeric sorting
        const entries = this.data()
            .map((entry) => [entry.category, entry.counts]) // Convert keys to numbers
            .sort(); // Sort by numeric value of key

        // Extract sorted categories and values
        const categories: string[] = entries.map(entry => String(entry[0])); // Convert back to string
        const values: number[] = entries.map((entry: any) => entry[1]);

        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.chartRef()!.nativeElement, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [
                    {
                        data: values,
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                    },
                ]
            },
            options: {
                plugins: {
                    legend: {
                        display: false,
                        position: this.legendPosition(),
                    }
                },
                scales: {
                    x: {
                        title: {
                        display: true,
                        text: 'Age (years)',
                        color: textColorSecondary,
                        },
                        ticks: {
                            color: textColorSecondary,
                            padding: 10.
                        },
                        grid: {
                            color: surfaceBorder,
                            drawTicks: false,
                        },
                        min: 0, 
                    },
                    y: {
                        title: {
                        display: true,
                        text: 'Cases',
                        color: textColorSecondary
                        },
                        ticks: {
                            color: textColorSecondary,
                            padding: 10.
                        },
                        grid: {
                            color: surfaceBorder,
                            drawTicks: false,
                        },
                        min: 0, 
                        max: Math.max(...values) + 1   
                    }
                }
            }
        });
    });

}
