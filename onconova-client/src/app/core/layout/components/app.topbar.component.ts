import { Component, computed, ElementRef, inject, viewChild, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MenuItem, MessageService } from 'primeng/api';
import { LayoutService } from "../app.layout.service";
import packageInfo from '../../../../../package.json';
import { AuthService } from '../../auth/services/auth.service';
import { Router } from '@angular/router';
import { Key } from 'lucide-angular';
import { SettingsDialogComponent } from './app.settings.component';
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
import { Divider } from 'primeng/divider';

@Component({
    selector: 'onconova-topbar',
    providers: [
        MessageService
    ],
    imports: [
        CommonModule,
        Avatar,
        Menu,
        Button,
        InlineSVGModule,
        Divider,
        SettingsDialogComponent,
        GetFullNamePipe,
        GetNameAcronymPipe,
    ],
    template: `
        <div #topbar class="layout-topbar">
            <a class="layout-topbar-logo" routerLink="">
                <div [inlineSVG]="logo" alt="logo" class="onconova-logo mr-3"></div>
                <div>
                    <div class="layout-topbar-title onconova-title">
                        Onconova
                    </div>
                    <div class="layout-topbar-version">
                        Precision Oncology Platform
                    </div>
                </div>
            </a>
        
            <button #menubutton class="p-link layout-menu-button layout-topbar-button" (click)="onMenuToggle()">
                <i class="pi pi-bars"></i>
            </button>

            <div #topbarmenubutton class="layout-topbar-menu-button">
                 <ng-template [ngTemplateOutlet]="topbarbuttons"></ng-template>
            </div>

            <div class="layout-topbar-menu">
                 <ng-template [ngTemplateOutlet]="topbarbuttons"></ng-template>
            </div>
        </div>
        <onconova-settings-dialog></onconova-settings-dialog>

        <ng-template #topbarbuttons>
                <p-button [icon]="darkMode() ? 'pi pi-moon' : 'pi pi-sun'" [rounded]="true" [outlined]="true" (onClick)="toggleDarkMode()" class="my-auto mr-3 btn-secondary"/>
                <p-button icon="pi pi-user" [rounded]="true" (onClick)="profile.toggle($event)" />
        </ng-template>

        <p-menu #profile class="onconova-profile-menu" [model]="profileItems()" [popup]="true">
            <ng-template #start>
                <div class="flex flex-column m-3 text-center">    
                    @if (currentUser().isProvided) {
                        <div class="text-muted text-sm">
                            <i class="pi pi-{{currentUser().provider}} mr-2"></i>{{currentUser().provider | titlecase}} account
                        </div>
                    }
                    <p-avatar label="{{ currentUser() | acronym }}" size="large" shape="circle" class="layout-tobbar-menu-avatar"/>
                    <div class="flex-col my-auto">
                        <div class="font-semibold mb-0 mt-1">{{currentUser() | fullname}}</div>
                        <div class="text-muted text-sm mb-2">{{currentUser().email || 'Email unknown'}}</div>

                    </div>
                </div>
                <p-divider><span class="p-divider-text text-sm">Access level</span></p-divider>
                <div class="flex flex-column m-3 text-center">    
                    <div class="">
                        <i class="pi pi-lock text-muted"></i> {{ currentUser().accessLevel }} - {{currentUser().role}}
                    </div>
                </div>
                <p-divider><span class="p-divider-text text-sm">Management</span></p-divider>
            </ng-template>
        </p-menu>
    `
})
export class AppTopBarComponent {

    // Injected services
    readonly #dialogService = inject(DialogService);
    readonly #authService = inject(AuthService);
    readonly #layoutService = inject(LayoutService);
    #modalFormRef: DynamicDialogRef | undefined;
    
    // Computed properties
    public readonly currentUser = computed(() => this.#authService.user())
    public readonly version = packageInfo.version;

    // View child references
    public menuButtonRef = viewChild<ElementRef>('menubutton');
    public topbarMenuButtonRef = viewChild<ElementRef>('topbarmenubutton');
    public menuRef = viewChild<ElementRef>('topbarmenu');
    public settingsDialogRef = viewChild(SettingsDialogComponent);
        
    // Other component properties
    public readonly logo = this.#layoutService.logo;
    public readonly organizationName = environment.organizationName;
    public readonly darkMode = this.#layoutService.config.darkMode;
    public readonly isProduction: boolean = environment.production;
    public readonly isSidebarVisible = computed(() => this.#layoutService.isProfileSidebarVisible);
    public readonly profileItems = computed<MenuItem[]>(() => [
        {
            label: 'Preferences',
            icon: 'pi pi-cog',
            command: () => this.showSettingsDialog()
        },
        {
            label: 'Change password',
            icon: 'pi pi-key',
            disabled: this.currentUser()?.isProvided,
            command: () => this.openPasswordResetForm(),
        },
        {
            label: 'Logout',
            icon: 'pi pi-sign-out',
            command: () => this.logout()
        },
    ])

    onMenuToggle() {
        this.#layoutService.onMenuToggle();
    }

    showProfileSidebar() {
        this.#layoutService.showProfileSidebar();
    }

    toggleDarkMode() {
        this.#layoutService.toggleDarkMode()
    }
    

    showSettingsDialog() {
        this.settingsDialogRef()?.visible.set(true);
    }

    openPasswordResetForm() {
        this.#modalFormRef = this.#dialogService.open(PasswordResetFormComponent, {
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
            styleClass: 'onconova-modal-form',
            breakpoints: {
                '1700px': '50vw',
                '960px': '75vw',
                '640px': '90vw'
            },
        })
        this.#modalFormRef.onClose.subscribe((data: any) => {
            if (data?.saved) {
                this.logout
            }
        })    
    }
    
    logout() {
        this.#authService.logout()
    }
    
}
