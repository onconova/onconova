import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { UsersService, User, UserCreate } from 'src/app/shared/openapi';
import { catchError, first, map, of, tap } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { UserFormComponent } from '../../forms/user-form/user-form.component';
import { PasswordResetFormComponent } from '../../forms/passwrd-reset-form/password-reset-form.component';
import { ModalFormHeaderComponent } from 'src/app/features/forms/modal-form-header.component';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { Key, User as UserIcon } from 'lucide-angular';
import { rxResource } from '@angular/core/rxjs-interop';
import { MessageService } from 'primeng/api';

@Component({
    selector: 'pop-users-management',
    templateUrl: './users-management.component.html',
    imports: [
        CommonModule,
        FormsModule,
        TableModule,
        ButtonModule,
        Skeleton,
        CardModule,
    ]
})
export class UsersManagementCompnent {

    // Injected services
    readonly #usersService = inject(UsersService);
    readonly #messageService = inject(MessageService); 
    readonly #dialogservice = inject(DialogService);

    // Resources
    public queryFilters = signal({})
    public users = rxResource({
        request: () => ({ ...this.queryFilters(), limit: this.pagination().limit, offset: this.pagination().offset}),
        loader: ({request}) => this.#usersService.getUsers(request).pipe(
            tap(page => this.totalUsers.set(page.count)),
            map(page => page.items),
            catchError((error: any) => {
                this.#messageService.add({ severity: 'error', summary: 'Error loading users', detail: error?.error?.detail });
                return of([] as User[]) 
            })
        )
    })

    // Pagination and search settings
    public readonly pageSizeChoices: number[] = [10, 20, 50, 100];
    public pagination = signal({limit: this.pageSizeChoices[0], offset: 0});
    public totalUsers= signal(0);
    public currentOffset: number = 0;

    // Modal form config
    #modalFormConfig = computed( () => ({
        templates: {
            header: ModalFormHeaderComponent,
        },   
        modal: true,
        closable: true,
        width: '45vw',
        styleClass: 'pop-modal-form',
        breakpoints: {
            '1700px': '50vw',
            '960px': '75vw',
            '640px': '90vw'
        },
    }))
    #modalFormRef: DynamicDialogRef | undefined;

    public openUserForm(initialData: UserCreate | {}) {    
        this.#modalFormRef = this.#dialogservice.open(UserFormComponent, {
            inputValues: {
                initialData: initialData,
            },
            data: {
                title: 'User information',
                subtitle: "Update a user's data",
                icon: UserIcon,
            },
            ...this.#modalFormConfig()
        })
        this.reloadDataIfClosedAndSaved(this.#modalFormRef)
    }

    public openPasswordResetForm(isAdmin: boolean, user: User) {
        this.#modalFormRef = this.#dialogservice.open(PasswordResetFormComponent, {
            inputValues: {
                initialData: {isAdmin: isAdmin, user: user},
            },
            data: {
                title: 'User Password',
                subtitle: "Reset a user's password",
                icon: Key,
            },
            ...this.#modalFormConfig()
        })
        this.reloadDataIfClosedAndSaved(this.#modalFormRef)
    }

    applyFilters(event: any) {
        const filtersMap = new Map(Object.entries(event.filters).map(([field, filter]) => {
            // @ts-ignore
            const matchMode = filter.matchMode.charAt(0).toUpperCase() + filter.matchMode.slice(1);
            // @ts-ignore
            return [`${field}${matchMode}`, filter.value]
        }))
        this.queryFilters.set(Object.fromEntries(filtersMap))
    }

    reloadDataIfClosedAndSaved(modalFormRef: DynamicDialogRef) {
        modalFormRef.onClose.subscribe((data: any) => {
            if (data?.saved) {
                this.users.reload()
            }
        })    
    }
}


