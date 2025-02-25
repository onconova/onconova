import { CommonModule } from "@angular/common";
import { Component, inject, Input, ViewEncapsulation } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { trigger, state, style, transition, animate } from '@angular/animations';

import { catchError, forkJoin, map, Observable, of, take } from "rxjs";

import JSZip from 'jszip';

import { Menu } from "primeng/menu";
import { MegaMenu } from 'primeng/megamenu';
import { MegaMenuItem, MenuItem } from "primeng/api";
import { TableModule } from 'primeng/table';
import { Avatar } from "primeng/avatar";
import { Button } from "primeng/button";
import { Toolbar } from "primeng/toolbar";
import { MessageService, TreeNode } from "primeng/api";
import { TreeModule} from 'primeng/tree';
import { AutoComplete } from 'primeng/autocomplete';


import openApiSchema from "../../../../openapi.json"; // Import OpenAPI JSON (if possible)
import { CohortsService, Dataset, DatasetsService, PaginatedDataset, DataResource } from "src/app/shared/openapi";
import { NestedTableComponent } from "src/app/shared/components";
import { NgxJdenticonModule } from "ngx-jdenticon";
import { AuthService } from "src/app/core/auth/services/auth.service";
import { CamelCaseToTitleCasePipe } from "src/app/shared/pipes/camel-to-title-case.pipe";

import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ standalone: true, name: 'isString' })
export class IsStringPipe implements PipeTransform {
  transform(value: any): value is string {
    return typeof value === 'string';
  }
}

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
        AutoComplete,
        TreeModule,
        MegaMenu,
        TableModule,
        NgxJdenticonModule,
        NestedTableComponent,
        CamelCaseToTitleCasePipe,
        IsStringPipe,
    ],
    animations: [
      trigger('fadeAnimation', [
        state('void', style({ opacity: 0 })),  // Initial state (not visible)
        transition(':enter', [animate('500ms ease-in')]),  // Fade-in effect
        transition(':leave', [animate('500ms ease-out')])  // Fade-out effect
      ])
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
    private datasetService = inject(DatasetsService);
    private cohortService = inject(CohortsService);
    private messageService = inject(MessageService);

    @Input({required: true}) cohortId!: string;

    public datasetRules: any[] = []
    public pageSizeChoices: number[] = [10, 20, 50, 100];
    public pageSize: number = this.pageSizeChoices[0];
    public totalEntries: number = 0;

    public currentOffset: number = 0;
    public dataset$: Observable<any[]> = of([]);
    public userDatasets$: Observable<Dataset[]> = of([])
    public userDatasetOptions: Dataset[] = []

    public selectedDataset!: Dataset | string;

    // Extract keys from OpenAPI schema
    private apiSchemaKeys = Object.fromEntries(
      Object.entries(openApiSchema.components.schemas).map(([key, schema]: any) => [
        key,
        Object.keys(schema.properties || {}).filter(property => !this.createMetadataItems('').map(item => item['field']).includes(property) && !['caseId', 'description'].includes(property))
            .map(property => this.createMenuItem(key, schema.properties[property].title, property, schema.properties[property].type) )
      ])
    )
    
    selectedNodes!: TreeNode[];

    public resourceItems: TreeNode<any>[] = [
        {key: DataResource.PatientCase, label: 'Patient Case', children: this.createSchemaTreeNodes(DataResource.PatientCase, ['pseudoidentifier'])},
        {key: this.makeRandom(6), label: 'Neoplastic Entities', children: this.createSchemaTreeNodes('NeoplasticEntity')},
        {key: this.makeRandom(6), label: 'Stagings', children: this.createSchemaTreeNodes('AnyStaging')},
        {key: this.makeRandom(6), label: 'Risk assessments', children: this.createSchemaTreeNodes('RiskAssessment')},
        {key: this.makeRandom(6), label: 'Therapy Lines', children: this.createSchemaTreeNodes('TherapyLine')},
        {key: this.makeRandom(6), label: 'Systemic Therapy', children: [
            this.createSchemaTreeNodes('SystemicTherapy', ['medications'])[0],
            {key: this.makeRandom(6), label: "Medications", children: this.apiSchemaKeys['SystemicTherapyMedication']},
            {key: this.makeRandom(6), label: "Metadata", children: this.createMetadataItems('SystemicTherapy')},

        ]},
        {key: this.makeRandom(6), label: 'Surgeries', children: this.createSchemaTreeNodes('Surgery')},
        {key: this.makeRandom(6), label: 'Radiotherapies',  children: [
            this.createSchemaTreeNodes('Radiotherapy', ['dosages', 'settings'])[0],
            {key: this.makeRandom(6), label: "Dosages", children: this.apiSchemaKeys['RadiotherapyDosage']},
            {key: this.makeRandom(6), label: "Settings", children: this.apiSchemaKeys['RadiotherapySetting']},
            {key: this.makeRandom(6), label: "Metadata", children: this.createMetadataItems('RadiotherRadiotherapyapySetting')},
        ]},
        {key: this.makeRandom(6), label: 'Treatment Responses', children: this.createSchemaTreeNodes('TreatmentResponse')},
        {key: this.makeRandom(6), label: 'Genomic Variants', children: this.createSchemaTreeNodes('GenomicVariant')},
        // {label: 'Genomic Signatures', items: this.createSchemaTreeNodes('GenomicSignature')},
        {key: this.makeRandom(6), label: 'AdverseEvent',  children: [
            this.createSchemaTreeNodes('AdverseEvent', ['suspectedCauses', 'mitigations'])[0],
            {key: this.makeRandom(6), label: "Suspected Causes", children: this.apiSchemaKeys['AdverseEventSuspectedCause']},
            {key: this.makeRandom(6), label: "Mitigations", children: this.apiSchemaKeys['AdverseEventMitigation']},
            {key: this.makeRandom(6), label: "Metadata", children: this.createMetadataItems('AdverseEvent')},
        ]},
        {key: this.makeRandom(6), label: 'Performance Status', children: this.createSchemaTreeNodes('PerformanceStatus')},
        {key: this.makeRandom(6), label: 'Lifestyle', children: this.createSchemaTreeNodes('Lifestyle')},
        {key: this.makeRandom(6), label: 'FamilyHistory', children: this.createSchemaTreeNodes('FamilyHistory')},
        {key: this.makeRandom(6), label: 'Comorbidities', children: this.createSchemaTreeNodes('ComorbiditiesAssessment')},
        {key: this.makeRandom(6), label: 'Vitals', children: this.createSchemaTreeNodes('Vitals')},
    ]

    public datasetFieldActions = [
        {
            label: 'Actions',
            items: [
                {
                    label: 'Remove',
                    icon: 'pi pi-times',
                    command: () => console.log('REMOVE')
                },
                {
                    label: 'Transformation',
                    icon: 'pi pi-filter',
                    command: () => console.log('TRANSFORM')
                }
            ]
        }
    ];

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

    ngOnInit() {
        this.refreshUserDatasets();
    }
    
    private createSchemaTreeNodes(schema: string, exclude: string[] = []): TreeNode<any>[] {
        if (!this.apiSchemaKeys.hasOwnProperty(schema)) {
            console.error(`Schema "${schema}" does not exist.`)
        }
        return [
            {key: `${schema}-properties`, label: "Properties", children: this.apiSchemaKeys[schema].filter(((item: any) => !exclude.includes(item.field)))},
            {key: `${schema}-metadata`, label: "Metadata", children: this.createMetadataItems(schema)},
        ]
    }

    public updateDataset(selectedNodes: any) {
        this.selectedNodes = selectedNodes.map((node: TreeNode) => ({key: node.key, data: node.data}))
        this.datasetRules = this.selectedNodes.filter(node => node.data).map(node => node.data)
        this.refreshDatasetObservable()    
    }

    private refreshDatasetObservable() {
        this.dataset$ = this.cohortService.getCohortDatasetDynamically({cohortId: this.cohortId, datasetRule: this.datasetRules, limit: this.pageSize, offset: this.currentOffset}).pipe(
            map(response => {
                this.totalEntries = response.count;
                return response.items
            })
        )
    }


    public searchUserDatasets(event: any) {
        this.userDatasets$ = this.datasetService.getDatasets({nameContains: event.query}).pipe(map((response: PaginatedDataset) => this.userDatasetOptions = response.items), catchError(() => []))
    }
    private refreshUserDatasets() {
        this.userDatasets$ = this.datasetService.getDatasets().pipe(map(response => this.userDatasetOptions = response.items), catchError(() => []))
    }
    public deleteUserDataset() {
        if (typeof this.selectedDataset !== 'string'  && this.selectedDataset.id) {
            this.datasetService.deleteDatasetById({datasetId: this.selectedDataset.id}).pipe(take(1)).subscribe({
                complete: () => {
                    const datasetName = (typeof this.selectedDataset !== 'string') ? this.selectedDataset.name : 'Unknown';
                    this.selectedDataset = ''
                    this.messageService.add({ severity: 'success', summary: 'Dataset deleted', detail: `Succesfully deleted dataset "${datasetName}"` })
                },
                error: (error) => this.messageService.add({ severity: 'error', summary: 'Dataset could not be deleted', detail: error.message }),
            })
        }
    }
    public loadUserDataset() {
        if (typeof this.selectedDataset !== 'string'  && this.selectedDataset.rules) {
            this.datasetRules = this.selectedDataset.rules;
            this.selectedNodes = [
                ...this.selectedDataset.rules.map(rule => ({key: `${rule.resource}-${rule.field}`, data: rule})),
                ...this.selectedDataset.rules.map(rule => ({key: `${rule.resource}-properties`, partialSelected: true , checked: false})),
                ...this.selectedDataset.rules.map(rule => ({key: `${rule.resource}`, partialSelected: true, checked: false })),
            ]
            this.refreshDatasetObservable()    
        }
    }
    public createUserDataset() {
        let datasetName = (typeof this.selectedDataset == 'string') ? this.selectedDataset : this.selectedDataset.name;
        this.datasetService.createDataset({
            datasetCreate: {
                name: datasetName,
                rules: this.datasetRules,
            }
        }).pipe(take(1)).subscribe({
            complete: () => {
                this.refreshUserDatasets()
                this.messageService.add({ severity: 'success', summary: 'Dataset update', detail: `Succesfully updated dataset "${datasetName}"` })
            },
            error: (error) => this.messageService.add({ severity: 'error', summary: 'Dataset could not be saved', detail: error.message }),
        })
    }


    public setPaginationAndRefresh(event: any) {
        this.currentOffset = event.first;
        this.pageSize = event.rows;
        this.refreshDatasetObservable()
     }
     
    public clearDatasetRules() {
        this.datasetRules = [];
        this.selectedNodes = []
        this.selectedDataset = '';
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

    private downloadAsFlatCsv(data: any[], filename: string = 'data.csv'): void {
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

    private downloadAsZip(data: any[], zipFilename: string = 'data.zip'): void {
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
        return {key: `${resource}-${field}`, label: label, field: field, data: {resource: resource, field: field}}
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

    private makeRandom(lengthOfCode: number, possible: string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890,./;\'[]\\=-)(*&^%$#@!~`") {
        let text = "";
        for (let i = 0; i < lengthOfCode; i++) {
          text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
      }

}   