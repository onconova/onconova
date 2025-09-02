import { Component, inject, input } from '@angular/core';
import { UsersService } from 'onconova-api-client';
import { GetNameAcronymPipe } from '../../pipes/name-acronym.pipe';
import { GetFullNamePipe } from '../../pipes/full-name.pipe';
import { Avatar } from 'primeng/avatar';
import { Tooltip } from 'primeng/tooltip';
import { map } from 'rxjs';
import { Skeleton } from 'primeng/skeleton';
import { rxResource } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';


/**
 * Displays a user badge with avatar, name, and role information.
 *
 * This component fetches user data by username and displays an avatar with a tooltip
 * containing the user's full name, access level, and role. Optionally, the user's name
 * can be shown next to the avatar. The avatar is clickable and links to the user's admin page.
 *
 * ```html
 * <onconova-user-badge [username]="'jdoe'" [showName]="true"></onconova-user-badge>
 * ```
 * 
 */
@Component({
    selector: 'onconova-user-badge',
    template: `
        @if (user.isLoading()) {
            <p-skeleton width="2rem" height="2rem" styleClass="user-avatar" shape="circle"/>
        }
        @if (user.value(); as userInfo) {
            <div class="flex">
                <p-avatar label="{{ userInfo | acronym }}" styleClass="user-avatar cursor-pointer" size="normal" shape="circle" [pTooltip]="userTooltipContent" [routerLink]="'/admin/users/' + userInfo.username"/>
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
        RouterLink,
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