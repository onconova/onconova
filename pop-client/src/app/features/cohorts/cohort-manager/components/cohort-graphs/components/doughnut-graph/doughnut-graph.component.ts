import { ChangeDetectorRef, Component, ElementRef, Input, ViewChild } from '@angular/core';
import { Chart } from 'chart.js';
import { ChartModule } from 'primeng/chart';

import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { CohortTraitCounts } from 'src/app/shared/openapi';

@Component({
    imports: [
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-doughnut-graph',
    template: `
    <div class="chart-container" style="height: {{height}}; width: {{width}}">
        <canvas #doughnutCanvas ></canvas>
        @if (chart) {
            <pop-cohort-graph-context-menu [target]="doughnutCanvas" [chart]="chart" [data]="countData"/>
        }
    </div>`
})
export class DoughnutGraphComponent {

    constructor(private cdr: ChangeDetectorRef) { }

    @Input({required: true}) countData!: CohortTraitCounts[];
    @Input() height: string = '12rem';
    @Input() width: string = '15rem';
    @Input() legendPosition: "left" | "right" | "bottom" | "top" | "center" | "chartArea" = 'top';

    @ViewChild('doughnutCanvas') private chartRef!: ElementRef<HTMLCanvasElement>;
    public chart!: Chart;

    ngAfterViewInit() {
        if (this.chartRef) {
            this.initChart();
            this.cdr.detectChanges();
        }
    }

    initChart() {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        const categories = this.countData.map(entry => entry.category)
        const values = this.countData.map(entry => entry.counts)

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
                        position: this.legendPosition,
                        labels: {
                            color: textColor
                        }
                    }
                },
            }
        });
    }

}
