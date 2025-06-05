import { Component, inject } from '@angular/core';
import { TableModule } from 'primeng/table';
import { RatingModule } from 'primeng/rating';
import { AvatarModule } from 'primeng/avatar';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { SkeletonModule } from 'primeng/skeleton';
import { EntityStatisticsSchema, DashboardService } from 'src/app/shared/openapi';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { rxResource } from '@angular/core/rxjs-interop';

@Component({
    selector: 'pop-primary-entities-table',
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
    template: `
        @if (entityStatistics.isLoading()) {
            <p-table [value]="[1,2,3,4,5,6,7,8]" [paginator]="true" [rows]="8">
                <ng-template #header>
                    <tr>
                        <th>Primary site</th>
                        <th>Cases</th>
                        <th>Average data completion</th>
                        <th>Contributors</th>
                    </tr>
                </ng-template>
                <ng-template #body let-entity>
                        <tr>
                            <td><p-skeleton /></td>
                            <td><p-skeleton /></td>
                            <td><p-skeleton /></td>
                            <td><p-skeleton /></td>
                        </tr>
                </ng-template>
            </p-table>
        } @else {
            <p-table [value]="entityStatistics.value() || []" [paginator]="true" [rows]="8">
                <ng-template #header>
                    <tr>
                        <th>Primary site</th>
                        <th class="text-center">Cases</th>
                        <th class="text-center">Average data completion</th>
                    </tr>
                </ng-template>
                <ng-template #body let-entity>
                    <tr>
                        <td class="flex">
                            <pop-cancer-icon [topography]="entity.topographyCode"/>
                            <div class="ml-3 my-auto">{{ entity.topographyGroup }}</div>
                        </td>
                        <td class="font-semibold text-center"> 
                            {{ entity.population }}
                        </td>
                        <td class="flex align-items-center">
                            <p-rating class="ml-auto" title="{{entity.dataCompletionMedian}}% median completion" [ngModel]="entity.dataCompletionMedian/20" [readonly]="true" />
                            <span class="text-muted ml-2 mr-auto">({{entity.dataCompletionMedian}}%)</span>
                        </td>
                    </tr>
                </ng-template>
            </p-table>
        }
    `
})
export class PrimaryEntitiesTableComponent {
    readonly #dashboardService = inject(DashboardService);
    public entityStatistics = rxResource({
        request: () => ({}),
        loader: () => this.#dashboardService.getPrimarySiteStatistics()
    });
}
