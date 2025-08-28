import { Component, input, Input } from '@angular/core';
import { SkeletonModule } from 'primeng/skeleton';
import { NgxCountAnimationDirective } from "ngx-count-animation";
import { ChartModule } from 'primeng/chart';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'onconova-data-summary-counter',
    template: `
        <div class="data-statistic">
            @if (!loading() && (count() || count()==0)) {
                <div class="data-statistic-number" [ngxCountAnimation]="count()" duration="1000"></div>
            } @else {
                <p-skeleton height="2rem"/>
            }
            <div class="data-statistic-label text-muted"><small>{{ title() }}</small></div>
        </div>    
    `,
    imports: [
        CommonModule,
        SkeletonModule,
        NgxCountAnimationDirective,
        ChartModule,
    ]
})
export class DataSummaryCounterComponent {
    public count = input.required<number | undefined>();    
    public title = input.required<string>();    
    public loading = input<boolean>(false);    
}