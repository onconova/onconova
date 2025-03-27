import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, inject, Input, SimpleChanges, ViewEncapsulation } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { trigger, state, style, transition, animate } from '@angular/animations';

import { catchError, forkJoin, map, Observable, of, take } from "rxjs";


import { Menu } from "primeng/menu";
import { MenuItem } from "primeng/api";
import { ContextMenuModule } from 'primeng/contextmenu';
import { Card } from "primeng/card";
import { TableModule } from 'primeng/table';
import { Avatar } from "primeng/avatar";
import { Button } from "primeng/button";
import { Toolbar } from "primeng/toolbar";
import { MessageService, TreeNode } from "primeng/api";
import { TreeModule} from 'primeng/tree';
import { AutoComplete } from 'primeng/autocomplete';


import openApiSchema from "../../../../../openapi.json";
import { CohortsService, Dataset, DatasetsService, PaginatedDataset, DataResource } from "src/app/shared/openapi";
import { NestedTableComponent } from "src/app/shared/components";
import { NgxJdenticonModule } from "ngx-jdenticon";
import { AuthService } from "src/app/core/auth/services/auth.service";
import { DownloadService } from "src/app/shared/services/download.service";
import { CamelCaseToTitleCasePipe } from "src/app/shared/pipes/camel-to-title-case.pipe";

import { Pipe, PipeTransform } from '@angular/core';
import { Skeleton } from "primeng/skeleton";

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
        Card,
        Menu,
        Skeleton,
        ContextMenuModule,
        AutoComplete,
        TreeModule,
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
    changeDetection: ChangeDetectionStrategy.OnPush,
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

    // Injected services
    public authService = inject(AuthService);
    private datasetService = inject(DatasetsService);
    private cohortService = inject(CohortsService);
    private downloadService = inject(DownloadService);
    private messageService = inject(MessageService);
    
    @Input({required: true}) cohortId!: string;
    @Input() loading: boolean = false;

    // User datasets properties
    public userDatasets$: Observable<Dataset[]> = of([])
    public userDatasetOptions: Dataset[] = []

    // Dataset table properties
    public dataset$!: Observable<any[]>;
    public datasetRules: any[] = []
    public pageSizeChoices: number[] = [10, 20, 50, 100];
    public pageSize: number = this.pageSizeChoices[0];
    public totalEntries: number = 0;
    public currentOffset: number = 0;

    // Dataset selection tree properties
    public selectedDataset!: Dataset | string;
    public selectedNodes!: TreeNode[];


    // Extract keys from OpenAPI schema
    private apiSchemaKeys = Object.fromEntries(
      Object.entries(openApiSchema.components.schemas).map(([key, schema]: any) => [
        key,
        Object.keys(schema.properties || {}).filter(property => !this.createMetadataItems('').map(item => item['field']).includes(property) && !['caseId', 'description'].includes(property))
          .map(propertyName => {
            let propertyType;
            const property = schema.properties[propertyName]
            if (property.anyOf && property.anyOf[property.anyOf.length-1].type === 'null') {
                propertyType = property.anyOf[0];
            } else {
                propertyType = property;
            }
            if (propertyType.type === undefined && propertyType.$ref) {
              propertyType = propertyType.$ref.split('/').pop();
            } else {
                propertyType = propertyType.type;
            }
            return this.createTreeNode(key, property.title, propertyName, propertyType, property.description);
          })
      ])
    )  
    public resourceItems: TreeNode<any>[] = [
        this.constructResourceTreeNode(DataResource.PatientCase, 'Patient case', {exclude: ['pseudoidentifier']}),
        this.constructResourceTreeNode(DataResource.NeoplasticEntity, 'Neoplastic Entities'),
        {key: 'Stagings', label: 'Stagings', children: [
            this.constructResourceTreeNode(DataResource.TnmStaging, 'TNM Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.FigoStaging, 'FIGO Stagings', {exclude: ['stagingDomain']}),
        ]},
        this.constructResourceTreeNode(DataResource.RiskAssessment, 'Risk Assessments'),
        this.constructResourceTreeNode(DataResource.TherapyLine, 'Therapy Lines'),
        this.constructResourceTreeNode(DataResource.SystemicTherapy, 'Systemic Therapies', {exclude: ['medications'], children: [
            this.constructResourceTreeNode(DataResource.SystemicTherapyMedication, 'Medications', {isRoot: false}),
        ]}),
        this.constructResourceTreeNode(DataResource.Surgery, 'Surgeries'),
        this.constructResourceTreeNode(DataResource.Radiotherapy, 'Radiotherapies', {exclude: ['dosages', 'settings'], children: [
            this.constructResourceTreeNode(DataResource.RadiotherapyDosage, 'Dosages', {isRoot: false}),
            this.constructResourceTreeNode(DataResource.RadiotherapySetting, 'Settings', {isRoot: false})
        ]}),
        this.constructResourceTreeNode(DataResource.TreatmentResponse, 'Treatment Responses'),
        this.constructResourceTreeNode(DataResource.GenomicVariant, 'Genomic Variants'),
        this.constructResourceTreeNode(DataResource.AdverseEvent, 'Adverse Events', {exclude: ['suspectedCauses', 'mitigations'], children: [
            this.constructResourceTreeNode(DataResource.AdverseEventSuspectedCause, 'Suspected Causes', {isRoot: false}),
            this.constructResourceTreeNode(DataResource.AdverseEventMitigation, 'Mitigations', {isRoot: false})
        ]}),
        this.constructResourceTreeNode(DataResource.PerformanceStatus, 'Performance Status'),
        this.constructResourceTreeNode(DataResource.Lifestyle, 'Lifestyle'),
        this.constructResourceTreeNode(DataResource.FamilyHistory, 'Family History'),
        this.constructResourceTreeNode(DataResource.ComorbiditiesAssessment, 'Comorbidities'),
        this.constructResourceTreeNode(DataResource.Vitals, 'Vitals'),
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

    ngOnInit() {
        this.refreshUserDatasets()
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes['loading'] && !this.loading) {
            this.refreshDatasetObservable()         
        }
    }

    public constructResourceTreeNode(resource: DataResource, label: string, options: {children?: any[], exclude?: string[], isRoot?: boolean} = {children: [], exclude: [], isRoot: true}){
        if (!this.apiSchemaKeys.hasOwnProperty(resource)) {
            console.error(`Schema "${resource}" does not exist.`)
        }
        const isRoot =  options?.isRoot ?? true
        const treeNode = {
            key: resource, 
            label: label, 
            children: isRoot ? [
                {key: `${resource}-properties`, label: "Properties", children: this.apiSchemaKeys[resource].filter(((item: any) => !resource.includes(item.field)))},
                {key: `${resource}-metadata`, label: "Metadata", children: this.createMetadataItems(resource)},
            ] : this.apiSchemaKeys[resource]
        }
        treeNode.children = isRoot ? [treeNode.children[0], ...(options?.children || []), treeNode.children[1]] : treeNode.children
        return treeNode
    }

    private createTreeNode(resource: string, label: string, field: string, type: string, description: string | null = null) {
        let defaultTransform;
        switch (type) {
            case 'CodedConcept':
                defaultTransform = 'GetCodedConceptDisplay';
                break
            case 'User':
                defaultTransform = 'GetUserUsername';
                break
            default:
                defaultTransform = null;
                break
        }
        
        return {
            key: `${resource}-${field}`, 
            label: label, 
            field: field, 
            type: type, 
            data: {
                resource: resource, 
                field: field,
                transform: defaultTransform,
            },
            description: description,
        }
    }

    private createMetadataItems(schema: string) {
        return [
            this.createTreeNode(schema, 'Database ID', 'id', 'string'),
            this.createTreeNode(schema, 'Date created', 'createdAt', 'date'),
            this.createTreeNode(schema, 'Date updated', 'updatedAt', 'date'),
            this.createTreeNode(schema, 'Created by', 'createdBy', 'User'),
            this.createTreeNode(schema, 'Updated by', 'updatedBy', 'User'),
            this.createTreeNode(schema, 'External source', 'externalSource', 'string'),
            this.createTreeNode(schema, 'External source ID', 'externalSourceId', 'string'),
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
                error: (error) => this.messageService.add({ severity: 'error', summary: 'Dataset could not be deleted', detail: error.error.detail }),
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
            error: (error) => this.messageService.add({ severity: 'error', summary: 'Dataset could not be saved', detail: error.error.detail }),
        })
    }


    public setPaginationAndRefresh(event: any) {
        if (this.currentOffset === event.first && this.pageSize === event.rows) return
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

    public downloadDataset(mode: 'tree' | 'split' | 'flat') {
        this.fetchFullDataset().pipe(take(1)).subscribe({
            next: data => {
                switch (mode) {
                    case 'tree':
                        this.downloadService.downloadAsJson(data);
                        break;
                    case 'split':
                        this.downloadService.downloadAsZip(data);
                        break;
                    case 'flat':
                        this.downloadService.downloadAsFlatCsv(data);
                        break;
                }
            },
            complete: () => this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Dataset downloaded successfully' }),
            error: (error) => this.messageService.add({ severity: 'error', summary: 'Dataset download failed', detail: error.error.detail }),
        });
    }

}   