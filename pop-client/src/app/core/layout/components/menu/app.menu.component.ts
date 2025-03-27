import { OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AuthService } from 'src/app/core/auth/services/auth.service';

import { BASE_PATH } from 'src/app/shared/openapi';
import { AppMenuitemComponent } from './components/menuitem/app.menuitem.component';
import { MenuItem } from 'primeng/api';

@Component({
    standalone: true,
    selector: 'pop-menu',
    templateUrl: './app.menu.component.html',
    imports: [
        CommonModule,
        AppMenuitemComponent
    ],
})
export class AppMenuComponent implements OnInit {

    model: MenuItem[] = [];
    private readonly authService: AuthService = inject(AuthService);
    private readonly basePath: string = inject(BASE_PATH);

    ngOnInit() {
        this.model = [
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
                    { label: 'My Cases', icon: 'pi pi-fw pi-search-plus', routerLink: ['/cases/search/', this.authService.getUsername()] },
                    { label: 'Import', icon: 'pi pi-fw pi-file-import', routerLink: ['/cases/import'] },
                ]
            },
            {
                label: 'Cohorts',
                items: [
                    { label: 'Search Cohorts', icon: 'pi pi-fw pi-users', routerLink: ['/cohorts/search'] },
                    { label: 'My Cohorts', icon: 'pi pi-fw pi-user', routerLink: ['/cohorts/search/', , this.authService.getUsername()] },
                ]
            },
            {
                label: 'Documentation',
                items: [
                    { label: 'User manual', icon: 'pi pi-fw pi-book', url: `/notfound`},
                    { label: 'API Specification', icon: 'pi pi-fw pi-book', url: `${this.basePath}/api/docs#/`},
                ]
            }
        ];
        if (this.authService.user.accessLevel && this.authService.user.accessLevel>=5) {
            this.model = [...this.model, 
                {
                    label: 'Administration',
                    items: [
                        { label: 'Users', icon: 'pi pi-fw pi-users', disabled:!this.authService.user.canManageUsers, routerLink: ['/admin/users'] },
                    ]
                }
            ]
        }
    }

}
