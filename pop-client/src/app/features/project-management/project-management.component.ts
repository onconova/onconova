import { CommonModule } from "@angular/common";
import { Component, computed, inject, input, signal } from "@angular/core";
import { rxResource } from "@angular/core/rxjs-interop";
import { FormsModule } from "@angular/forms";
import { ConfirmationService, MenuItem, MessageService } from "primeng/api";
import { Button } from "primeng/button";
import { ConfirmDialog } from "primeng/confirmdialog";
import { DatePicker } from "primeng/datepicker";
import { Fluid } from "primeng/fluid";
import { Menu } from "primeng/menu";
import { Skeleton } from "primeng/skeleton";
import { TableModule } from "primeng/table";
import { TagModule } from "primeng/tag";
import { ToggleSwitch } from "primeng/toggleswitch";
import { forkJoin, from, map, mergeMap, Observable, toArray } from "rxjs";
import { UserBadgeComponent } from "src/app/shared/components/user-badge/user-badge.component";
import { Period, ProjectDataManagerGrant, ProjectsService, ProjectStatusChoices, User, UsersService } from "src/app/shared/openapi";

interface ProjectMember extends User {
    authorization: ProjectDataManagerGrant
}

@Component({
    selector: 'pop-project-management',
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
        ConfirmDialog,
        ToggleSwitch,
        TagModule,
        TableModule,
        DatePicker,
        Menu,
        Button,
    ]
})
export class ProjectManagementComponent {
    
    readonly projectId = input.required<string>();
    
    readonly #projectsService = inject(ProjectsService);
    readonly #userService = inject(UsersService);
    readonly #messageService = inject(MessageService);
    readonly #confirmationService = inject(ConfirmationService);

    protected project = rxResource({
        request: () => ({projectId: this.projectId()}),
        loader: ({request}) => this.#projectsService.getProjectById(request)
    });
    
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
    
    protected authDialogExpirationDuration = computed(() => {
        let duration: number = 0;
        if (this.authDialogValidityPeriod()[1]) {
            duration = this.getDaysDifference(this.authDialogValidityPeriod()![0], this.authDialogValidityPeriod()![1])
        } 
        return duration
    })

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

    getDaysDifference(start: Date, end: Date) {
        const oneDayMs = 1000 * 60 * 60 * 24; // milliseconds in one day
        const diffMs = end.getTime() - start.getTime();
        console.log(diffMs / oneDayMs)
        return Math.ceil(diffMs / oneDayMs);
    }

    getMemberMenuItems(member: ProjectMember): MenuItem[] {
        return [{
            label: 'Actions for ' + member.fullName,
            items: [
                {
                    label: 'Grant data management authorization',
                    icon: 'pi pi-plus',
                    disabled: (member?.accessLevel || 0) >= 4 || !!member.authorization,
                    command: (event: any) => {this.grantNewAuthorization(event, member)}
                },
                {
                    label: 'Revoke data management authorization',
                    disabled: (member?.accessLevel || 0) >= 4 || !member.authorization || (new Date(member.authorization.validityPeriod.end as string) < new Date()),
                    icon: 'pi pi-times',
                    command: (event: any) => {this.revokeAuthorization(event, member)}
                },
            ]
        }]
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
    

}