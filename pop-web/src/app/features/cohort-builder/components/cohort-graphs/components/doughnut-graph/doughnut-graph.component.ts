import { CommonModule } from '@angular/common';
import { Component, ElementRef, inject, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { Chart } from 'chart.js';
import { ChartModule } from 'primeng/chart';

import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';

@Component({
    standalone: true,
    imports: [
        CommonModule,
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-doughnut-graph',
    template: `
    <div class="chart-container" style="height: 12rem; width: 15rem">
        <canvas #doughnutCanvas ></canvas>
        <pop-cohort-graph-context-menu *ngIf="chart" [target]="doughnutCanvas" [chart]="chart" [data]="countData"/>
    </div>`,
})
export class DoughnutGraphComponent {
    @Input() countData!: any;

    @ViewChild('doughnutCanvas') private chartRef!: ElementRef<HTMLCanvasElement>;
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

        const categories = Object.keys(this.countData)
        const values = Object.values(this.countData)  

        // @ts-ignore
        this.chart = new Chart(this.chartRef.nativeElement, {
            type: 'doughnut',
            data: {
                labels: categories,
                datasets: [
                    {
                        data: values,
                        backgroundColor: [
                            documentStyle.getPropertyValue('--p-primary-600-semitransparent'),
                            documentStyle.getPropertyValue('--p-primary-400-semitransparent'),
                            documentStyle.getPropertyValue('--p-primary-200-semitransparent'),
                        ],
                        borderColor: 'rgba(0, 0, 0, 0)'
                    },
                ]
            },
            options: {
                maintainAspectRatio: false,
                aspectRatio: 0.6,
                plugins: {
                    legend: {
                        labels: {
                            color: textColor
                        }
                    }
                },
            }
        });
    }

}
