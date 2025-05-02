import { Component, Input, ViewChild, ElementRef, ChangeDetectorRef} from '@angular/core';
import { Chart } from 'chart.js';
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix';
import { ChartModule } from 'primeng/chart';
import { CohortGraphsContextMenu } from '../graph-context-menu/graph-context-menu.component';

// Register Chart.js modules and BoxPlot plugin
Chart.register(MatrixController, MatrixElement);

@Component({
    imports: [
        CohortGraphsContextMenu,
        ChartModule,
    ],
    selector: 'pop-oncoplot',
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
            <pop-cohort-graph-context-menu [target]="oncoplot" [chart]="chart" [data]="genomicsData"/>
        }
    </div>`
})
export class OncoplotComponent {

    constructor(private cdr: ChangeDetectorRef) { }

    @Input() genomicsData!: any;

    @ViewChild('oncoplotCanvas') private chartRef!: ElementRef<HTMLCanvasElement>;
    @ViewChild('oncoplotSideCanvas') private sideChartRef!: ElementRef<HTMLCanvasElement>;
    @ViewChild('oncoplotTopCanvas') private topChartRef!: ElementRef<HTMLCanvasElement>;
    public chart!: Chart;
    public sideChart!: Chart;
    public topChart!: Chart;

    ngAfterViewInit() {
        if (this.chartRef && this.sideChartRef && this.topChartRef) {
            this.initChart();
            this.cdr.detectChanges();
        }
    }


    initChart() {
        if (!this.genomicsData) return;

        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--p-text-color');
        const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
        const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');
        
        const reversedGenes = [...this.genomicsData['genes']].reverse()
        const genomicsData = this.genomicsData;

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

        this.chart = new Chart(this.chartRef.nativeElement, {
            type: 'matrix',
            data: {
                datasets: [
                    {
                        data: this.genomicsData['variants'].map( (entry: any) => ({
                            x: entry.pseudoidentifier, y: entry.gene, variant: entry.variant, isPathogenic: entry.is_pathogenic ? 1 : 0,
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
                        height: ({chart}) =>(chart.chartArea || {}).height / this.genomicsData['genes'].length - 1,
                        width: ({chart}) =>(chart.chartArea || {}).width / this.genomicsData['cases'].length - 1
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
                          const variants = genomicsData['variants'].filter((entry: any) => entry.gene == data.y && entry.pseudoidentifier == data.x).map((entry: any) => entry.variant + (entry.is_pathogenic ? ' (Pathogenic)' : ' (VUS)'))
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
                        labels: this.genomicsData['cases'],
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
                            display: this.genomicsData['cases'].length > 100 ? false : true,
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
                            display: this.genomicsData['cases'].length > 100 ? false : true,
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


        this.sideChart = new Chart(this.sideChartRef.nativeElement, {
            type: 'bar',
            data: {
                labels: this.genomicsData['genes'],
                datasets: [
                    {
                        label: 'Pathogenic',
                        data: this.genomicsData['genes'].map((gene:string) => this.genomicsData['variants'].filter((entry:any) => entry.is_pathogenic).reduce((total: number, entry: any) => (gene==entry.gene ? total+1 : total), 0)),
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                        barPercentage: 1,
                    },
                    {
                        label: 'VUS',
                        data: this.genomicsData['genes'].map((gene:string) => this.genomicsData['variants'].filter((entry:any) => !entry.is_pathogenic).reduce((total: number, entry: any) => (gene==entry.gene ? total+1 : total), 0)),
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
                        labels: this.genomicsData['genes'],
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


        this.topChart = new Chart(this.topChartRef.nativeElement, {
            type: 'bar',
            data: {
                labels: this.genomicsData['cases'],
                datasets: [
                    {
                        label: 'Pathogenic',
                        data: this.genomicsData['cases'].map((pseudoidentifier:string) => this.genomicsData['variants'].filter((entry:any) => entry.is_pathogenic).reduce((total: number, entry: any) => (pseudoidentifier==entry.pseudoidentifier ? total+1 : total), 0)),
                        backgroundColor: documentStyle.getPropertyValue('--p-primary-500-semitransparent'),
                        barPercentage: 1,
                    },
                    {
                        label: 'VUS',
                        data: this.genomicsData['cases'].map((pseudoidentifier:string) => this.genomicsData['variants'].filter((entry:any) => !entry.is_pathogenic).reduce((total: number, entry: any) => (pseudoidentifier==entry.pseudoidentifier ? total+1 : total), 0)),
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
                        labels: this.genomicsData['cases'],
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
    }

}
