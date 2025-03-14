import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { PatientCaseBundle, PatientCasesService } from 'src/app/shared/openapi';

import { MessageService, TreeNode } from 'primeng/api';
import { FileUpload } from 'primeng/fileupload';
import { Panel } from 'primeng/panel';
import { Button } from 'primeng/button';
import { TabsModule } from 'primeng/tabs';
import { SelectButtonModule } from 'primeng/selectbutton';
import { StepperModule } from 'primeng/stepper';

import { NgxJsonViewerModule } from 'ngx-json-viewer';
import { TreeModule } from 'primeng/tree';
import { Badge } from 'primeng/badge';
import { NgxJdenticonModule } from 'ngx-jdenticon';
import { AvatarModule } from 'primeng/avatar';
import { Divider } from 'primeng/divider';
import { AuthService } from 'src/app/core/auth/services/auth.service';

@Component({
    standalone: true,
    selector: 'pop-case-importer',
    templateUrl: 'case-importer.component.html',
    imports:  [
        CommonModule,
        FormsModule,
        NgxJsonViewerModule,
        Button,
        Badge,
        Divider,
        NgxJdenticonModule,
        AvatarModule,
        SelectButtonModule,
        StepperModule,
        TabsModule,
        Panel,
        TreeModule,
    ],
})
export class CaseImporterComponent {
    public bundle: PatientCaseBundle | null = null;
    public bundleTree: TreeNode[] = [];
    private readonly messageService: MessageService = inject(MessageService);
    private readonly casesService: PatientCasesService = inject(PatientCasesService);
    public readonly authService: AuthService = inject(AuthService);


    public importFormat: string = 'pop+json' 
    public uploadedFile: File | null = null;
    public readonly importOptions: any[] = [
        { label: 'POP JSON', value: 'pop+json' },
        { label: 'FHIR JSON', value: 'fhir+json'  }
    ];

    
    onFileChange(event: any): void {
        this.uploadedFile = event.target.files[0];
        const isValid = (value: PatientCaseBundle): value is PatientCaseBundle => !!value?.id;
        const isPopBundle = (value: PatientCaseBundle): value is PatientCaseBundle => !!value?.pseudoidentifier;

        if (this.uploadedFile) {
            const reader = new FileReader();
            reader.onload = (e: any) => {
                try {
                    const jsonData = JSON.parse(e.target.result);
                    // Validate against schema
                    if (isValid(jsonData) && isPopBundle(jsonData)) {
                        this.bundle = jsonData;
                        this.messageService.add({ severity: 'success', summary: 'Validation', detail: 'Succesfully uploaded the file' });
                    } else {
                        this.messageService.add({ severity: 'error', summary: 'Validation', detail: 'Uploaded file is invalid' });
                    }
                } catch (error) {
                    this.bundle = null;
                    this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to parse JSON.' });
                }
                if (this.bundle) {
                    console.log('AAAAA')
                    this.bundleTree = this.constructBundleTree(this.bundle)
                }
            };
            reader.readAsText(this.uploadedFile);
        }
    }

    onImportBundle() {
        this.casesService.importPatientCaseBundle({patientCaseBundle: this.bundle!}).subscribe({
            next: (response) => {
                this.messageService.add({ severity: 'success', summary: 'Import', detail: 'Succesfully imported the file' });
            },
            error: (error) => this.messageService.add({ severity: 'error', summary: 'Error', detail: error.message }),
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