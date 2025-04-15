import { Component, inject, ViewEncapsulation } from '@angular/core';

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
import { AuthService } from 'src/app/core/auth/services/auth.service';

@Component({
    standalone: true,
    selector: 'pop-primary-entities-table',
    imports: [
        CommonModule,
        FormsModule,
        CancerIconComponent,
        UserBadgeComponent,
        AvatarModule,
        AvatarGroupModule,
        RatingModule,
        TableModule,
        SkeletonModule,
    ],
    template:`
        @let entityStatistics = entityStatistics$ | async;
        <p-table [value]="entityStatistics || [1,2,3,4,5,6,7,8]" [paginator]="true" [rows]="8">
            <ng-template #header>
                <tr>
                    <th>Primary site</th>
                    <th>Cases</th>
                    <th>Completion</th>
                    <th>Contributors</th>
                </tr>
            </ng-template>
            <ng-template #body let-entity>
                @if (entityStatistics) {
                    <tr>
                        <td class="flex">
                            <pop-cancer-icon [topography]="entity.topographyCode"/>
                            <div class="ml-3 my-auto">{{ entity.topographyGroup }}</div>
                        </td>
                        <td class="font-semibold"> 
                            {{ entity.population }}
                        </td>
                        <td>
                            <p-rating title="{{entity.dataCompletionMedian}}% median completion" [ngModel]="entity.dataCompletionMedian/20" [readonly]="true" />
                        </td>
                        <td>
                            <p-avatar-group>
                                @for (contributorUsername of entity.contributors; track $index; let index = $index;) {
                                    @if (index<3) {
                                        <pop-user-badge [username]="contributorUsername"/>
                                    }
                                }
                                @if (entity.contributors.length>3) {
                                    <p-avatar class="pop-other-users-avatar" [label]="'+' + (entity.contributors.length-3).toString()" shape="circle" size="normal" />
                                }
                            </p-avatar-group>
                        </td>
                    </tr>
                } @else {
                    <tr>
                        <td><p-skeleton /></td>
                        <td><p-skeleton /></td>
                        <td><p-skeleton /></td>
                        <td><p-skeleton /></td>
                    </tr>
                }
            </ng-template>
        </p-table>
    `
})
export class PrimaryEntitiesTableComponent {
    public readonly authService = inject(AuthService)
    public readonly dashboardService = inject(DashboardService);
    public entityStatistics$: Observable<EntityStatisticsSchema[]> = this.dashboardService.getPrimarySiteStatistics()    
}
