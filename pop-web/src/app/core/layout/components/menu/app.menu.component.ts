import { OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AuthService } from 'src/app/core/auth/services/auth.service';

import { AppMenuitemComponent } from './components/menuitem/app.menuitem.component';

@Component({
    standalone: true,
    selector: 'app-menu',
    templateUrl: './app.menu.component.html',
    imports: [
        CommonModule,
        AppMenuitemComponent
    ],
})
export class AppMenuComponent implements OnInit {

    model: any[] = [];
    private readonly authService: AuthService = inject(AuthService);

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
                    { label: 'Import Case', icon: 'pi pi-fw pi-file-import', routerLink: ['/uikit/formlayout'] },
                ]
            },
            {
                label: 'Cohort Analysis',
                items: [
                    { label: 'Cohort Builder', icon: 'pi pi-fw pi-hammer', routerLink: ['/uikit/formlayout'] },
                    { label: 'Cohort Analysis', icon: 'pi pi-fw pi-chart-bar', routerLink: ['/uikit/formlayout'] },
                    { label: 'Cohort Extraction', icon: 'pi pi-fw pi-table', routerLink: ['/uikit/formlayout'] },
                ]
            },
            {
                label: 'Others',
                items: [
                    { label: 'Terminology', icon: 'pi pi-fw pi-book', routerLink: ['/uikit/formlayout'] },
                    { label: 'API Docs', icon: 'pi pi-fw pi-code', routerLink: ['/uikit/formlayout'] },
                ]
            }
        ];
    }
}
