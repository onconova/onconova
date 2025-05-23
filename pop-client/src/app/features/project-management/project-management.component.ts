import { CommonModule } from "@angular/common";
import { Component, inject, input, signal } from "@angular/core";
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
import { forkJoin, from, map, mergeMap, toArray } from "rxjs";
import { UserBadgeComponent } from "src/app/shared/components/user-badge/user-badge.component";
import { ProjectsService, ProjectStatusChoices, User, UsersService } from "src/app/shared/openapi";

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
            mergeMap(user =>
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

    protected authDialogMember = signal<User | null>(null);
    protected authDialogExpirationDate = signal<Date | null>(null);
    protected authDialogExpirationMinDate = new Date();
    protected authDialogExpirationMaxDate = new Date(this.authDialogExpirationMinDate.getTime() + 31 * 24 * 60 * 60 * 1000);


    getMemberMenuItems(member: User): MenuItem[] {
        return [{
            label: 'Actions for ' + member.fullName,
            items: [
                {
                    label: 'Revoke data management authorization',
                    disabled: (member?.accessLevel || 0) >= 4,
                    icon: 'pi pi-times',
                    command: () => {}
                },
                {
                    label: 'Give data management authorization',
                    icon: 'pi pi-plus',
                    disabled: (member?.accessLevel || 0) >= 4,
                    command: (event: any) => {this.grantNewAuthorization(event, member)}
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

    grantNewAuthorization(event: Event, member: User) {
        this.authDialogMember.set(member)
        this.#confirmationService.confirm({
            target: event.target as EventTarget,
            closable: true,
            closeOnEscape: true,
            accept: () => {
                this.#messageService.add({ severity: 'info', summary: 'Confirmed', detail: 'You have accepted' });
            },
            reject: () => {
                this.#messageService.add({
                    severity: 'error',
                    summary: 'Rejected',
                    detail: 'You have rejected',
                    life: 3000,
                });
            },
        });
    };

}