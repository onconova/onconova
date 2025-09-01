import { Component, computed, inject, signal, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';
import { FormsModule } from '@angular/forms';
import { LayoutService } from '../app.layout.service';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { AuthService } from '../../auth/services/auth.service';


@Component({
    selector: 'onconova-settings-dialog',
    template: `
        <p-dialog header="Preferences" [modal]="true" [(visible)]="visible" [style]="{ width: '25rem' }">
            
            <div class="field">
                <span class="font-medium block mb-1">Data sharing consent</span>
                <small class="text-muted">Do you want your data to be shareable with other organizations for acreditation purposes.</small>
                <div class="flex mt-2">
                    <p-toggleswitch [ngModel]="dataShareable()" (ngModelChange)="updateUserConcent($event)"/>
                    <label class="my-auto ml-2 block" style="line-height: 0;">{{ darkMode() ? 'Yes' : 'No' }}</label>            
                </div>
            </div>
            <div class="field">
                <span class="font-medium block mb-1">Dark mode</span>
                <small class="text-muted">Enable dark mode for a darker interface that's easier on the eyes in low-light environments.</small>
                <div class="flex mt-2">
                    <p-toggleswitch [(ngModel)]="darkMode"/>
                    <label class="my-auto ml-2 block" style="line-height: 0;">{{ darkMode() ? 'Enabled' : 'Disabled' }}</label>            
                </div>
            </div>
            <div>        
                <span class="font-medium block mb-1">Color theme</span>
                <small class="text-muted">Choose your preferred color theme to personalize the look and feel of the interface. This will affect highlights, buttons, and other UI elements.</small>
                <div class="field-themes mt-2">
                    @for (theme of themes; track theme.color;) {
                        <p-button 
                        styleClass="theme-config-color-button "
                        (onClick)="colorTheme.set(theme.color)"
                        [style]="{background: 'var(--p-' + theme.color + '-500)'}" />
                    }
            </div>
        </div>
        </p-dialog>
    `,
    imports: [CommonModule, FormsModule, ToggleSwitchModule, Dialog, ButtonModule]
})
export class SettingsDialogComponent {

    readonly #layoutService = inject(LayoutService);
    readonly #authService = inject(AuthService);

    public dataShareable = computed(() => this.#authService.user()?.shareable)
    public darkMode = this.#layoutService.config.darkMode
    public colorTheme = this.#layoutService.config.theme
    public visible = signal<boolean>(false);

    public readonly themes = [
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

    updateUserConcent(shareable: boolean) {
        this.#authService.updateUserDataConsent(shareable)
    }

}