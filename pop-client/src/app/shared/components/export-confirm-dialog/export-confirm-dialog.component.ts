import { Component, input, signal } from "@angular/core";
import { Button } from "primeng/button";
import { ConfirmDialog } from "primeng/confirmdialog";

@Component({
    selector: 'pop-export-confirm-dialog',
    imports: [Button],
    template: `
        <div class="confirmdialog-container" style="width: 50rem;">
            <div class="confirmdialog-icon">
                <i class="pi pi-exclamation-triangle text-6xl"></i>
            </div>
            <span class="font-semibold text-2xl block mb-2 mt-3">Data Access and Compliance Acknowledgement</span>
            <div class="m-auto text-center">
                You are initiating the download of anonymized but sensitive healthcare data. This activity will be recorded and linked 
                to your user credentials.<br/><br/>Prior to proceeding, <b>you are required to confirm that valid and current patient consent has been
                obtained for all cases included in the cohort</b>.<br/><br/>By continuing, you formally accept full responsibility for the lawful and
                compliant handling, use, storage, and eventual secure destruction of this data, in strict accordance with applicable data
                    protection legislation, institutional policies, and ethical standards. Unauthorized use or disclosure may result in disciplinary,
                civil, or criminal penalties.
            </div>
            <div class="flex items-center gap-2 my-3">
                <p-button label="Confirm" (onClick)="onAccept()()" styleClass="w-32"></p-button>
                <p-button label="Cancel" [outlined]="true" (onClick)="onReject()()" styleClass="w-32"></p-button>
            </div>
        </div>
    `,
})
export class ExportConfirmDialogComponent {
    public onAccept = input.required<() => void>()
    public onReject = input.required<() => void>()
}