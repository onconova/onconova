import { Component, inject, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';
import { FormsModule } from '@angular/forms';
import { LayoutService } from '../../app.layout.service';
import { ToggleSwitchModule } from 'primeng/toggleswitch';


@Component({
    selector: 'pop-settings-dialog',
    templateUrl: './app.settings.component.html',
    imports: [CommonModule, FormsModule, ToggleSwitchModule, Dialog, ButtonModule]
})
export class SettingsDialogComponent {

    public readonly layoutService = inject(LayoutService);
    public visible: boolean = false;

    public themes = [
        {name: 'emerald', color: 'emerald'},
        {name: 'green', color: 'green'},
        {name: 'lime', color: 'lime'},
        {name: 'red', color: 'red'},
        {name: 'orange', color: 'orange'},
        {name: 'amber', color: 'amber'},
        {name: 'yellow', color: 'yellow'},
        {name: 'teal', color: 'teal'},
        {name: 'cyan', color: 'cyan'},
        {name: 'sky', color: 'sky'},
        {name: 'blue', color: 'blue'},
        {name: 'indigo', color: 'indigo'},
        {name: 'violet', color: 'violet'},
        {name: 'purple', color: 'purple'},
        {name: 'fuchsia', color: 'fuchsia'},
        {name: 'pink', color: 'pink'},
        {name: 'rose', color: 'rose'},
    ]

    showDialog() {
        this.visible = true;
    }

}