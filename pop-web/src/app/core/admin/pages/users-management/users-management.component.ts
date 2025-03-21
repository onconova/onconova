import { Component, inject, OnInit } from '@angular/core';
import { MessageService } from 'primeng/api';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { AuthService, User, UserCreate } from 'src/app/shared/openapi';
import { first, map, Observable, of } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';
import { UserFormComponent } from '../../forms/user-form/user-form.component';
import { ModalFormComponent } from 'src/app/shared/components/modal-form/modal-form.component';
import { PasswordResetFormComponent } from '../../forms/passwrd-reset-form/password-reset-form.component';

@Component({
    standalone: true,
    selector: 'pop-users-management',
    templateUrl: './users-management.component.html',
    imports:[
        CommonModule,
        FormsModule,
        TableModule,
        ButtonModule,
        Skeleton,
        CardModule,
        ModalFormComponent,
        PasswordResetFormComponent,
    ]
})
export class UsersManagementCompnent implements OnInit {

    // Inject services
    private authService = inject(AuthService);
    private modalFormService = inject(ModalFormService)

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


    public openUserForm(initialData: UserCreate | {}) {    
        this.modalFormService.open(UserFormComponent, initialData, this.refreshUsers.bind(this));
    }
    public openPasswordResetForm(isAdmin: boolean, user: User) {
        this.modalFormService.open(PasswordResetFormComponent, {isAdmin: isAdmin, user: user}, this.refreshUsers.bind(this));
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

    public setPaginationAndRefresh(event: TableLazyLoadEvent) {
        if (this.currentOffset === event.first && this.pageSize === event.rows) return
        this.currentOffset = event.first as number;
        this.pageSize = event.rows as number;
        this.refreshUsers()
     }
}


