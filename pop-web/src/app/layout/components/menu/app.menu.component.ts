import { OnInit } from '@angular/core';
import { Component } from '@angular/core';
import { LayoutService } from '../../service/app.layout.service';

@Component({
    selector: 'app-menu',
    templateUrl: './app.menu.component.html'
})
export class AppMenuComponent implements OnInit {

    model: any[] = [];

    constructor(public layoutService: LayoutService) { }

    ngOnInit() {
        this.model = [
            {
                label: 'Home',
                items: [
                    { label: 'Dashboard', icon: 'pi pi-fw pi-home', routerLink: ['/dashboard'] }
                ]
            },
            {
                label: 'Data Management',
                items: [
                    { label: 'New Case', icon: 'pi pi-fw pi-plus', routerLink: ['/uikit/formlayout'] },
                    { label: 'Import Case', icon: 'pi pi-fw pi-file-import', routerLink: ['/uikit/formlayout'] },
                    { label: 'Case Browser', icon: 'pi pi-fw pi-search', routerLink: ['/cases'] },
                    { label: 'My Cases', icon: 'pi pi-fw pi-user', routerLink: ['/cases/browser'] },
                ]
            },
            {
                label: 'Data Analysis',
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
