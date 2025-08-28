import { CommonModule } from "@angular/common";
import { Component, computed, inject, input, signal } from "@angular/core";
import { rxResource } from "@angular/core/rxjs-interop";
import { FormsModule } from "@angular/forms";
import { ConfirmationService, MenuItem, MessageService } from "primeng/api";
import { Button } from "primeng/button";
import { ConfirmDialog } from "primeng/confirmdialog";
import { DataView } from "primeng/dataview";
import { DatePicker } from "primeng/datepicker";
import { Fluid } from "primeng/fluid";
import { Menu } from "primeng/menu";
import { Skeleton } from "primeng/skeleton";
import { TableModule } from "primeng/table";
import { TagModule } from "primeng/tag";
import { ToggleSwitch } from "primeng/toggleswitch";
import { BehaviorSubject, forkJoin, from, map, mergeMap, Observable, toArray } from "rxjs";
import { UserBadgeComponent } from "src/app/shared/components/user-badge/user-badge.component";
import { AccessRoles, Cohort, CohortsService, DatasetsService, Period, ProjectCreate, ProjectDataManagerGrant, ProjectsService, ProjectStatusChoices, User, UsersService } from "onconova-api-client";
import { CohortSearchItemComponent } from "../cohorts/cohort-search/components/cohort-search-item/cohort-search-item.component";
import { AuthService } from "src/app/core/auth/services/auth.service";
import { ResolveResourcePipe } from "src/app/shared/pipes/resolve-resource.pipe";
import { Popover } from "primeng/popover";
import { UserSelectorComponent } from "src/app/shared/components/user-selector/user-selector.component";
import { Divider } from "primeng/divider";
import { Card } from "primeng/card";

interface ProjectMember extends User {
    authorization: ProjectDataManagerGrant
}

@Component({
    selector: 'onconova-project-management',
    templateUrl: './project-management.component.html',
    providers: [
        ConfirmationService
    ],
    imports: [
        Fluid,
        FormsModule,
        CommonModule,
        Skeleton,
        UserBadgeComponent,
        Divider,
        Popover,
        Card,
        ConfirmDialog,
        ToggleSwitch,
        TagModule,
        DataView,
        TableModule,
        DatePicker,
        Menu,
        Button,
        UserSelectorComponent,
        CohortSearchItemComponent,
    ]
})
export class ProjectManagementComponent {
    
    readonly projectId = input.required<string>();
    
    readonly #projectsService = inject(ProjectsService);
    readonly #userService = inject(UsersService);
    readonly #authService = inject(AuthService);
    readonly #messageService = inject(MessageService);
    readonly #confirmationService = inject(ConfirmationService);
    readonly #cohortsService = inject(CohortsService);
    readonly #datasetsService = inject(DatasetsService);

    public readonly currentUser = computed(() => this.#authService.user())

    protected project = rxResource({
        request: () => ({projectId: this.projectId()}),
        loader: ({request}) => this.#projectsService.getProjectById(request)
    });
    
    protected readonly membersPlaceholder = [1,3,4,5] as unknown as ProjectMember[];
    protected members = rxResource({
        request: () => ({usernameAnyOf: this.project.value()?.members ?? []}),
        loader: ({request}) => this.#userService.getUsers(request).pipe(
            map(response => response.items),       
            mergeMap(users => from(users)),
            mergeMap((user): Observable<ProjectMember> =>
                forkJoin({
                authorization: this.#projectsService.getProjectDataManagerGrant({projectId: this.projectId(), memberId: user.id}).pipe(map(response => response.items[0])),
                }).pipe(
                map(results => ({
                    ...user,
                    ...results
                }))
                )
            ),
            toArray()
        )
    });

    protected cohorts = rxResource({
        request: () => ({projectId: this.projectId()}),
        loader: ({request}) => this.#cohortsService.getCohorts(request).pipe(map(response => {
            this.totalCohorts.set(response.count)
            return response.items
        }))
    });
    protected datasets = rxResource({
        request: () => ({projectId: this.projectId()}),
        loader: ({request}) => this.#datasetsService.getDatasets(request).pipe(map(response => {
            this.totalDatasets.set(response.count)
            return response.items
        }))
    });

    protected authDialogMember = signal<ProjectMember | null>(null);
    protected authDialogConfirmation = signal<boolean>(false);
    protected authDialogValidityPeriod = signal<Date[]>([]);
    protected authDialogExpirationMinDate = new Date();
    protected authDialogExpirationMaxDate = computed(() => {
        const start = this.authDialogValidityPeriod()![0];
        if (!start) {
            return null
        }
        return new Date(start.getTime() + 31 * 24 * 60 * 60 * 1000)
    })
    


    // Pagination and search settings
    public readonly cohortsPageSizeChoices: number[] = [4, 8, 12];
    public cohortsPagination = signal({limit: this.cohortsPageSizeChoices[0], offset: 0});
    public totalCohorts= signal(0);
    public readonly datasetsPageSizeChoices: number[] = [4, 8, 12];
    public datasetsPagination = signal({limit: this.cohortsPageSizeChoices[0], offset: 0});
    public totalDatasets= signal(0);

    public selectedUser = signal<string>('')


    getValidityPeriodAnnotation(period: Period) {
        const today = new Date()
        const begin = new Date(period.start!)
        const expiration = new Date(period.end!)
        if (today < begin) {
            return `Begins in ${this.getDaysDifference(today, begin)} day(s)`
        } else if (today < expiration) {
            return `Expires in ${this.getDaysDifference(today, expiration)} day(s)`
        } else {
            return 'Expired'
        }
    }


    matchCohort(cohortId: string) {
        return (cohort: Cohort): boolean => cohort.id == cohortId
    }
    
    getDaysDifference(start: Date, end: Date) {
        const oneDayMs = 1000 * 60 * 60 * 24; // milliseconds in one day
        const diffMs = end.getTime() - start.getTime();
        return Math.ceil(diffMs / oneDayMs);
    }

    canEditAuthorizations = computed(() => 
        this.project.value() && (this.currentUser()?.accessLevel || 0) > 1 && (
            (this.currentUser()?.accessLevel || 0) > 2 ||
            this.currentUser().username == this.project.value()?.leader 
            || 
            (this.project.value()?.members || []).includes(this.currentUser().username)
         ) && !(
            this.project.value()?.status === ProjectStatusChoices.Completed 
            || this.project.value()?.status === ProjectStatusChoices.Aborted
        ) 
    )

    public dynamicMenuItems$: BehaviorSubject<MenuItem[]> = new BehaviorSubject(
        [] as MenuItem[]
    );
    getMemberMenuItems(member: ProjectMember) {
        this.dynamicMenuItems$.next([{
            label: 'Actions for ' + member.fullName,
            items: [
                {
                    label: 'Grant data management authorization',
                    icon: 'pi pi-plus',
                    disabled: !this.canEditAuthorizations() 
                            || (member?.accessLevel || 0) >= 2 
                            || !!member.authorization,
                    command: (event: any) => this.grantNewAuthorization(event, member)
                },
                {
                    label: 'Revoke data management authorization',
                    disabled: !this.canEditAuthorizations() 
                            || (member?.accessLevel || 0) >= 2 
                            || !member.authorization 
                            || (new Date(member.authorization.validityPeriod.end as string) < new Date()),
                    icon: 'pi pi-times',
                    command: (event: any) => this.revokeAuthorization(event, member)
                },
                {
                    label: 'Remove member',
                    disabled: !this.canEditAuthorizations() || this.currentUser().username == member.username || this.project.value()?.leader == member.username,
                    icon: 'pi pi-trash',
                    command: (event: any) => this.confirmMemberRemoval(event, member)
                },
            ]
        }])
    };

    parseStatus(status: ProjectStatusChoices): {value: string, icon: string, severity: string} {
        switch (status) {
            case ProjectStatusChoices.Planned:
                return {value: 'Planned', icon: 'pi pi-info', severity: 'secondary'}
            case ProjectStatusChoices.Ongoing:
                return {value: 'Ongoing', icon: 'pi pi-info', severity: 'info'}
            case ProjectStatusChoices.Completed:
                return {value: 'Completed', icon: 'pi pi-check', severity: 'success'}
            case ProjectStatusChoices.Aborted:
                return {value: 'Aborted', icon: 'pi pi-times', severity: 'danger'}
            default: 
                throw new Error(`Unknown status: ${status}`);
        }
    };

    grantNewAuthorization(event: Event, member: ProjectMember) {
        this.authDialogMember.set(member)
        this.authDialogValidityPeriod.set([])
        this.authDialogConfirmation.set(false)
        this.#confirmationService.confirm({
            target: event.target as EventTarget,
            closable: true,
            key: 'authorize',
            closeOnEscape: true,
            accept: () => {
                this.#projectsService.createProjectDataManagerGrant({
                    projectId: this.projectId(),
                    memberId: member.id,
                    projectDataManagerGrantCreate: {
                        validityPeriod: {
                            start: this.authDialogValidityPeriod()[0].toISOString().split('T')[0],
                            end: this.authDialogValidityPeriod()[1].toISOString().split('T')[0],
                        }
                    }
                }).subscribe({
                    complete: () => {
                        this.#messageService.add({ severity: 'success', summary: 'Authorization', detail: 'Successfully updated authorization for ' + member.fullName });
                        this.project.reload()    
                    }
                })
                
            },
            reject: () => {},
        });
    };

    
    revokeAuthorization(event: Event, member: ProjectMember) {
        this.#confirmationService.confirm({
            target: event.target as EventTarget,
            key: 'revoke',
            closable: true,
            message: `Do you want to revoke ${member.fullName} data management authorization?`,
            icon: 'pi pi-info-circle',
            rejectButtonProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptButtonProps: {
                label: 'Delete',
                severity: 'danger'
            },
            accept: () => this.#projectsService.revokeProjectDataManagerGrant({
                    projectId: this.projectId(),
                    memberId: member.id,
                    grantId: member.authorization.id
                }).subscribe({
                    complete: () => {
                        this.#messageService.add({ severity: 'info', summary: 'Confirmed', detail: 'Authorization revoked for ' + member.fullName })
                        this.project.reload()
                    }
                }),
            reject: () => {}
        });
    }
    

    confirmMemberRemoval(event: Event, member: ProjectMember) {
        this.#confirmationService.confirm({
            key: 'remove',
            header: 'Danger Zone',
            message: 'Do you want to remove ' + member.fullName + ' from the project?',
            icon: 'pi pi-info-circle',
            rejectButtonProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptButtonProps: {
                label: 'Delete',
                severity: 'danger'
            },
            accept: () => {
                const members = this.project.value()?.members?.filter(m => m !== member.username) || []
                this.updateProjectMembers(members)
            },
        });
    }

    addMember(member: string) {
        this.updateProjectMembers([...(this.project.value()?.members || []), member])
    }

    private updateProjectMembers(members: string[]) {
        const payload = {
                leader: this.project.value()?.leader,
                status: this.project.value()?.status,
                title: this.project.value()?.title,
                summary: this.project.value()?.description,
                clinicalCenters: this.project.value()?.clinicalCenters,
                ethicsApprovalNumber: this.project.value()?.ethicsApprovalNumber,
                members: members
            } as ProjectCreate
        this.#projectsService.updateProjectById({
            projectId: this.projectId(),
            projectCreate: payload
        }).subscribe({
            complete: () => {
                this.#messageService.add({ severity: 'success', summary: 'Project update', detail: 'Successfully updated project members.' })
                this.project.reload()
            }
        })
    }

}