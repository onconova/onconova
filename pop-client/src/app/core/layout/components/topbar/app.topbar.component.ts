import { Component, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MessageService } from 'primeng/api';
import { LayoutService } from "../../service/app.layout.service";
import packageInfo from '../../../../../../package.json';
import { AuthService } from '../../../auth/services/auth.service';
import { Router } from '@angular/router';

import { SettingsDialogComponent } from '../settings/app.settings.component';
import { GetFullNamePipe } from 'src/app/shared/pipes/full-name.pipe';
import { GetNameAcronymPipe } from 'src/app/shared/pipes/name-acronym.pipe';

import { InlineSVGModule } from 'ng-inline-svg-2';

import { Avatar } from 'primeng/avatar';
import { Menu } from 'primeng/menu';
import { Button } from 'primeng/button';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';
import { PasswordResetFormComponent } from 'src/app/core/admin/forms/passwrd-reset-form/password-reset-form.component';
import { ModalFormComponent } from 'src/app/shared/components/modal-form/modal-form.component';

@Component({
    standalone: true,
    selector: 'pop-topbar',
    templateUrl: './app.topbar.component.html',
    providers: [
        MessageService
    ],
    imports: [
        CommonModule,
        Avatar,
        Menu,
        Button,
        InlineSVGModule,
        SettingsDialogComponent,
        GetFullNamePipe,
        GetNameAcronymPipe,
        ModalFormComponent,
    ]
})
export class AppTopBarComponent {
    version = packageInfo.version;
    items!: any[];
    profile_items!: any[];
    themeModeIcon: 'pi pi-sun' | 'pi pi-moon' = 'pi pi-sun';


    @ViewChild('menubutton') menuButton!: ElementRef;

    @ViewChild('topbarmenubutton') topbarMenuButton!: ElementRef;

    @ViewChild('topbarmenu') menu!: ElementRef;
    
    @ViewChild(SettingsDialogComponent) settingsDialog!: SettingsDialogComponent;

    constructor(
        public layoutService: LayoutService,
        private router: Router,
        private messageService: MessageService,
        public authService: AuthService,
        private modalFormService: ModalFormService){
         
        this.profile_items = [
            {
                separator: true
            },
            {
                label: 'Menu',
                items: [
                    {
                        label: 'Preferences',
                        icon: 'pi pi-cog',
                        command: () => {
                            this.showSettingsDialog();
                        }
                    },
                    {
                        label: 'Change password',
                        icon: 'pi pi-key',
                        command: () => {
                            this.modalFormService.open(PasswordResetFormComponent, {isAdmin: false, user: this.authService.user}, this.logout);
                        }
                    },
                    {
                        label: 'Logout',
                        icon: 'pi pi-sign-out',
                        command: () => {
                            this.logout();
                        }
                    },
                ]
            },
        ];
    }


    ngOnInit(): void {
    }

    showSettingsDialog() {
        this.settingsDialog.showDialog()
    }
    
    logout() {
        this.authService.logout()
        this.router.navigate(['auth','login'])
        this.messageService.add({ severity: 'success', summary: 'Logout', detail: 'Succesful logout' });
    }
    
}
