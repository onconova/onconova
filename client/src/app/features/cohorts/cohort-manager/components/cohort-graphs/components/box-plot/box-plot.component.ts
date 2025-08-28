import { Component, Input, ViewChild, ElementRef, ChangeDetectorRef, viewChild, input, effect, inject} from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { BoxPlotChart, BoxPlotController, BoxAndWiskers } from '@sgratzl/chartjs-chart-boxplot';
import { ChartModule } from 'primeng/chart';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { LayoutService } from 'src/app/core/layout/app.layout.service';

// Register Chart.js modules and BoxPlot plugin
Chart.register(...registerables, BoxPlotController, BoxPlotChart, BoxAndWiskers);

@Component({
    imports: [
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'onconova-box-plot',
    template: `
    <div class="chart-container" style="height: {{height()}}; width: {{width()}}">
        <canvas #boxPlotCanvas ></canvas>
        @if (chart) {
            <onconova-cohort-graph-context-menu [target]="boxPlotCanvas" [chart]="chart" [data]="data()"/>
        }
    </div>`
})
export class BoxPlotComponent {

    readonly #layoutService = inject(LayoutService);

    public data = input.required<{[key: string]: number[]}>()
    public height = input<string>('20rem')
    public width = input<string>('80%')
    public legendPosition = input<"left" | "right" | "bottom" | "top" | "center" | "chartArea">('top')

    public chartRef = viewChild<ElementRef<HTMLCanvasElement>>('boxPlotCanvas');
    public chart!: Chart;

    #initChart = effect(() => {
        // React to changes in the overall theme settings
        this.#layoutService.config.darkMode();
        this.#layoutService.config.theme();

        if (!this.data()) return;

        const documentStyle = getComputedStyle(document.documentElement);
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

        // Extract sorted categories and values
        const categories: string[] = Object.keys(this.data());
        const values: number[][] = Object.values(this.data());

        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.chartRef()!.nativeElement, {
            type: 'boxplot',
            data: {
                labels: categories,
                datasets: [
                    {
                        data: values,
                        // backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),

                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                        borderColor: documentStyle.getPropertyValue('--p-primary-color'),
                        borderWidth: 1,
                    },
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                        position: this.legendPosition(),
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
    });

}
