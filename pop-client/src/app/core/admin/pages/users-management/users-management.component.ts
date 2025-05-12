import { Component, computed, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { AuthService, User, UserCreate } from 'src/app/shared/openapi';
import { first, map } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { UserFormComponent } from '../../forms/user-form/user-form.component';
import { PasswordResetFormComponent } from '../../forms/passwrd-reset-form/password-reset-form.component';
import { ModalFormHeaderComponent } from 'src/app/features/forms/modal-form-header.component';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { Key, User as UserIcon } from 'lucide-angular';

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
export class UsersManagementCompnent implements OnInit {

    // Inject services
    private authService = inject(AuthService);
    readonly #dialogservice = inject(DialogService);

    // Properties
    public paginatedUsers!: User[];
    public users!: User;
    public loading: boolean = false;
    public pageSizeChoices: number[] = [10, 20, 50, 100];
    public pageSize: number = this.pageSizeChoices[0];
    public totalEntries: number = 0;
    public currentOffset: number = 0;

    ngOnInit() {
        this.refreshUsers()
    }

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
        const userFilters = Object.fromEntries(filtersMap)
        this.refreshUsers(userFilters)
    }

    public refreshUsers(filters = {}) {
        this.loading = true;
        this.authService.getUsers({limit: this.pageSize, offset: this.currentOffset, ...filters}).pipe(
            first(),
            map(response => {
                this.totalEntries = response.count;
                this.paginatedUsers = response.items;
                this.loading = false;
            }),
        ).subscribe()
    }

    reloadDataIfClosedAndSaved(modalFormRef: DynamicDialogRef) {
        modalFormRef.onClose.subscribe((data: any) => {
            if (data?.saved) {
                this.refreshUsers()
            }
        })    
    }

    public setPaginationAndRefresh(event: TableLazyLoadEvent) {
        if (this.currentOffset === event.first && this.pageSize === event.rows) return
        this.currentOffset = event.first as number;
        this.pageSize = event.rows as number;
        this.refreshUsers()
     }
}


