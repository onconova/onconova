import { CommonModule } from "@angular/common";
import { Component, inject, input } from "@angular/core";
import { rxResource } from "@angular/core/rxjs-interop";
import { Skeleton } from "primeng/skeleton";
import { TableModule } from "primeng/table";
import { TagModule } from "primeng/tag";
import { forkJoin, from, map, mergeMap, toArray } from "rxjs";
import { UserBadgeComponent } from "src/app/shared/components/user-badge/user-badge.component";
import { ProjectsService, ProjectStatusChoices, UsersService } from "src/app/shared/openapi";

@Component({
    selector: 'pop-project-management',
    templateUrl: './project-management.component.html',
    imports: [
        CommonModule,
        Skeleton,
        UserBadgeComponent,
        TagModule,
        TableModule,
    ]
})
export class ProjectManagementComponent {
    
    readonly projectId = input.required<string>();
    
    readonly #projectsService = inject(ProjectsService)
    readonly #userService = inject(UsersService)

    protected project = rxResource({
        request: () => ({projectId: this.projectId()}),
        loader: ({request}) => this.#projectsService.getProjectById(request)
    }) 
    
    protected members = rxResource({
        request: () => ({usernameAnyOf: this.project.value()?.members ?? []}),
        loader: ({request}) => this.#userService.getUsers(request).pipe(
            map(response => response.items),       
            mergeMap(users => from(users)),
            mergeMap(user =>
                forkJoin({
                grant: this.#projectsService.getProjectDataManagerGrant({projectId: this.projectId(), memberId: user.id}).pipe(map(response => response.items[0])),
                }).pipe(
                map(results => ({
                    user,
                    ...results
                }))
                )
            ),
            toArray() // collect all the combined results into a single array
        )
    })

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
    }
}