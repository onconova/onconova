import { Component, computed, ElementRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BASE_PATH } from 'onconova-api-client';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { MenuItem } from 'primeng/api';
import { MenuModule } from 'primeng/menu';

@Component({
    selector: 'onconova-sidebar-menu',
    template: `
        <div class="onconova-layout-sidebar">
            <p-menu [model]="navigationMenuItems()" />
        </div>
    `,
    imports: [
        MenuModule,
        CommonModule,
    ]
})
export class AppSidebarMenuComponent {

    // Injected services and variables
    readonly #authService = inject(AuthService);
    readonly #basePath: string = inject(BASE_PATH);
    public el = inject(ElementRef);


    private readonly currenUser = computed(() => this.#authService.user());
    #accessLevel = computed(() => this.currenUser()?.accessLevel || 0); 
    public readonly navigationMenuItems = computed<MenuItem[]>(() => {
        let items: MenuItem[] = [
            {
                label: 'Home',
                items: [
                    { 
                        label: 'Dashboard', 
                        icon: 'pi pi-fw pi-home', 
                        routerLink: ['/dashboard'], 
                    }
                ]
            },
            {
                label: 'Data Hub',
                items: [
                    { 
                        label: 'Case Explorer', 
                        icon: 'pi pi-fw pi-search', 
                        routerLink: ['/cases/search'],
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'My Contributions', 
                        icon: 'pi pi-fw pi-bookmark', 
                        routerLink: ['/cases/search'],
                        queryParams: { contributor: this.currenUser()?.username },
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'Upload Cases', 
                        icon: 'pi pi-fw pi-file-import', 
                        routerLink: ['/cases/import'],
                        disabled: this.#accessLevel() == 0,
                    },
                ]
            },
            {
                label: 'Research Management',
                items: [
                    { 
                        label: 'Project Explorer', 
                        icon: 'pi pi-fw pi-graduation-cap', 
                        routerLink: ['/projects/search'],
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'My Projects', 
                        icon: 'pi pi-fw pi-bookmark', 
                        routerLink: ['/projects/search'],
                        queryParams: { member: this.currenUser()?.username },
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'Cohort Explorer', 
                        icon: 'pi pi-fw pi-users', 
                        routerLink: ['/cohorts/search'],
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'My Cohorts', 
                        icon: 'pi pi-fw pi-bookmark', 
                        routerLink: ['/cohorts/search'],
                        queryParams: { contributor: this.currenUser()?.username },
                        disabled: this.#accessLevel() == 0,
                    },
                ]
            },
            {
                label: 'Documentation',
                items: [
                    { 
                        label: 'API Specification', 
                        icon: 'pi pi-fw pi-book', 
                        url: `${this.#basePath}/api/v1/docs#/`,
                    },
                ]
            }
        ];
        if (this.#accessLevel() && this.#accessLevel()>=3) {
            items = [...items, 
                {
                    label: 'Administration',
                    items: [
                        { label: 'Users', icon: 'pi pi-fw pi-users', disabled:!this.currenUser().canManageUsers, routerLink: ['/admin/users'] },
                    ]
                }
            ]
        }
        return items
    });
}

