import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { InteroperabilityService, PatientCaseBundle, PatientCasesService } from 'src/app/shared/openapi';

import { MessageService, TreeNode } from 'primeng/api';
import { Button } from 'primeng/button';
import { TabsModule } from 'primeng/tabs';
import { SelectButtonModule } from 'primeng/selectbutton';
import { StepperModule } from 'primeng/stepper';
import { ImageCompareModule } from 'primeng/imagecompare';
import { MessageModule } from 'primeng/message';
import { RadioButtonModule } from 'primeng/radiobutton';

import { NgxJsonViewerModule } from 'ngx-json-viewer';
import { NgxJdenticonModule } from 'ngx-jdenticon';
import { AvatarModule } from 'primeng/avatar';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { ToggleSwitch } from 'primeng/toggleswitch';
import { CaseImporterBundleViewerComponent } from './components/case-importer-bundle-viewer/case-importer-bundle-viewer.component';
import { first, mergeMap } from 'rxjs';

@Component({
    standalone: true,
    selector: 'pop-case-importer',
    templateUrl: 'case-importer.component.html',
    imports:  [
        CommonModule,
        FormsModule,
        NgxJsonViewerModule,
        InlineSVGModule,
        MessageModule,
        Button,
        ToggleSwitch,
        RadioButtonModule,
        NgxJdenticonModule,
        ImageCompareModule,
        AvatarModule,
        SelectButtonModule,
        StepperModule,
        TabsModule,
        CaseImporterBundleViewerComponent,
    ],
})
export class CaseImporterComponent {
    public bundle: PatientCaseBundle | null = null;
    public conflictingBundle: PatientCaseBundle | null = null;
    public bundleTree: TreeNode[] = [];
    private readonly messageService: MessageService = inject(MessageService);
    private readonly casesService: PatientCasesService = inject(PatientCasesService);
    private readonly interoperabilityService: InteroperabilityService = inject(InteroperabilityService);
    public readonly authService: AuthService = inject(AuthService);


    public readonly consentIllustration = 'assets/images/accessioning/consent.svg';
    public consentValid: boolean = false;
    public importFormat: string = 'pop+json' 
    public uploadedLoading: boolean = false;
    public uploadedFile: File | null = null;
    public readonly importOptions: any[] = [
        { label: 'POP JSON', value: 'pop+json' },
        { label: 'FHIR JSON', value: 'fhir+json'  }
    ];
    public conflictResolution!: string;

    
    onFileChange(event: any): void {
        this.bundle = null;
        this.uploadedFile = event.target.files[0];
        const isValid = (value: PatientCaseBundle): value is PatientCaseBundle => !!value?.id;

        if (this.uploadedFile && this.uploadedFile.name.endsWith('.json')) {
            const reader = new FileReader();
            reader.onload = (e: any) => {
                try {
                    const bundle = JSON.parse(e.target.result);
                    // Validate against schema
                    if (isValid(bundle)) {
                        this.uploadedLoading = true;
                        this.casesService.getPatientCaseByPseudoidentifier({pseudoidentifier: bundle.pseudoidentifier}).pipe(
                            mergeMap((response) => this.interoperabilityService.exportPatientCaseBundle({caseId: response.id}).pipe(first()))
                        ).subscribe({
                            next: (response) => {
                                this.conflictingBundle = response
                                this.messageService.add({ severity: 'warning', summary: 'Validation', detail: 'There is a conflict with your import' });                                
                            },
                            error: () => {
                                this.conflictingBundle = null
                            },
                            complete: () => {
                                this.bundle = bundle
                                this.uploadedLoading = false;
                                this.messageService.add({ severity: 'success', summary: 'Validation', detail: 'Succesfully uploaded the file' });
                            }
                        })
                    } else {
                    this.bundle = null;
                        this.messageService.add({ severity: 'error', summary: 'Validation', detail: 'Uploaded file is invalid' });
                    }
                } catch (error) {
                    this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to parse JSON.' });
                }
                if (this.bundle) {
                    this.bundleTree = this.constructBundleTree(this.bundle)
                }
            };
            reader.readAsText(this.uploadedFile);
        }
    }

    onImportBundle() {
        this.interoperabilityService.importPatientCaseBundle({patientCaseBundle: this.bundle!}).subscribe({
            next: () => {
                this.messageService.add({ severity: 'success', summary: 'Import', detail: 'Succesfully imported the file' });
            },
            error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error', detail: error.error.detail }),
        })    
    }

    private constructBundleTree(bundle: PatientCaseBundle): TreeNode[] {
        return Object.entries(bundle)
            .filter(([key,value]) => Array.isArray(value) && key!='updatedBy') // Only process array properties
            .map(([key,value]) => ({
                label: key
                    .replace(/([a-z])([A-Z])/g, '$1 $2')
                    .replace(/^./, (str) => str.toUpperCase()),
                type: 'category',
                children: value.map((item: any) => ({
                    label: item.description,
                    type: 'resource',
                    data: item,
                })),
            }));
    }
}