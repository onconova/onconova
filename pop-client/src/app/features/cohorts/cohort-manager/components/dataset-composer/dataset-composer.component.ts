import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, computed, inject, input, linkedSignal, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { trigger, state, style, transition, animate } from '@angular/animations';
import { catchError, first, map, Observable, of, take, tap } from "rxjs";

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

import OpenAPISpecification from "../../../../../../../openapi.json";
import { CohortsService, Dataset, DatasetsService, PaginatedDataset, DataResource, Cohort } from "src/app/shared/openapi";
import { NestedTableComponent } from "src/app/shared/components";
import { NgxJdenticonModule } from "ngx-jdenticon";
import { AuthService } from "src/app/core/auth/services/auth.service";
import { DownloadService } from "src/app/shared/services/download.service";
import { CamelCaseToTitleCasePipe } from "src/app/shared/pipes/camel-to-title-case.pipe";

import { Pipe, PipeTransform } from '@angular/core';
import { TypeCheckService } from "src/app/shared/services/type-check.service";
import { rxResource } from "@angular/core/rxjs-interop";

@Pipe({ standalone: true, name: 'isString' })
export class IsStringPipe implements PipeTransform {
  transform(value: any): value is string {
    return typeof value === 'string';
  }
}


function getColumns(data: any[]): string[] {
    const allKeys = new Set<string>();
    data.forEach(item => Object.entries(item).forEach(([key,value]) => {
        allKeys.add(key);
    }))
    return Array.from(allKeys);
}


@Component({
    selector: 'pop-dataset-composer',
    templateUrl: './dataset-composer.component.html',
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        Avatar,
        Button,
        Toolbar,
        Card,
        Menu,
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
            state('void', style({ opacity: 0 })), // Initial state (not visible)
            transition(':enter', [animate('500ms ease-in')]), // Fade-in effect
            transition(':leave', [animate('500ms ease-out')]) // Fade-out effect
        ])
    ],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DatasetComposerComponent {

    // Input properties
    cohort = input.required<Cohort>();
    loading = input<boolean>(false);

    // Injected services
    readonly #authService = inject(AuthService);
    readonly #datasetService = inject(DatasetsService);
    readonly #cohortService = inject(CohortsService);
    readonly #downloadService = inject(DownloadService);
    readonly #messageService = inject(MessageService);
    readonly #typeCheckService = inject(TypeCheckService); 

    public isArray = this.#typeCheckService.isArray;
    public user = computed(() => this.#authService.user());
    
    // User datasets properties
    public selectedDataset!: Dataset | string;
    public userDatasets$: Observable<Dataset[]> = of([])
    public userDatasetOptions: Dataset[] = []

    // Dataset properties
    public dataset = rxResource({
        request: () => ({cohortId: this.cohort().id, datasetRule: this.datasetRules(), limit: this.pagination().limit, offset: this.pagination().offset}),
        loader: ({request}) => this.#cohortService.getCohortDatasetDynamically(request).pipe(
            tap(response => this.datasetSize.set(response.count)),
            map(response => response.items)
        )
    });
    public datasetColumns = computed(() => this.dataset.value() ? getColumns(this.dataset.value()!) : [])
    public datasetSize = signal<number>(0)

    // Table pagination
    readonly pageSizeChoices: number[] = [10, 20, 50, 100];
    public pagination = signal({limit: this.pageSizeChoices[0], offset: 0})

    // Dataset selection tree properties
    public selectedRules = signal<TreeNode[]>([]);
    public datasetRules = linkedSignal<any[]>(() => this.selectedRules().map((node: TreeNode) => ({key: node.key, data: node.data})).filter(node => node.data).map(node => node.data))

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
        {key: 'GenomicSignatures', label: 'Genomic Signatures', children: [
            this.constructResourceTreeNode(DataResource.TumorMutationalBurden, 'Tumor Mutational Burdens', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.MicrosatelliteInstability, 'Microsatellite Instabilities', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.LossOfHeterozygosity, 'Losses of Heterozygosity', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.HomologousRecombinationDeficiency, 'Homologous Recombination Deficiencies', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.TumorNeoantigenBurden, 'Tumor Neoantigen Burdens', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.AneuploidScore, 'Aneuploid Score', {exclude: ['category']}),
        ]},
        this.constructResourceTreeNode(DataResource.AdverseEvent, 'Adverse Events', {exclude: ['suspectedCauses', 'mitigations'], children: [
            this.constructResourceTreeNode(DataResource.AdverseEventSuspectedCause, 'Suspected Causes', {isRoot: false}),
            this.constructResourceTreeNode(DataResource.AdverseEventMitigation, 'Mitigations', {isRoot: false})
        ]}),
        {key: 'TumorBoards', label: 'Tumor Boards', children: [
            this.constructResourceTreeNode(DataResource.UnspecifiedTumorBoard, 'Unspecified Tumor Boards', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.MolecularTumorBoard, 'Molecular Tumor Boards', {exclude: ['category', 'therapeuticRecommendations'], children: [
                this.constructResourceTreeNode(DataResource.MolecularTherapeuticRecommendation, 'Therapeutic Recommendations', {isRoot: false}),
            ]}),
        ]},
        this.constructResourceTreeNode(DataResource.PerformanceStatus, 'Performance Status'),
        this.constructResourceTreeNode(DataResource.Lifestyle, 'Lifestyle'),
        this.constructResourceTreeNode(DataResource.FamilyHistory, 'Family History'),
        this.constructResourceTreeNode(DataResource.ComorbiditiesAssessment, 'Comorbidities'),
        this.constructResourceTreeNode(DataResource.Vitals, 'Vitals'),
    ]

    public downloadMenuItems: MenuItem[] = [
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


    public constructResourceTreeNode(resource: DataResource, label: string, options: {children?: any[], exclude?: string[], isRoot?: boolean} = {children: [], exclude: [], isRoot: true}){
        // Get the schema definition of the entity from the OpenAPISpecification object
        const schemas = OpenAPISpecification.components.schemas
        // Get a list of all fields/properties in that resource
        const properties = schemas[resource].properties || {};
        const propertyNodes = Object.entries(properties)
            .filter(
                ([propertyKey,_]) => !this.createMetadataItems('').map(
                    item => item['field']).includes(propertyKey) && !['caseId', 'description','anonymized'].includes(propertyKey)
            ).flatMap(
                ([propertyKey,property]:[string, any]) => {
                    const title: string = property.title
                    const description: string = property.description
                    if (property.anyOf && property.anyOf[property.anyOf.length-1].type === 'null') {
                        property = property.anyOf[0];
                    }
                    if (property.items) {
                        property = property.items;       
                    }

                    let propertyType: string;
                    if (property.type === undefined && property.$ref) {
                        propertyType = property.$ref.split('/').pop();
                    } else {
                        propertyType = property.type;
                    }     
                    return this.createTreeNode(resource, title, propertyKey, propertyType, description);
                }
            )
                
        const isRoot =  options?.isRoot ?? true
        const treeNode = {
            key: resource, 
            label: label, 
            children: isRoot ? [
                {key: `${resource}-properties`, label: "Properties", children: propertyNodes.filter(
                    ((item: any) => !resource.includes(item.field) && !options?.exclude?.includes(item.field))
                )},
                {key: `${resource}-metadata`, label: "Metadata", children: this.createMetadataItems(resource)},
            ] : propertyNodes
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


    public searchUserDatasets(event: any) {
        this.#datasetService.getDatasets({nameContains: event.query}).pipe(first(), map((response: PaginatedDataset) => this.userDatasetOptions = response.items), catchError(() => [])).subscribe()
    }
    private refreshUserDatasets() {
        this.userDatasets$ = this.#datasetService.getDatasets().pipe(map(response => this.userDatasetOptions = response.items), catchError(() => []))
    }
    public deleteUserDataset() {
        if (typeof this.selectedDataset !== 'string'  && this.selectedDataset.id) {
            this.#datasetService.deleteDatasetById({datasetId: this.selectedDataset.id}).pipe(take(1)).subscribe({
                complete: () => {
                    const datasetName = (typeof this.selectedDataset !== 'string') ? this.selectedDataset.name : 'Unknown';
                    this.selectedDataset = ''
                    this.#messageService.add({ severity: 'success', summary: 'Dataset deleted', detail: `Succesfully deleted dataset "${datasetName}"` })
                },
                error: (error) => this.#messageService.add({ severity: 'error', summary: 'Dataset could not be deleted', detail: error.error.detail }),
            })
        }
    }
    public loadUserDataset() {
        if (typeof this.selectedDataset !== 'string'  && this.selectedDataset.rules) {
            this.datasetRules.set(this.selectedDataset.rules);
            this.selectedRules.set([
                ...this.selectedDataset.rules.map(rule => ({key: `${rule.resource}-${rule.field}`, data: rule})),
                ...this.selectedDataset.rules.map(rule => ({key: `${rule.resource}-properties`, partialSelected: true , checked: false})),
                ...this.selectedDataset.rules.map(rule => ({key: `${rule.resource}`, partialSelected: true, checked: false })),
            ])
            this.dataset.reload()    
        }
    }
    public createUserDataset() {
        let datasetName = (typeof this.selectedDataset == 'string') ? this.selectedDataset : this.selectedDataset.name;
        this.#datasetService.createDataset({
            datasetCreate: {
                name: datasetName,
                rules: this.datasetRules(),
            }
        }).pipe(take(1)).subscribe({
            complete: () => {
                this.refreshUserDatasets()
                this.#messageService.add({ severity: 'success', summary: 'Dataset update', detail: `Succesfully updated dataset "${datasetName}"` })
            },
            error: (error) => this.#messageService.add({ severity: 'error', summary: 'Dataset could not be saved', detail: error.error.detail }),
        })
    }
     
    downloadDataset(mode: 'tree' | 'split' | 'flat') {
        this.#messageService.add({ severity: 'info', summary: 'Downloading', detail: 'Please wait for the download to begin...' })
        this.#cohortService.exportCohortDataset({
            cohortId: this.cohort().id,
            datasetRule: this.datasetRules(),
          }).pipe(first()).subscribe({
            next: (data: any) => {
                console.log('data', data)
                switch (mode) {
                    case 'tree':
                        this.#downloadService.downloadAsJson(data);
                        break;
                    case 'split':
                        this.#downloadService.downloadAsZip(data.dataset);
                        break;
                    case 'flat':
                        this.#downloadService.downloadAsFlatCsv(data.dataset);
                        break;
                }
            },
            complete: () => this.#messageService.add({ severity: 'success', summary: 'Success', detail: 'Dataset downloaded successfully' }),
            error: (error) => this.#messageService.add({ severity: 'error', summary: 'Dataset download failed', detail: error.error.detail }),
        });
    }


    isNested(value: any): boolean {
        return value !== null && typeof value === 'object' && typeof value[0] === 'object';
    }

}   