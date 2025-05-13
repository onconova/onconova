import { Component, computed, ElementRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AppMenuitemComponent } from './app.menuitem.component';
import { BASE_PATH } from 'src/app/shared/openapi';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { MenuItem } from 'primeng/api';

@Component({
    selector: 'pop-sidebar-menu',
    template: `
        <ul class="layout-menu">
            @for (item of navigationMenuItems(); track item.label; let i = $index;) {
                @if (item.separator) {
                    <li class="menu-separator"></li>
                } @else {
                    <li pop-menuitem [item]="item" [index]="i" [root]="true"></li>
                }
            }
        </ul>
    `,
    imports: [
        CommonModule,
        AppMenuitemComponent
    ]
})
export class AppSidebarMenuComponent {

    // Injected services and variables
    readonly #authService = inject(AuthService);
    readonly #basePath: string = inject(BASE_PATH);
    public el = inject(ElementRef);

    private readonly currenUser = computed(() => this.#authService.user());
    public readonly navigationMenuItems = computed<MenuItem[]>(() => {
        let items: MenuItem[] = [
            {
                label: 'Home',
                items: [
                    { label: 'Dashboard', icon: 'pi pi-fw pi-home', routerLink: ['/dashboard'] }
                ]
            },
            {
                label: 'Cases',
                items: [
                    { label: 'Search Cases', icon: 'pi pi-fw pi-search', routerLink: ['/cases/search'] },
                    { label: 'My Cases', icon: 'pi pi-fw pi-search-plus', routerLink: ['/cases/search/', this.currenUser().username] },
                    { label: 'Import', icon: 'pi pi-fw pi-file-import', routerLink: ['/cases/import'] },
                ]
            },
            {
                label: 'Cohorts',
                items: [
                    { label: 'Search Cohorts', icon: 'pi pi-fw pi-users', routerLink: ['/cohorts/search'] },
                    { label: 'My Cohorts', icon: 'pi pi-fw pi-user', routerLink: ['/cohorts/search/', this.currenUser().username] },
                ]
            },
            {
                label: 'Documentation',
                items: [
                    { label: 'User manual', icon: 'pi pi-fw pi-book', url: `/notfound`},
                    { label: 'API Specification', icon: 'pi pi-fw pi-book', url: `${this.#basePath}/api/docs#/`},
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

