import { Component, ElementRef } from '@angular/core';
import { LayoutService } from "../../service/app.layout.service";

import { CommonModule } from '@angular/common';
import { AppMenuComponent } from '../menu/app.menu.component';

@Component({
    standalone: true,
    selector: 'app-sidebar',
    templateUrl: './app.sidebar.component.html',
    imports: [
        CommonModule,
        AppMenuComponent,

    ],
})
export class AppSidebarComponent {
    constructor(public layoutService: LayoutService, public el: ElementRef) { }
}

