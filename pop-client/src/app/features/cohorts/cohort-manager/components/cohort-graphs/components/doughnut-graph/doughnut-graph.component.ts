import { ChangeDetectorRef, Component, ElementRef, Input, ViewChild } from '@angular/core';
import { Chart } from 'chart.js';
import { ChartModule } from 'primeng/chart';

import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { CohortTraitCounts } from 'src/app/shared/openapi';

@Component({
    standalone: true,
    imports: [
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-doughnut-graph',
    template: `
    <div class="chart-container" style="height: 12rem; width: 15rem">
        <canvas #doughnutCanvas ></canvas>
        @if (chart) {
            <pop-cohort-graph-context-menu [target]="doughnutCanvas" [chart]="chart" [data]="countData"/>
        }
    </div>`,
})
export class DoughnutGraphComponent {

    constructor(private cdr: ChangeDetectorRef) { }

    @Input() countData!: CohortTraitCounts[];

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
                        labels: {
                            color: textColor
                        }
                    }
                },
            }
        });
    }

}
