import { Component, computed, ElementRef, inject, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MenuItem, MessageService } from 'primeng/api';
import { LayoutService } from "../../app.layout.service";
import packageInfo from '../../../../../../package.json';
import { AuthService } from '../../../auth/services/auth.service';
import { Router } from '@angular/router';
import { Key } from 'lucide-angular';
import { SettingsDialogComponent } from '../settings/app.settings.component';
import { GetFullNamePipe } from 'src/app/shared/pipes/full-name.pipe';
import { GetNameAcronymPipe } from 'src/app/shared/pipes/name-acronym.pipe';

import { InlineSVGModule } from 'ng-inline-svg-2';

import { Avatar } from 'primeng/avatar';
import { Menu } from 'primeng/menu';
import { Button } from 'primeng/button';
import { PasswordResetFormComponent } from 'src/app/core/admin/forms/passwrd-reset-form/password-reset-form.component';
import { environment } from 'src/environments/environment';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormHeaderComponent } from 'src/app/features/forms/modal-form-header.component';

@Component({
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
    ]
})
export class AppTopBarComponent {

    readonly #router = inject(Router);
    readonly #messageService = inject(MessageService);
    readonly #dialogService = inject(DialogService);
    readonly #authService = inject(AuthService);
    public layoutService = inject(LayoutService);

    public isProduction: boolean = environment.production;
    public version = packageInfo.version;
    public themeModeIcon: 'pi pi-sun' | 'pi pi-moon' = 'pi pi-sun';
    public user = computed(() => this.#authService.user())
    #modalFormRef: DynamicDialogRef | undefined;

    @ViewChild('menubutton') menuButton!: ElementRef;
    @ViewChild('topbarmenubutton') topbarMenuButton!: ElementRef;
    @ViewChild('topbarmenu') menu!: ElementRef;
    @ViewChild(SettingsDialogComponent) settingsDialog!: SettingsDialogComponent;
         
    public profileItems: MenuItem[] = [
        {separator: true},
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
                        this.#dialogService.open(PasswordResetFormComponent, {
                            inputValues: {
                                initialData: {isAdmin: false, user: this.#authService.user()}
                            },
                            data: {
                                title: 'Reset password',
                                subtitle: 'Change existing password',
                                icon: Key,
                            },
                            templates: {
                                header: ModalFormHeaderComponent,
                            },   
                            modal: true,
                            closable: true,
                            width: '45vw',
                            styleClass: 'pop-modal-form',
                            breakpoints: {
                                '1700px': '50vw',
                                '960px': '75vw',
                                '640px': '90vw'
                            },
                        })
                        this.#modalFormRef!.onClose.subscribe((data: any) => {
                            if (data?.saved) {
                                this.logout
                            }
                        })                  
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


    showSettingsDialog() {
        this.settingsDialog.showDialog()
    }
    
    logout() {
        this.#authService.logout()
        this.#router.navigate(['auth','login'])
        this.#messageService.add({ severity: 'success', summary: 'Logout', detail: 'Succesful logout' });
    }
    
}
