import { CommonModule } from "@angular/common";
import { Component, inject, Input, ViewEncapsulation } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { forkJoin, map, Observable, of, take } from "rxjs";

import JSZip from 'jszip';

import { Menu } from "primeng/menu";
import { MegaMenu } from 'primeng/megamenu';
import { MegaMenuItem, MenuItem } from "primeng/api";
import { TableModule } from 'primeng/table';
import { Avatar } from "primeng/avatar";
import { Button } from "primeng/button";
import { Toolbar } from "primeng/toolbar";
import { MessageService } from "primeng/api";

import openApiSchema from "../../../../openapi.json"; // Import OpenAPI JSON (if possible)
import { CohortsService } from "src/app/shared/openapi";
import { NestedTableComponent } from "src/app/shared/components";
import { NgxJdenticonModule } from "ngx-jdenticon";
import { AuthService } from "src/app/core/auth/services/auth.service";
import { CamelCaseToTitleCasePipe } from "src/app/shared/pipes/camel-to-title-case.pipe";

@Component({
    standalone: true,
    selector: 'pop-dataset-composer',
    templateUrl: './dataset-composer.component.html',
    styleUrl: './dataset-composer.component.css',
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        Avatar,
        Button,
        Toolbar,
        Menu,
        MegaMenu,
        TableModule,
        NgxJdenticonModule,
        NestedTableComponent,
        CamelCaseToTitleCasePipe,
    ],
    encapsulation: ViewEncapsulation.None,
})
export class DatasetComposerComponent {


    getColumns(data: any[]): string[] {
        const allKeys = new Set<string>();
        data.forEach(item => Object.keys(item).forEach(key => allKeys.add(key)));
        return Array.from(allKeys);
    }

    isNested(value: any): boolean {
        return typeof value === 'object' && value !== null;
    }
    // ==========================================

    public authService = inject(AuthService);
    private cohortService = inject(CohortsService);
    private messageService = inject(MessageService);

    @Input({required: true}) cohortId!: string;

    public datasetRules: any[] = []
    public pageSizeChoices: number[] = [10, 20, 50, 100];
    public pageSize: number = this.pageSizeChoices[0];
    public totalEntries: number = 0;

    public currentOffset: number = 0;
    public dataset$: Observable<any[]> = of([]);

    // Extract keys from OpenAPI schema
    private apiSchemaKeys = Object.fromEntries(
      Object.entries(openApiSchema.components.schemas).map(([key, schema]: any) => [
        key,
        Object.keys(schema.properties || {}).filter(property => !this.createMetadataItems('').map(item => item['field']).includes(property) && !['caseId', 'description'].includes(property))
            .map(property => this.createMenuItem(key, schema.properties[property].title, property, schema.properties[property].type) )
      ])
    )
    

    public resourceItems: MegaMenuItem[] = [
        {label: 'Patient Case', items: this.createSchemaMegaMenuItems('PatientCase')},
        {label: 'Neoplastic Entities', items: this.createSchemaMegaMenuItems('NeoplasticEntity')},
        {label: 'Stagings', items: this.createSchemaMegaMenuItems('AnyStaging')},
        {label: 'Risk assessments', items: this.createSchemaMegaMenuItems('RiskAssessment')},
        {label: 'Therapy Lines', items: this.createSchemaMegaMenuItems('TherapyLine')},
        {label: 'Systemic Therapy', items: [
            this.createSchemaMegaMenuItems('SystemicTherapy', ['medications'])[0],
            [{label: "Medications", items: this.apiSchemaKeys['SystemicTherapyMedication']}],
            [{label: "Metadata", items: this.createMetadataItems('SystemicTherapy')}],

        ]},
        {label: 'Surgeries', items: this.createSchemaMegaMenuItems('Surgery')},
        {label: 'Radiotherapies',  items: [
            this.createSchemaMegaMenuItems('Radiotherapy', ['dosages', 'settings'])[0],
            [{label: "Dosages", items: this.apiSchemaKeys['RadiotherapyDosage']}],
            [{label: "Settings", items: this.apiSchemaKeys['RadiotherapySetting']}],
            [{label: "Metadata", items: this.createMetadataItems('RadiotherRadiotherapyapySetting')}],
        ]},
        {label: 'Treatment Responses', items: this.createSchemaMegaMenuItems('TreatmentResponse')},
        {label: 'Genomic Variants', items: this.createSchemaMegaMenuItems('GenomicVariant')},
        // {label: 'Genomic Signatures', items: this.createSchemaMegaMenuItems('GenomicSignature')},
        {label: 'AdverseEvent',  items: [
            this.createSchemaMegaMenuItems('AdverseEvent', ['suspectedCauses', 'mitigations'])[0],
            [{label: "Suspected Causes", items: this.apiSchemaKeys['AdverseEventSuspectedCause']}],
            [{label: "Mitigations", items: this.apiSchemaKeys['AdverseEventMitigation']}],
            [{label: "Metadata", items: this.createMetadataItems('AdverseEvent')}],
        ]},
        {label: 'Performance Status', items: this.createSchemaMegaMenuItems('PerformanceStatus')},
        {label: 'Lifestyle', items: this.createSchemaMegaMenuItems('Lifestyle')},
        {label: 'FamilyHistory', items: this.createSchemaMegaMenuItems('FamilyHistory')},
        {label: 'Comorbidities', items: this.createSchemaMegaMenuItems('ComorbiditiesAssessment')},
        {label: 'Vitals', items: this.createSchemaMegaMenuItems('Vitals')},
    ]


    public items: MenuItem[] = [
        {
            label: 'Download dataset as...',
            items: [
                {
                    label: 'Data tree',
                    icon: 'pi pi-sitemap',
                    badge: 'Recommended',
                    command: () => this.downloadDataset('tree')
                },
                {
                    label: 'Flat table',
                    icon: 'pi pi-table',
                    command: () => this.downloadDataset('flat')
                },
                {
                    label: 'Split tables',
                    icon: 'pi pi-objects-column',
                    command: () => this.downloadDataset('split')
                }
            ]
        }
    ];

    
    private createSchemaMegaMenuItems(schema: string, exclude: string[] = []): MenuItem[][] {
        if (!this.apiSchemaKeys.hasOwnProperty(schema)) {
            console.error(`Schema "${schema}" does not exist.`)
        }
        return [
            [{label: "Properties", items: this.apiSchemaKeys[schema].filter(((item: any) => !exclude.includes(item.field)))}],
            [{label: "Metadata", items: this.createMetadataItems(schema)}],
        ]
    }

    private refreshDatasetObservable() {
        this.dataset$ = this.cohortService.getCohortDatasetDynamically({cohortId: this.cohortId, datasetRule: this.datasetRules, limit: this.pageSize, offset: this.currentOffset}).pipe(
            map(response => {
                this.totalEntries = response.count;
                return response.items
            })
        )
    }

    public setPaginationAndRefresh(event: any) {
        this.currentOffset = event.first;
        this.pageSize = event.rows;
        this.refreshDatasetObservable()
     }
     
    public clearDatasetRules() {
        this.datasetRules = [];
        this.refreshDatasetObservable()
    }

    private fetchFullDataset(): Observable<any[]> {
        const pageSize = 100;
        const totalPages = Math.ceil(this.totalEntries / pageSize);
        const requests: Observable<any>[] = [];
    
        for (let page = 0; page < totalPages; page++) {
          const request = this.cohortService.getCohortDatasetDynamically({
            cohortId: this.cohortId,
            datasetRule: this.datasetRules,
            limit: pageSize,
            offset: page * pageSize,
          }).pipe(map(response => response.items));
          requests.push(request);
        }    
        return forkJoin(requests).pipe(
          map((responses) => responses.flat()), // Flatten results into a single array
        );
    }


    private downloadAsJson(data: any[], filename: string = 'data.json'): void {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }



      downloadAsFlatCsv(data: any[], filename: string = 'data.csv'): void {
        if (data.length === 0) return;
                
        const flattenedData = data.flatMap(item => this.flattenObject(item));
        const headers = Array.from(new Set(flattenedData.flatMap(row => Object.keys(row))));
        const csvRows = flattenedData.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','));
        csvRows.unshift(headers.join(',')); // Add header row
        
        const csvString = csvRows.join('\n');
        const blob = new Blob([csvString], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }




  downloadAsCsv(data: any[], filename: string = 'data.csv'): void {
    if (data.length === 0) return;
    
    const flattenedData = data.flatMap(item => this.flattenObject(item));
    const headers = Array.from(new Set(flattenedData.flatMap(row => Object.keys(row))));
    const csvRows = flattenedData.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','));
    csvRows.unshift(headers.join(',')); // Add header row
    
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  downloadAsZip(data: any[], zipFilename: string = 'data.zip'): void {
    const zip = new JSZip();
    
    const mainData: any[] = [];
    const nestedDataMap: { [key: string]: any[] } = {};
    
    data.forEach(item => {
      const flatObj: any = {};
      const pseudoIdentifier = item.pseudoidentifier || '';
      
      Object.entries(item).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          if (!nestedDataMap[key]) nestedDataMap[key] = [];
          value.forEach(subItem => {
            const nestedRow = { pseudoidentifier: pseudoIdentifier, ...this.flattenObject(subItem)[0] };
            nestedDataMap[key].push(nestedRow);
          });
        } else if (typeof value === 'object' && value !== null) {
          if (!nestedDataMap[key]) nestedDataMap[key] = [];
          const nestedRow = { pseudoidentifier: pseudoIdentifier, ...this.flattenObject(value)[0] };
          nestedDataMap[key].push(nestedRow);
        } else {
          flatObj[key] = value;
        }
      });
      mainData.push(flatObj);
    });
    
    this.addCsvToZip(zip, 'main.csv', mainData);
    
    Object.entries(nestedDataMap).forEach(([key, nestedData]) => {
      this.addCsvToZip(zip, `${key}.csv`, nestedData);
    });
    
    zip.generateAsync({ type: 'blob' }).then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = zipFilename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    });
  }
    
      private addCsvToZip(zip: JSZip, filename: string, data: any[]): void {
        if (data.length === 0) return;
        const headers = Array.from(new Set(data.flatMap(row => Object.keys(row))));
        const csvRows = data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','));
        csvRows.unshift(headers.join(','));
        zip.file(filename, csvRows.join('\n'));
      }

      private flattenObject(obj: any, parentKey = ''): any[] {
        let rows: any[] = [{}];
        
        Object.entries(obj).forEach(([key, value]) => {
          const newKey = parentKey ? `${parentKey}.${key}` : key;
          
          if (Array.isArray(value)) {
            const expandedRows = value.flatMap(item => this.flattenObject(item, newKey));
            rows = expandedRows.map(expandedRow => ({ ...rows[0], ...expandedRow }));
          } else if (typeof value === 'object' && value !== null) {
            rows = rows.map(row => ({ ...row, ...this.flattenObject(value, newKey)[0] }));
          } else {
            rows.forEach(row => row[newKey] = value);
          }
        });
        
        return rows;
      }


    public downloadDataset(mode: 'tree' | 'split' | 'flat') {
        this.fetchFullDataset().pipe(take(1)).subscribe({
            next: data => {
                switch (mode) {
                    case 'tree':
                        this.downloadAsJson(data);
                        break;
                    case 'split':
                        this.downloadAsZip(data);
                        break;
                    case 'flat':
                        this.downloadAsFlatCsv(data);
                        break;
                }
            },
            complete: () => this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Dataset downloaded successfully' }),
            error: (error) => this.messageService.add({ severity: 'error', summary: 'Dataset download failed', detail: error.message }),
        });
    }


    private createMenuItem(resource: string, label: string, field: string, type: string) {
        return {label: label, field: field, command: () => {
            this.datasetRules.push({resource: resource, field: field})
            this.refreshDatasetObservable()
        }}
    }

    private createMetadataItems(schema: string) {
        return [
            this.createMenuItem(schema, 'Database ID', 'id', 'string'),
            this.createMenuItem(schema, 'Date created', 'createdAt', 'date'),
            this.createMenuItem(schema, 'Date updated', 'updatedAt', 'date'),
            this.createMenuItem(schema, 'Created by', 'createdBy', 'User'),
            this.createMenuItem(schema, 'Updated by', 'updatedBy', 'User'),
            this.createMenuItem(schema, 'External source', 'externalSource', 'string'),
            this.createMenuItem(schema, 'External source ID', 'externalSourceId', 'string'),
        ]
    }

}   