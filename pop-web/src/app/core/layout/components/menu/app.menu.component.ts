import { OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Location, LocationStrategy } from '@angular/common';
import { Component } from '@angular/core';
import { AuthService } from 'src/app/core/auth/services/auth.service';

import { BASE_PATH } from 'src/app/shared/openapi';
import { AppMenuitemComponent } from './components/menuitem/app.menuitem.component';

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

    model: any[] = [];
    private readonly authService: AuthService = inject(AuthService);
    private readonly location: Location = inject(Location);

    ngOnInit() {
        this.model = [
            {
                label: 'Home',
                items: [
                    { label: 'Dashboard', icon: 'pi pi-fw pi-home', routerLink: ['/dashboard'] }
                ]
            },
            {
                label: 'Case Management',
                items: [
                    { label: 'Search Cases', icon: 'pi pi-fw pi-search', routerLink: ['/cases/search'] },
                    { label: 'My Cases', icon: 'pi pi-fw pi-user', routerLink: ['/cases/search/', this.authService.getUsername()] },
                    { label: 'Import Case', icon: 'pi pi-fw pi-file-import', routerLink: ['/cases/import'] },
                ]
            },
            {
                label: 'Cohort Analysis',
                items: [
                    { label: 'Search Cohorts', icon: 'pi pi-fw pi-search', routerLink: ['/cohorts/search'] },
                    { label: 'My Cohorts', icon: 'pi pi-fw pi-user', routerLink: ['/cohorts/search/', , this.authService.getUsername()] },
                    { label: 'Cohort Extraction', icon: 'pi pi-fw pi-table', routerLink: ['/notfound'] },
                ]
            },
            {
                label: 'Others',
                items: [
                    { label: 'Terminology', icon: 'pi pi-fw pi-book', routerLink: ['/notfound'] },
                    { label: 'API Docs', icon: 'pi pi-fw pi-code', url: `https://localhost:4443/api/docs#/` },
                ]
            }
        ];
    }
}
