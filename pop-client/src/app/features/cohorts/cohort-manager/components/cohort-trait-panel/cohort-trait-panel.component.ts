import { CommonModule } from '@angular/common';
import { Component,Input } from '@angular/core';
import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';
import { Avatar } from 'primeng/avatar';
import { Card } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { TableModule } from 'primeng/table';

@Component({
    standalone: true,
    imports: [
    CommonModule,
    Card,
    Avatar,
    LucideAngularModule,
    Skeleton,
    TableModule,
],
    selector: 'pop-cohort-trait-panel',
    template:`
    <p-card class="flex" styleClass="border border-surface shadow-none">
        <div class="flex justify-between gap-8">
            <div class="flex flex gap-2">

                <div class="mr-1 my-auto">
                    <p-avatar class="cohort-statistics-avatar mr-2" size="large" shape="circle" [style]="{ 'background-color': 'var(--p-primary-color)', color: '#ffffff'}">
                        <lucide-angular class="cohort-search-item-icon" [img]="icon"></lucide-angular>
                    </p-avatar>
                </div>

                <div class="flex flex-column">
                    <div class="text-muted mb-1">{{ title }}</div>
                    <div class="flex">
                        <div>
                            @if (loading) {
                                <p-skeleton width="10rem" height="1.5rem"/>
                            } @else if (valid) { 
                                <ng-content></ng-content>
                            } @else {
                                -
                            }                     
                        </div>                 
                    </div>
                </div>
            </div>
        </div>
    </p-card>
    `
})
export class CohortTraitPanel{
    
    @Input({required: true}) icon!: LucideIconData;
    @Input({required: true}) title!: string;
    @Input() loading: boolean = false;
    @Input() valid: boolean = true;

}
