import { Component, effect, inject, Input, ViewEncapsulation } from '@angular/core';

import { SkeletonModule } from 'primeng/skeleton';
import { NgxCountAnimationDirective } from "ngx-count-animation";

import { DataPlatformStatisticsSchema, DashboardService, CasesPerMonthSchema } from 'src/app/shared/openapi';
import { ChartModule } from 'primeng/chart';
import { LayoutService } from 'src/app/core/layout/app.layout.service';
import { map, Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { style } from '@angular/animations';

@Component({
    standalone: true,
    selector: 'pop-data-summary-counter',
    template: `
        <div class="data-statistic">
            @if (count || count==0) {
                <div class="data-statistic-number" [ngxCountAnimation]="count" duration="1000"></div>
            } @else {
                <p-skeleton height="2rem"/>
            }
            <div class="data-statistic-label text-muted"><small>{{title}}</small></div>
        </div>    
    `,
    imports: [
        CommonModule,
        SkeletonModule,
        NgxCountAnimationDirective,
        ChartModule,
    ],
})
export class DataSummaryCounterComponent {
    @Input({required: true}) public count!: number | undefined;    
    @Input({required: true}) public title!: string;    
}