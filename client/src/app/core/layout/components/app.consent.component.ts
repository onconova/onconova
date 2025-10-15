import { Component, computed, inject, signal } from '@angular/core';
import { AuthService } from '../../auth/services/auth.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { DialogModule } from 'primeng/dialog';
import { Button } from 'primeng/button';
import { Card } from 'primeng/card';
import { UsersService } from 'onconova-api-client';

@Component({
    selector: 'onconova-consent-modal',
    imports: [FormsModule, CommonModule, DialogModule, Button, Card],
    template:  `
        <p-dialog 
            header="End-User Consent Notice & Terms for Data Collection" 
            [modal]="true" 
            [visible]="(currentUser().shareable == null) || (currentUser().shareable == undefined)" 
            [style]="{ width: '50rem' }" 
            [closable]="false"
            [breakpoints]="{ '1199px': '75vw', '575px': '90vw' }">
            <div class="text-sm">
                <h6>Data Collected</h6>
                <p>Onconova collects the following information to facilitate your use of this platform:</p>
                <ul>
                    <li>Username</li>
                    <li>Full name</li>
                    <li>Work email</li>
                    <li>Organization</li>
                </ul>
                <h6>Purpose of Collection</h6>
                <p>This information is collected to:</p>
                <ul>
                    <li>Identify you within the app</li>
                    <li>Accredit your contributions to the platform</li>
                    <li>Maintain a traceable audit trail of activities.</li>
                </ul>
                <p>Please note: Providing this information is necessary for using the application and cannot be opted out of.</p>

                <h6>Data Sharing</h6>
                <p>You can opt for your data to be shared with:</p>
                <ul>
                    <li>External or internal collaborators to be credited for your data contributions.</li>
                </ul>
                <p> If you opt out, your contributions will be anonymized for external collaborators, but you will not be directly creditable.</p> 

                <h6>Acceptance</h6>
                <p>
                    By checking any of the options below and continuing to use the app, you confirm thatYou understand and agree to the collection and sharing of your data as described above
                </p>
            </div>
            <p-card styleClass="card border-solid surface-border p-2 mt-3" header="Please read carefully">
                <b> 
                    Do you want your data to be shareable with other organizations for acreditation purposes?
                </b>
                <div class="flex gap-3 my-3">
                    <p-button (click)="authService.updateUserDataConsent(true)" label="Accept" [loading]="processing()" severity='success' styleClass="px-4"/>
                    <p-button (click)="authService.updateUserDataConsent(false)" label="Reject" [loading]="processing()" severity='danger' styleClass="px-4"/>
                </div>
                <p>
                You can later change your decision under <i>Preferences</i>.
                </p>
            </p-card>
        </p-dialog>
    `,
})
export class ConsentNoticeModalComponent {
    readonly authService = inject(AuthService);
    currentUser = computed(() => this.authService.user());
    processing = signal<boolean>(false);
}