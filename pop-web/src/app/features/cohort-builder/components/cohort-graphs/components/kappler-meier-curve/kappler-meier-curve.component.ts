import { CommonModule } from '@angular/common';
import { Component, inject, Input, OnChanges, SimpleChanges } from '@angular/core';
import { ChartModule } from 'primeng/chart';

import { Cohort, CohortsService, KapplerMeierCurve } from 'src/app/shared/openapi';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        ChartModule,
    ],
    selector: 'pop-kappler-meier-curve',
    template: `<p-chart type="line" [data]="data" [options]="options" height="30rem" width="60%"/>`,
})
export class KapplerMeierCurveComponent {
    @Input() survivalData!: KapplerMeierCurve;

    public data!: any;
    public options!: any;


    ngOnInit() {
        this.initChart()
    }


    initChart() {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        // Find the first valid x-value (month) where dataset1 has data
        const firstContactX = this.findFirstContactX(this.survivalData.months, this.survivalData.probabilities);
        console.log('firstContactX', [
            { x: 0, y: 0.5 },                 // Start at (0, 0.5)
            { x: firstContactX, y: 0.5 },     // Move right to (firstContactX, 0.5)
            { x: firstContactX, y: 0 }        // Move down to (firstContactX, 0)
        ],)

        this.data = {
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
                        { x: 0, y: 0.5 },                 // Start at (0, 0.5)
                        { x: firstContactX, y: 0.5 },     // Move right to (firstContactX, 0.5)
                        { x: firstContactX, y: 0 }        // Move down to (firstContactX, 0)
                    ],
                    borderColor: 'grey', // Choose a contrasting color
                    borderDash: [5, 5], // Dashed line
                    fill: false,
                    pointRadius: 0, // Hide points
                    tension: 0.0
                }
            ]
        };

        this.options = {
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
        };
    }

    private findFirstContactX(months: number[], probabilities: number[]) {
        let shiftedProbabilities = probabilities.map(p => Math.abs(p - 0.5));
        let minIndex = shiftedProbabilities.indexOf(Math.min(...shiftedProbabilities));
        return months[minIndex]; // Fallback if not found
    }


}
