import { CommonModule } from '@angular/common';
import { Component, Input, ViewChild, ElementRef, AfterViewInit, OnChanges, SimpleChanges } from '@angular/core';
import { Chart, ChartConfiguration, registerables } from 'chart.js';
import { BoxPlotChart, BoxPlotController, BoxAndWiskers } from '@sgratzl/chartjs-chart-boxplot';
import { ChartModule } from 'primeng/chart';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';

// Register Chart.js modules and BoxPlot plugin
Chart.register(...registerables, BoxPlotController, BoxPlotChart, BoxAndWiskers);

@Component({
    standalone: true,
    imports: [
        CommonModule,
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-box-plot',
    template: `
    <div class="chart-container" style="height: 20rem; width: 80%">
        <canvas #boxPlotCanvas ></canvas>
        <pop-cohort-graph-context-menu *ngIf="chart" [target]="boxPlotCanvas" [chart]="chart" [data]="boxData"/>
    </div>`,
})
export class BoxPlotComponent {
    @Input() boxData!: any;

    @ViewChild('boxPlotCanvas') private chartRef!: ElementRef<HTMLCanvasElement>;
    public chart!: Chart;

    ngAfterViewInit() {
        if (this.chartRef) {
            this.initChart();
        }
    }


    initChart() {
        if (!this.boxData) return;

        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        // Extract sorted categories and values
        const categories: string[] = Object.keys(this.boxData);
        const values: number[][] = Object.values(this.boxData);

        this.chart = new Chart(this.chartRef.nativeElement, {
            type: 'boxplot',
            data: {
                labels: categories,
                datasets: [
                    {
                        data: values,
                        // backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),

                        backgroundColor:   documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                        borderColor:  documentStyle.getPropertyValue('--p-primary-color'),
                        borderWidth: 1,
                    },
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                elements: {
                  boxandwhiskers: {
                    itemRadius: 2,
                    itemHitRadius: 4,
                    },
                },
                indexAxis: 'y',
                scales: {
                    x: {
                        title: {
                        display: true,
                        text: 'Progression-Free Survival (months)',
                        color: textColorSecondary,
                        },
                        ticks: {
                            color: textColorSecondary
                        },
                        grid: {
                            color: surfaceBorder
                        },
                    },
                    y2: {
                        position: 'left', // Moves tick labels to the right
                        title: {
                            display: true,
                            text: 'Systemic Therapy Drug Combinations',
                            color: textColorSecondary,
                        },
                        ticks: {
                            display: false,
                        },
                    },
                    y: {
                        position: 'right', // Moves tick labels to the right
                        ticks: {
                            color: textColorSecondary
                        },
                        grid: {
                            color: surfaceBorder
                        }
                    }
                }
            }
        });
    }

}
