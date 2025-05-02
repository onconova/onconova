import { Component} from '@angular/core';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { CommonModule } from '@angular/common';
import { Card } from 'primeng/card';
import { Dialog } from 'primeng/dialog';
import { Button } from 'primeng/button';

@Component({
    selector: 'pop-disclaimer-banner',
    imports: [
        InlineSVGModule, CommonModule,
        Card, Dialog, Button
    ],
    template: `
        <p-card styleClass="pop-disclaimer-banner-card">
            <h5 class="mb-3 font-semibold">Remember · Research-use only</h5>
            <div class="pop-disclaimer-banner-content">
                <div class="pop-disclaimer-banner-content-text">
                    <div >
                        This platform is intended for <b>research and informational purposes</b> only.
                    </div>
                    <div class="mt-2">
                        The information and resources presented here are <b>not intended for use in diagnosing or treating health problems or diseases</b> under any circumstances.
                    </div>
                    <p-button icon="pi pi-info-circle" styleClass="my-3" (click)="disclaimerDialogVisible = true" label="View disclaimer" />
                    <div style="max-width: 35rem;">
                        <small class="text-muted"> 
                        *By using this platform, you are agreeing to comply with and be bound by the terms and conditions of use.    
                        </small>
                    </div>
                    <p-dialog 
                        header="Terms and Conditions of Use" 
                        [modal]="true" 
                        [(visible)]="disclaimerDialogVisible" 
                        [style]="{ width: '40rem' }">
                        <div class="flex items-center gap-4 mb-4">
                            By accessing and using this website, you agree to comply with and be bound by the following terms and conditions. The content provided on this platform is intended solely for general informational and research purposes. While we strive to ensure the information is accurate and reliable, we do not make any express or implied warranties about the accuracy, adequacy, validity, reliability, availability, or completeness of the content.
                            <br><br>
                            The information presented on this platform is provided in good faith. However, we do not accept any liability for any loss or damage incurred as a result of using the site or relying on the information provided. Your use of this site and any reliance on the content is solely at your own risk.
                            <br><br>                    
                            These terms and conditions may be updated from time to time, and it is your responsibility to review them regularly to ensure compliance.
                        </div>
                        <div class="flex justify-end gap-2">
                            <p-button label="Close" (click)="disclaimerDialogVisible = false" />
                        </div>
                    </p-dialog>
                </div>
                <div [inlineSVG]="illustration" class="pop-disclaimer-banner-illustration"></div>
            </div>
        </p-card>
    `
})
export class DisclaimerBannerComponent {
    
    public readonly illustration: string = 'assets/images/landing/researcher.svg';
    public disclaimerDialogVisible: boolean = false;

}
