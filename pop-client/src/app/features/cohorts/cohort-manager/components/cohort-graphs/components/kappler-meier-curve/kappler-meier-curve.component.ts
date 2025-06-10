import { ChangeDetectorRef, Component, effect, ElementRef, inject, input, Input, viewChild, ViewChild } from '@angular/core';
import { ChartModule } from 'primeng/chart';

import { KapplerMeierCurve } from 'pop-api-client';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { Chart } from 'chart.js';
import { LayoutService } from 'src/app/core/layout/app.layout.service';

@Component({
    imports: [
        ChartModule,
        CohortGraphsContextMenu,
    ],
    selector: 'pop-kappler-meier-curve',
    template: `
    <div class="chart-container" style="height: {{height()}}; width: {{width()}}">
        <canvas #KapplerMeierCurve></canvas>
        @if (chart) {
            <pop-cohort-graph-context-menu [target]="KapplerMeierCurve" [chart]="chart" [data]="data()"/>
        }
    </div>`
})
export class KapplerMeierCurveComponent {

    readonly #layoutService = inject(LayoutService);

    public data = input.required<KapplerMeierCurve>()
    public height = input<string>('30rem')
    public width = input<string>('100%')
    public legendPosition = input<"left" | "right" | "bottom" | "top" | "center" | "chartArea">('top')

    public chartRef = viewChild<ElementRef<HTMLCanvasElement>>('KapplerMeierCurve');
    public chart!: Chart;

    #initChart = effect(() => {
        // React to changes in the overall theme settings
        this.#layoutService.config.darkMode();
        this.#layoutService.config.theme();

        if (!this.data()) return;

        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        const firstContactX = this.findFirstContactX(this.data().months, this.data().probabilities);

        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.chartRef()!.nativeElement, {
            type: 'line',
            data: {
                labels: this.data().months,
                datasets: [
                    {
                        label: 'Estimated Survival',
                        data: this.data().probabilities,
                        stepped: true,
                        fill: false,
                        tension: 0,
                        pointRadius: 0,
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
                        borderColor: documentStyle.getPropertyValue('--p-primary-500')
                    },
                    {
                        label: 'Confidence bands',
                        data: this.data().lowerConfidenceBand,
                        stepped: true,
                        fill: '+1',
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-color-transparent'), // Adjust transparency for confidence bands
                        borderColor: 'rgba(0, 0, 0, 0)',
                        pointRadius: 0,
                        tension: 0,
                    },
                    {
                        data: this.data().upperConfidenceBand,
                        stepped: true,
                        fill: false,
                        tension: 0,
                        pointRadius: 0,
                        borderColor: 'rgba(0, 0, 0, 0)',
                    },
                    {   
                        data: [
                            // @ts-ignore
                            { x: 0, y: 0.5 },          
                            // @ts-ignore
                            { x: firstContactX, y: 0.5 },
                            // @ts-ignore
                            { x: firstContactX, y: 0 }   
                        ],
                        borderColor: 'grey', // Choose a contrasting color
                        borderDash: [5, 5], // Dashed line
                        fill: false,
                        pointRadius: 0, // Hide points
                        tension: 0.0
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                aspectRatio: 0.6,
                plugins: {
                    legend: {
                        labels: {
                            filter: (item: any) => item.text !== undefined,
                            color: textColor
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                        display: true,
                        color: textColorSecondary,
                        text: 'Survival (months)',
                        },
                        ticks: {
                            color: textColorSecondary,
                            padding: 10.
                        },
                        grid: {
                            color: surfaceBorder,
                            drawTicks: false,
                        }
                    },
                    y: {
                        title: {
                        display: true,
                        color: textColorSecondary,
                        text: 'Estimated survival probability',
                        },
                        ticks: {
                            color: textColorSecondary,
                            padding: 10.
                        },
                        grid: {
                            color: surfaceBorder,
                            drawTicks: false,
                        },
                    }
                }
            }
        })
    })

    private findFirstContactX(months: number[], probabilities: number[]) {
        let shiftedProbabilities = probabilities.map(p => Math.abs(p - 0.5));
        let minIndex = shiftedProbabilities.indexOf(Math.min(...shiftedProbabilities));
        return months[minIndex]; // Fallback if not found
    }


}
