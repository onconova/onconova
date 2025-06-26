import { CommonModule } from "@angular/common";
import { Component, computed, inject, input, signal } from "@angular/core";
import { rxResource } from "@angular/core/rxjs-interop";
import { GetProjectsRequestParams, GetUserEventsRequestParams, GetUsersRequestParams, HistoryEventCategory, Project, ProjectsService, ProjectStatusChoices, UsersService } from "pop-api-client";
import { Avatar } from "primeng/avatar";
import { Card } from "primeng/card";
import { Divider } from "primeng/divider";
import { Skeleton } from "primeng/skeleton";
import { Table, TableModule } from "primeng/table";
import { Tag } from "primeng/tag";
import { map, of } from "rxjs";
import { UserBadgeComponent } from "src/app/shared/components/user-badge/user-badge.component";
import { CamelCaseToTitleCasePipe } from "src/app/shared/pipes/camel-to-title-case.pipe";
import { ResolveResourcePipe } from "src/app/shared/pipes/resolve-resource.pipe";

@Component({
    selector: 'pop-user-details',
    imports: [
        CommonModule,
        CamelCaseToTitleCasePipe,
        ResolveResourcePipe,
        UserBadgeComponent,
        Tag,
        Divider,
        Card,
        Skeleton,
        TableModule,
        Avatar,

    ],
    template: `
        <p-card>
            <div class="flex">
                <p-avatar shape="circle" [label]="initials()" styleClass="user-avatar text-7xl w-8rem h-8rem"></p-avatar>
                <div class="my-auto ml-3"> 
                    <div>
                        <h3 class="mb-0">
                            @if (user.value(); as user) {
                                {{user.firstName}} {{user.lastName}}
                            }
                        </h3>
                        <h6 class="mt-1 text-muted">
                            @if (user.value(); as user) {
                                <i class="pi pi-lock"></i> {{user.accessLevel}} - {{user.role}}
                            }
                        </h6>
                    </div>
                    <div class="mt-2 flex gap-4">
                        <div>
                            <div class="text-muted">Username</div>
                            @if (user.value(); as user) {
                                <span class="">{{ user.username || '-' }}</span>
                            }
                        </div>
                        <div>
                            <div class="text-muted">Last login</div>
                            @if (user.value(); as user) {
                                {{ (user.lastLogin | date:'medium' ) || '-' }}
                            }
                        </div>
                        <div>
                            <div class="text-muted">Email</div>
                            @if (user.value(); as user) {
                                {{user.email || '-' }}
                            }
                        </div>
                        <div>
                            <div class="text-muted">Organization</div>
                            @if (user.value(); as user) {
                                {{user.organization || '-'}}
                            }
                        </div>
                    </div>
                </div>
            </div>

            <p-divider class="my-4"></p-divider>

            <h5 class="mb-1 mt-5">Project Memberships</h5>
            <p-table [value]="projects.value() || []">
                <ng-template pTemplate="header">
                    <tr>
                        <th>Title</th>
                        <th>Leader</th>
                        <th>Status</th>
                    </tr>
                </ng-template>
                <ng-template pTemplate="body" let-project>
                    <tr>
                        <td>{{project.title || '-'}}</td>
                        <td>
                            <pop-user-badge [username]="project.leader" [showName]="true"/>    
                        <td>@switch (project.status) {
                                @case (projectStatus.Planned) {
                                    <p-tag severity="secondary" value="Planned"></p-tag>
                                }
                                @case (projectStatus.Ongoing) {
                                    <p-tag severity="info" value="Ongoing"></p-tag>
                                }
                                @case (projectStatus.Completed) {
                                    <p-tag severity="success" value="Completed"></p-tag>
                                }
                                @case (projectStatus.Aborted) {
                                    <p-tag severity="danger" value="Aborted"></p-tag>
                                }
                                @default {
                                    -
                                }
                            }</td>
                    </tr>
                </ng-template>
            </p-table>

            <p-divider class="my-4"></p-divider>
            
            <h5 class="mb-1 mt-5">Activity</h5>
            <p-table 
                [value]="events.value() || []"
                [paginator]="true" 
                [showCurrentPageReport]="true"
                lazy="true"
                [rows]="10" 
                [totalRecords]="totalEvents()"
                (onLazyLoad)="eventsPaginationOffset.set($event.first || 0)"
                currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries">
                <ng-template pTemplate="header">
                    <tr>
                        <th>Timestamp</th>
                        <th>Action</th>
                        <th>Resource</th>
                        <th>Details</th>
                    </tr>
                </ng-template>
                <ng-template pTemplate="body" let-event>
                    <tr>
                        <td>{{(event.timestamp | date:'medium') || '-'}}</td>
                        <td> @switch (event.category) {
                                @case (eventCategories.Import) {
                                    <p-tag severity="warning" value="Imported"></p-tag>
                                }
                                @case (eventCategories.Delete) {
                                    <p-tag severity="danger" value="Deleted"></p-tag>
                                }
                                @case (eventCategories.Create) {
                                    <p-tag severity="success" value="Created"></p-tag>
                                }
                                @case (eventCategories.Update) {
                                    <p-tag severity="info" value="Updated"></p-tag>
                                }
                                @case (eventCategories.Export) {
                                    <p-tag severity="danger" value="Exported"></p-tag>
                                }
                                @case (eventCategories.Create) {
                                    <p-tag severity="success" value="Created"></p-tag>
                                }
                                @default {
                                    -
                                }
                            }
                        </td>
                        <td>{{ event.resource | camelCaseToTitleCase }}</td>
                        <td>
                            @let description =event.snapshot.id | resolve | async;
                            @if (description) {
                                {{description}}
                            } @else {
                                <p-skeleton height="2rem" width="30rem"/>
                            }

                        </td>
                    </tr>
                </ng-template>
            </p-table>
        </p-card>
    `,
})
export class UserDetailsComponent {

    readonly username = input.required<string>();

    #usersService = inject(UsersService);
    #projectsService = inject(ProjectsService);

    protected user = rxResource({
        request: () => ({username: this.username(), limit: 1} satisfies GetUsersRequestParams),
        loader: ({request}) => this.#usersService.getUsers(request).pipe(
            map(response => response.items[0])
        )
    });
    protected projects = rxResource({
        request: () => ({membersUsername: this.username()} satisfies GetProjectsRequestParams),
        loader: ({request}) => this.#projectsService.getProjects(request).pipe(
            map(response => response.items)
        )
    })
    protected totalEvents = signal(0);

    protected eventsPaginationOffset = signal(0);
    protected events = rxResource({
        request: () =>  this.user.hasValue() ? {userId: this.user.value()?.id || '', limit: 10, offset: this.eventsPaginationOffset()} satisfies GetUserEventsRequestParams : undefined,
        loader: ({request}) => request ? this.#usersService.getUserEvents(request).pipe(
            map(response => {
                this.totalEvents.set(response.count)
                return response.items
            })
        ) : of(null)        
    }) 


    protected readonly eventCategories = HistoryEventCategory;
    protected readonly projectStatus = ProjectStatusChoices;
    protected readonly initials = computed(() => (this.user.value()?.firstName?.charAt(0) || '?') + this.user.value()?.lastName?.charAt(0));

}
