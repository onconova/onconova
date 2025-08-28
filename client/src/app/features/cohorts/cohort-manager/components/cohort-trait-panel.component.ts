import { CommonModule } from '@angular/common';
import { Component,input,Input } from '@angular/core';
import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';
import { Avatar } from 'primeng/avatar';
import { Card } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { TableModule } from 'primeng/table';

@Component({
    imports: [
        CommonModule,
        LucideAngularModule,
        Skeleton,
        TableModule,
    ],
    selector: 'onconova-cohort-trait',
    template: `
        <div class="grid mb-1">
            <div class="text-muted text-small col-12 md:col-4">{{ title() }}</div>
            <div class="col-12 md:col">
                @if (loading()) {
                    <p-skeleton width="10rem" height="1rem"/>
                } @else if (valid()) { 
                    <ng-content></ng-content>
                } @else {
                    -
                }                     
            </div>                 
        </div>
    `
})
export class CohortTraitPanel{
    public title = input.required<string>(); 
    public loading = input<boolean>(false); 
    public valid = input<boolean | null>(true); 
}
