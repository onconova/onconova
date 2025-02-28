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
    selector: 'pop-distribution-graph',
    template: `<p-chart type="bar" [data]="data" [options]="options" height="15rem" width="35rem"/>`,
})
export class DistributionGraphComponent {
    @Input() countData!: any;

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

        // Convert keys to numbers for proper numeric sorting
        const entries = Object.entries(this.countData)
        .map(([key, value]) => [Number(key), value]) // Convert keys to numbers
        .sort((a: any, b: any) => a[0] - b[0]); // Sort by numeric value of key

        // Extract sorted categories and values
        const categories: string[] = entries.map(entry => String(entry[0])); // Convert back to string
        const values: number[] = entries.map((entry: any) => entry[1]);

        this.data = {
            labels: categories,
            datasets: [
                {
                    data: values,
                    fill: true,
                    stepped: true,
                    pointRadius: 0,
                    backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                },
            ]
        };

        this.options = {
            plugins: {
                legend: {
                    display: false
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
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder
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
                        color: textColorSecondary
                    },
                    grid: {
                        color: surfaceBorder
                    },
                    min: 0, 
                    max: Math.max(...values) + 1   
                }
            }
        };
    }

}
