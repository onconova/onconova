import { CommonModule } from '@angular/common';
import { Component, ElementRef, inject, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { ChartModule } from 'primeng/chart';

import { Cohort, CohortsService, CohortTraitCounts, KapplerMeierCurve } from 'src/app/shared/openapi';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { Chart } from 'chart.js';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-distribution-graph',
    template: `
    <div class="chart-container" style="height: 15rem; width: 100%">
        <canvas #histogramCanvas></canvas>
        <pop-cohort-graph-context-menu *ngIf="chart" [target]="histogramCanvas" [chart]="chart" [data]="countData"/>
    </div>`,
})
export class DistributionGraphComponent {
    @Input() countData!: CohortTraitCounts[];

    @ViewChild('histogramCanvas') private chartRef!: ElementRef<HTMLCanvasElement>;
    public chart!: Chart;

    ngAfterViewInit() {
        if (this.chartRef) {
            this.initChart();
        }
    }

    initChart() {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        // Convert keys to numbers for proper numeric sorting
        const entries = this.countData
            .map((entry) => [Number(entry.category), entry.counts]) // Convert keys to numbers
            .sort((a: any, b: any) => a[0] - b[0]); // Sort by numeric value of key

        // Extract sorted categories and values
        const categories: string[] = entries.map(entry => String(entry[0])); // Convert back to string
        const values: number[] = entries.map((entry: any) => entry[1]);

        this.chart = new Chart(this.chartRef.nativeElement, {
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
    }

}
