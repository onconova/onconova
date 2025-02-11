import { Component, inject, ViewEncapsulation } from '@angular/core';

import { TableModule } from 'primeng/table';
import { RatingModule } from 'primeng/rating';
import { AvatarModule } from 'primeng/avatar';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { SkeletonModule } from 'primeng/skeleton';

import { EntityStatisticsSchema, DashboardService } from 'src/app/shared/openapi';

import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
    standalone: true,
    selector: 'pop-primary-entities-table',
    templateUrl: './primary-entities-table.component.html',
    styleUrl: './primary-entities-table.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule,
        FormsModule,
        CancerIconComponent,
        AvatarModule,
        AvatarGroupModule,
        RatingModule,
        TableModule,
        SkeletonModule,
    ],
})
export class PrimaryEntitiesTableComponent {
    public readonly dashboardService = inject(DashboardService);
    public entityStatistics$: Observable<EntityStatisticsSchema[]> = this.dashboardService.getPrimarySiteStatistics()    
}
