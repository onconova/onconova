import { CommonModule } from '@angular/common';
import { Component, ElementRef, inject, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { ChartModule, UIChart } from 'primeng/chart';

import { Cohort, CohortsService, KapplerMeierCurve } from 'src/app/shared/openapi';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { Chart } from 'chart.js';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        ChartModule,
        CohortGraphsContextMenu,
    ],
    selector: 'pop-kappler-meier-curve',
    template: `
    <div class="chart-container" style="height: 30rem; width: 60%">
        <canvas #KapplerMeierCurve></canvas>
        <pop-cohort-graph-context-menu *ngIf="chart" [target]="KapplerMeierCurve" [chart]="chart" [data]="survivalData"/>
    </div>`,
})
export class KapplerMeierCurveComponent {
    @Input() survivalData!: KapplerMeierCurve;

    @ViewChild('KapplerMeierCurve') private chartRef!: ElementRef<HTMLCanvasElement>;
    public chart!: Chart;

    ngAfterViewInit() {
        if (this.chartRef) {
            this.initChart();
        }
    }



    initChart() {
        if (!this.survivalData) return;

        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        const firstContactX = this.findFirstContactX(this.survivalData.months, this.survivalData.probabilities);

        this.chart = new Chart(this.chartRef.nativeElement, {
            type: 'line',
            data: {
                labels: this.survivalData.months,
                datasets: [
                    {
                        label: 'Estimated Survival',
                        data: this.survivalData.probabilities,
                        stepped: true,
                        fill: false,
                        tension: 0,
                        pointRadius: 0,
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
                        borderColor: documentStyle.getPropertyValue('--p-primary-500')
                    },
                    {
                        label: 'Confidence bands',
                        data: this.survivalData.lowerConfidenceBand,
                        stepped: true,
                        fill: '+1',
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-color-transparent'), // Adjust transparency for confidence bands
                        borderColor: 'rgba(0, 0, 0, 0)',
                        pointRadius: 0,
                        tension: 0,
                    },
                    {
                        data: this.survivalData.upperConfidenceBand,
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
                            color: textColorSecondary
                        },
                        grid: {
                            color: surfaceBorder
                        }
                    },
                    y: {
                        title: {
                        display: true,
                        color: textColorSecondary,
                        text: 'Estimated survival probability',
                        },
                        ticks: {
                            color: textColorSecondary
                        },
                        grid: {
                            color: surfaceBorder
                        },
                    }
                }
            }
        })
    }

    private findFirstContactX(months: number[], probabilities: number[]) {
        let shiftedProbabilities = probabilities.map(p => Math.abs(p - 0.5));
        let minIndex = shiftedProbabilities.indexOf(Math.min(...shiftedProbabilities));
        return months[minIndex]; // Fallback if not found
    }


}
