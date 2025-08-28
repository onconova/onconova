import { Component, Input, ViewChild, ElementRef, ChangeDetectorRef, inject, input, viewChild, effect} from '@angular/core';
import { Chart } from 'chart.js';
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix';
import { ChartModule } from 'primeng/chart';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';
import { LayoutService } from 'src/app/core/layout/app.layout.service';
import { OncoplotDataset } from 'onconova-api-client';

// Register Chart.js modules and BoxPlot plugin
Chart.register(MatrixController, MatrixElement);

@Component({
    imports: [
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'onconova-oncoplot',
    template: `
    <div #oncoplot class="chart-container" style="height: 40rem; width: 100%">
        <div style="height: 15%; margin-left: 7.5rem; margin-bottom: -1rem; margin-right: 10%;">
            <canvas #oncoplotTopCanvas></canvas>
        </div>
        <div class="flex" style="height: 85%; width: 100%">
            <div style="height: 100%; width: 90%">
                <canvas #oncoplotCanvas></canvas>
            </div>
            <div class="my-auto" style="height: 95%; width: 10%">
                <canvas #oncoplotSideCanvas></canvas>
            </div>
        </div>    
        @if (chart) {
            <onconova-cohort-graph-context-menu [target]="oncoplot" [chart]="chart" [data]="data()"/>
        }
    </div>`
})
export class OncoplotComponent {

    readonly #layoutService = inject(LayoutService);

    public data = input.required<OncoplotDataset>()

    public chartRef = viewChild<ElementRef<HTMLCanvasElement>>('oncoplotCanvas');
    public sideChartRef = viewChild<ElementRef<HTMLCanvasElement>>('oncoplotSideCanvas');
    public topChartRef = viewChild<ElementRef<HTMLCanvasElement>>('oncoplotTopCanvas');
    public chart!: Chart;
    public sideChart!: Chart;
    public topChart!: Chart;


    #initChart = effect(() => {
        // React to changes in the overall theme settings
        this.#layoutService.config.darkMode();
        this.#layoutService.config.theme();

        if (!this.data()) return;

        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');
        
        const reversedGenes = [...this.data()['genes']].reverse()
        const genomicsData = this.data();

        const chartAreaBorder = {
            id: 'chartAreaBorder',
            beforeDraw(chart: any, args: any, options: any) {
              const {ctx, chartArea: {left, top, width, height}} = chart;
              ctx.save();
              ctx.strokeStyle = options.borderColor;
              ctx.lineWidth = options.borderWidth;
              ctx.strokeRect(left, top, width, height);
              ctx.restore();
            }
          };

        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.chartRef()!.nativeElement, {
            type: 'matrix',
            data: {
                datasets: [
                    {
                        data: this.data()['variants'].map( (entry: any) => ({
                            x: entry.caseId, y: entry.gene, hgvsExpression: entry.hgvsExpression, isPathogenic: entry.isPathogenic ? 1 : 0,
                        })),
                        backgroundColor(context: any) {
                          if (context.dataset.data[context.dataIndex].isPathogenic){
                            return documentStyle.getPropertyValue('--p-primary-500-semitransparent')
                          } else {
                            return documentStyle.getPropertyValue('--p-primary-500-transparent')
                          }
                        },
                        borderColor(context: any) {
                          if (context.dataset.data[context.dataIndex].isPathogenic){
                            return documentStyle.getPropertyValue('--p-primary-500-semitransparent')
                          } else {
                            return documentStyle.getPropertyValue('--p-primary-500-transparent')
                          }
                        },
                        borderWidth: 0,
                        height: ({chart}) =>(chart.chartArea || {}).height / this.data()['genes'].length - 1,
                        width: ({chart}) =>(chart.chartArea || {}).width / this.data()['cases'].length - 1
                    },
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    // @ts-ignore
                    chartAreaBorder: {
                        borderColor: surfaceBorder,
                        borderWidth: 1,
                    },
                    tooltip: {
                      callbacks: {
                        title() {
                          return '';
                        },
                        label(context) {
                          const data: any = context.dataset.data[context.dataIndex];
                          const variants = genomicsData['variants'].filter((entry: any) => entry.gene == data.y && entry.caseId == data.x && entry.hgvsExpression == data.hgvsExpression).map((entry: any) => entry.hgvsExpression + (entry.isPathogenic ? ' (Pathogenic)' : ' (VUS)'))
                          return [...variants, 'Gene: ' + data.y, 'Case: ' + data.x];
                        }
                      }
                    }
                },
                elements: {
                  boxandwhiskers: {
                    itemRadius: 2,
                    itemHitRadius: 4,
                    },
                },
                scales: {
                    x: {
                        type: 'category',
                        labels: this.data()['cases'],
                        offset: true,
                        title: {
                            display: true,
                            text: 'Cohort cases',
                            color: textColorSecondary,
                        },
                        ticks: {
                            padding: 10,
                            autoSkip: true,
                            display: false,
                        },
                        grid: {
                            display: this.data()['cases'].length > 100 ? false : true,
                            offset: true,
                            color: surfaceBorder,
                            drawTicks: false,
                        }
                    },
                    y: {
                        type: 'category',
                        labels: reversedGenes,
                        offset: true,
                        title: {
                            display: true,
                            text: 'Genes',
                            color: textColorSecondary,
                        },
                        ticks: {
                            padding: 10,
                            autoSkip: false,
                            color: textColorSecondary,
                            callback: function(scale, value) {
                                const label = reversedGenes[value]
                                const maxLength = 8; // Limit label length
                                return (label.length > maxLength) ? label.substring(0, maxLength) + "…" : label;
                            }
                        },
                        grid: {
                            display: this.data()['cases'].length > 100 ? false : true,
                            offset: true,
                            color: surfaceBorder,
                            drawOnChartArea: true,
                            drawTicks: false,
                        }
                    }
                }
            },
            plugins: [chartAreaBorder]
        });


        if (this.sideChart) {
            this.sideChart.destroy();
        }
        this.sideChart = new Chart(this.sideChartRef()!.nativeElement, {
            type: 'bar',
            data: {
                labels: this.data()['genes'],
                datasets: [
                    {
                        label: 'Pathogenic',
                        data: this.data()['genes'].map((gene:string) => this.data()['variants'].filter((entry:any) => entry.isPathogenic).reduce((total: number, entry: any) => (gene==entry.gene ? total+1 : total), 0)),
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                        barPercentage: 1,
                    },
                    {
                        label: 'VUS',
                        data: this.data()['genes'].map((gene:string) => this.data()['variants'].filter((entry:any) => !entry.isPathogenic).reduce((total: number, entry: any) => (gene==entry.gene ? total+1 : total), 0)),
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-transparent'),
                        barPercentage: 1,
                    },
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                      callbacks: {
                        title() {
                          return '';
                        },
                        label(context) {
                          const count: any = context.dataset.data[context.dataIndex];
                          return [context.dataset.label as string, `${count} cases`];
                        }
                      }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: false,
                        },
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false,
                        },
                    },
                    y: {
                        type: 'category',
                        stacked: true,
                        labels: this.data()['genes'],
                        title: {
                            display: false,
                        },
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false,
                            drawOnChartArea: true
                        },
                    }
                }
            }
        });

        if (this.topChart) {
            this.topChart.destroy();
        }
        this.topChart = new Chart(this.topChartRef()!.nativeElement, {
            type: 'bar',
            data: {
                labels: this.data()['cases'],
                datasets: [
                    {
                        label: 'Pathogenic',
                        data: this.data()['cases'].map((caseId:string) => this.data()['variants'].filter((entry:any) => entry.isPathogenic).reduce((total: number, entry: any) => (caseId==entry.caseId ? total+1 : total), 0)),
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                        barPercentage: 1,
                    },
                    {
                        label: 'VUS',
                        data: this.data()['cases'].map((caseId:string) => this.data()['variants'].filter((entry:any) => !entry.isPathogenic).reduce((total: number, entry: any) => (caseId==entry.caseId ? total+1 : total), 0)),
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-transparent'),
                        barPercentage: 1,
                    },
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                      callbacks: {
                        title() {
                          return '';
                        },
                        label(context) {
                          const count: any = context.dataset.data[context.dataIndex];
                          return [context.dataset.label as string, `${count} variants`];
                        }
                      }
                    }
                },
                scales: {
                    y: {
                        stacked: true,
                        title: {
                            display: false,
                        },
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false,
                        },
                    },
                    x: {
                        type: 'category',
                        stacked: true,
                        labels: this.data()['cases'],
                        title: {
                            display: false,
                        },
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false,
                        },
                    }
                }
            }
        });
    })

}
