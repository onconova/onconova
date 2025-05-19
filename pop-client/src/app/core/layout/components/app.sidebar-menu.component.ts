import { Component, computed, ElementRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BASE_PATH } from 'src/app/shared/openapi';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { MenuItem } from 'primeng/api';
import { MenuModule } from 'primeng/menu';

@Component({
    selector: 'pop-sidebar-menu',
    template: `
        <div class="pop-layout-sidebar">
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

    #accessLevel = computed(() => this.#authService.user().accessLevel || 0); 

    private readonly currenUser = computed(() => this.#authService.user());
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
                label: 'Cases',
                items: [
                    { 
                        label: 'Search Cases', 
                        icon: 'pi pi-fw pi-search', 
                        routerLink: ['/cases/search'],
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'My Cases', 
                        icon: 'pi pi-fw pi-search-plus', 
                        routerLink: ['/cases/search/', this.currenUser().username],
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'Import', 
                        icon: 'pi pi-fw pi-file-import', 
                        routerLink: ['/cases/import'],
                        disabled: this.#accessLevel() == 0,
                    },
                ]
            },
            {
                label: 'Cohorts',
                items: [
                    { 
                        label: 'Search Cohorts', 
                        icon: 'pi pi-fw pi-users', 
                        routerLink: ['/cohorts/search'],
                        disabled: this.#accessLevel() == 0,
                    },
                    { 
                        label: 'My Cohorts', 
                        icon: 'pi pi-fw pi-user', 
                        routerLink: ['/cohorts/search/', this.currenUser().username],
                        disabled: this.#accessLevel() == 0,
                    },
                ]
            },
            {
                label: 'Documentation',
                items: [
                    { 
                        label: 'User manual', 
                        icon: 'pi pi-fw pi-book', 
                        url: `/notfound`,
                        disabled: true
                    },
                    { 
                        label: 'API Specification', 
                        icon: 'pi pi-fw pi-book', 
                        url: `${this.#basePath}/api/docs#/`,
                    },
                ]
            }
        ];
        if (this.currenUser().accessLevel && (this.currenUser().accessLevel || 0)>=5) {
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

