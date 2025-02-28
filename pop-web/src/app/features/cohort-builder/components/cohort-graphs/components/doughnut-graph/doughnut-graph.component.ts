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
    selector: 'pop-doughnut-graph',
    template: `<p-chart type="doughnut" [data]="data" [options]="options" height="12rem" width="15rem"/>`,
})
export class DoughnutGraphComponent {
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

        const categories = Object.keys(this.countData)
        const values = Object.values(this.countData)  

        this.data = {
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
        };

        this.options = {
            maintainAspectRatio: false,
            aspectRatio: 0.6,
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                }
            },
        };
    }

}
