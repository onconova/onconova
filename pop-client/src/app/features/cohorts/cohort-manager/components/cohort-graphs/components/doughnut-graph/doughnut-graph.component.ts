import { ChangeDetectorRef, Component, effect, ElementRef, inject, input, Input, viewChild, ViewChild } from '@angular/core';
import { Chart } from 'chart.js';
import { ChartModule } from 'primeng/chart';

import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { CohortTraitCounts } from 'pop-api-client';
import { LayoutService } from 'src/app/core/layout/app.layout.service';

@Component({
    imports: [
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-doughnut-graph',
    template: `
    <div class="chart-container" style="height: {{ height() }}; width: {{ width() }}">
        <canvas #doughnutCanvas ></canvas>
        @if (chart) {
            <pop-cohort-graph-context-menu [target]="doughnutCanvas" [chart]="chart" [data]="data()"/>
        }
    </div>`
})
export class DoughnutGraphComponent {

    readonly #layoutService = inject(LayoutService);

    public data = input.required<CohortTraitCounts[]>()
    public height = input<string>('12rem')
    public width = input<string>('15rem')
    public legendPosition = input<"left" | "right" | "bottom" | "top" | "center" | "chartArea">('top')

    public chartRef = viewChild<ElementRef<HTMLCanvasElement>>('doughnutCanvas');
    public chart!: Chart;

    #initChart = effect(() => {
        // React to changes in the overall theme settings
        this.#layoutService.config.darkMode();
        this.#layoutService.config.theme();
        
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');

        const categories = this.data().map(entry => entry.category)
        const values = this.data().map(entry => entry.counts)

        // @ts-ignore
        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.chartRef()!.nativeElement, {
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
                        position: this.legendPosition(),
                        labels: {
                            color: textColor
                        }
                    }
                },
            }
        });
    })

}
