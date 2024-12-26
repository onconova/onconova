import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';

@Component({
    standalone: true,
    imports: [
        RouterModule,
        CommonModule,
        ButtonModule,
    ],
    selector: 'app-access',
    templateUrl: './access.component.html',
})
export class AccessComponent { }
