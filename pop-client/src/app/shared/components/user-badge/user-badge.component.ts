import { Component, inject, input, ViewEncapsulation } from '@angular/core';

import { UsersService } from 'pop-api-client';
import { GetNameAcronymPipe } from '../../pipes/name-acronym.pipe';
import { GetFullNamePipe } from '../../pipes/full-name.pipe';

import { Avatar } from 'primeng/avatar';
import { Tooltip } from 'primeng/tooltip';
import { map } from 'rxjs';
import { Skeleton } from 'primeng/skeleton';
import { rxResource } from '@angular/core/rxjs-interop';

@Component({
    selector: 'pop-user-badge',
    template: `
        @if (user.isLoading()) {
            <p-skeleton width="2rem" height="2rem" styleClass="user-avatar" shape="circle"/>
        }
        @if (user.value(); as userInfo) {
            <div class="flex">
                <p-avatar label="{{ userInfo | acronym }}" styleClass="user-avatar" size="normal" shape="circle" [pTooltip]="userTooltipContent"/>
                @if (showName()) {
                    <div class="my-auto ml-2">{{ userInfo | fullname}}</div>   
                }
            </div>
            <ng-template #userTooltipContent>
                <div class="user-tooltip-content">
                    <p-avatar label="{{ userInfo | acronym }}" styleClass="user-avatar" size="large" shape="circle"/>
                    <div class="flex flex-column my-auto">
                        <div class="user-tooltip-content-name">
                        {{ userInfo | fullname }}          
                        </div>
                        <div class="user-tooltip-content-role text-muted">
                            <i class="pi pi-lock mr-1"></i>{{ userInfo.accessLevel }}, {{ userInfo.role }}          
                        </div>
                    </div>
                </div>
            </ng-template>
        }
    `,
    imports: [
        GetNameAcronymPipe,
        GetFullNamePipe,
        Avatar,
        Skeleton,
        Tooltip,
    ]
})
export class UserBadgeComponent {
    readonly #usersService = inject(UsersService);
    public username = input.required<string>();
    public showName = input<boolean>(false);
    public user = rxResource({
        request: () => ({username: this.username(), limit: 1}),
        loader: ({request}) => this.#usersService.getUsers(request).pipe(
            map(response => response.items[0])
        )
    });
}