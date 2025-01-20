import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { PatientCaseBundle } from 'src/app/shared/openapi';

import { MessageService } from 'primeng/api';
import { FileUpload } from 'primeng/fileupload';
import { Panel } from 'primeng/panel';
import { Button } from 'primeng/button';
import { TabsModule } from 'primeng/tabs';
import { SelectButtonModule } from 'primeng/selectbutton';
import { StepperModule } from 'primeng/stepper';

import { NgxJsonViewerModule } from 'ngx-json-viewer';

@Component({
    standalone: true,
    selector: 'app-case-importer',
    templateUrl: 'case-importer.component.html',
    imports:  [
        FileUpload,
        CommonModule,
        FormsModule,
        NgxJsonViewerModule,
        Button,
        SelectButtonModule,
        StepperModule,
        TabsModule,
        Panel,
    ],
})
export class CaseImporterComponent {
    public jsonContent: any = null;
    private readonly messageService: MessageService = inject(MessageService);
    public importFormat: string = 'pop+json' 
    public readonly importOptions: any[] = [
        { label: 'POP JSON', value: 'pop+json' },
        { label: 'FHIR JSON', value: 'fhir+json'  }
    ];

    
    onFileChange(event: any): void {
        console.log('UPLOADED')
        const file = event.target.files[0];
        const isValid = (value: PatientCaseBundle): value is PatientCaseBundle => !!value?.id;

        if (file) {
        const reader = new FileReader();
        reader.onload = (e: any) => {
            try {
            const jsonData = JSON.parse(e.target.result);

                // Validate against schema
                if (isValid(jsonData)) {
                    this.jsonContent = jsonData;
                    this.messageService.add({ severity: 'success', summary: 'Validation', detail: 'JSON is valid' });
                } else {
                    this.messageService.add({ severity: 'error', summary: 'Validation', detail: 'JSON is invalid' });
                }
            } catch (error) {
            this.jsonContent = null;
            this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to parse JSON.' });
            }
        };

        reader.readAsText(file);
        }
    }


}