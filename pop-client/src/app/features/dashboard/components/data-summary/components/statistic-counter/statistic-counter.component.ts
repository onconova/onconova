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
    selector: 'pop-data-summay-counter',
    template: `
        <div class="data-statistic">
            @if (count !== undefined) {
                <div class="data-statistic-number" [ngxCountAnimation]="count" duration="1000"></div>
            } @else {
                <p-skeleton/>
            }
            <div class="data-statistic-label text-muted"><small>{{title}}</small></div>
        </div>    
    `,
    styles: `
        .data-statistic {
            border-left: solid 4px var(--p-primary-color); 
            padding-left: .5rem;
        }
        .data-statistic-number {
            font-size: 2rem;
            font-weight: 500;
        }
        .data-statistic-label {
            text-transform: uppercase;
        }
    `,
    encapsulation: ViewEncapsulation.None,
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