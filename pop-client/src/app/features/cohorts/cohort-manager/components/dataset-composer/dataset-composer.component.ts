import { CommonModule } from "@angular/common";
import { ChangeDetectionStrategy, Component, computed, effect, inject, input, linkedSignal, signal } from "@angular/core";
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from "@angular/forms";
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

import { CohortsService, PatientCaseDataset, DatasetsService, PaginatedDataset, DataResource, Cohort, Dataset, DatasetCreate, DatasetRule } from "pop-api-client";
import { NestedTableComponent } from "src/app/shared/components";
import { NgxJdenticonModule } from "ngx-jdenticon";
import { AuthService } from "src/app/core/auth/services/auth.service";
import { DownloadService } from "src/app/shared/services/download.service";
import { CamelCaseToTitleCasePipe } from "src/app/shared/pipes/camel-to-title-case.pipe";

import { Pipe, PipeTransform } from '@angular/core';
import { TypeCheckService } from "src/app/shared/services/type-check.service";
import { rxResource, toSignal } from "@angular/core/rxjs-interop";
import { Skeleton } from "primeng/skeleton";
import { Fieldset } from "primeng/fieldset";
import { InputText } from "primeng/inputtext";
import { Fluid } from "primeng/fluid";
import { DatasetComposeService } from "./dataset-composer.service";
import { PopoverModule } from 'primeng/popover';

@Pipe({ standalone: true, name: 'isString' })
export class IsStringPipe implements PipeTransform {
  transform(value: any): value is string {
    return typeof value === 'string';
  }
}


function getColumns(data: any[]): string[] {
    const allKeys = new Set<string>();
    allKeys.add('pseudoidentifier')
    data.forEach(item => Object.entries(item).forEach(([key,value]) => {
        if (key!=='pseudoidentifier') {
            allKeys.add(key);
        }
    }))
    return Array.from(allKeys);
}


@Component({
    selector: 'pop-dataset-composer',
    templateUrl: './dataset-composer.component.html',
    providers: [],
    imports: [
        FormsModule,
        ReactiveFormsModule,
        CommonModule,
        Avatar,
        Button,
        Fieldset,
        InputText,
        Card,
        Menu,
        ContextMenuModule,
        Skeleton,
        PopoverModule,
        AutoComplete,
        TreeModule,
        TableModule,
        NgxJdenticonModule,
        NestedTableComponent,
        CamelCaseToTitleCasePipe,
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
    readonly #fb = inject(FormBuilder);
    readonly #datasetService = inject(DatasetsService);
    readonly #cohortService = inject(CohortsService);
    readonly #downloadService = inject(DownloadService);
    readonly #messageService = inject(MessageService);
    readonly #typeCheckService = inject(TypeCheckService); 
    readonly #datasetComposerService = inject(DatasetComposeService); 

    public isArray = this.#typeCheckService.isArray;
    public isNested = (value: any): boolean => value !== null && typeof value === 'object' && typeof value[0] === 'object';
    
    protected readonly currentUser = computed(() => this.#authService.user());
    
    protected form = this.#fb.group({
        datasetId: this.#fb.control<string>(''),
        title: this.#fb.nonNullable.control<string>('', Validators.required),
        summary: this.#fb.nonNullable.control<string>('', Validators.required),
        projectId: this.#fb.nonNullable.control<string>('', Validators.required),
        datasetRules: this.#fb.nonNullable.control<any[]>([], Validators.required)
    })
    protected processing = signal<boolean>(false);
    #formChanges = toSignal(this.form.valueChanges, { initialValue: this.form.value });
    private payload = () => {
        const data = this.form.value;
        return {
            name: data.title,
            summary: data.summary,
            rules: data.datasetRules,
            projectId: data.projectId,
        } as DatasetCreate
    }


    // Dataset properties
    protected datasetData = rxResource({
        request: () => ({cohortId: this.cohort().id, datasetRule: this.datasetRules(), limit: this.pagination().limit, offset: this.pagination().offset}),
        loader: ({request}) => this.#cohortService.getCohortDatasetDynamically(request).pipe(
            tap(response => this.datasetDataSize.set(response.count)),
            map(response => response.items)
        )
    });
    protected datasetDataColumns = computed(() => this.datasetData.value() ? getColumns(this.datasetData.value()!) : [])
    protected datasetDataSize = signal<number>(0)

    // Dataset definition
    protected datasetId = signal<string>('');
    protected dataset = rxResource({
        request: () => ({datasetId: this.datasetId() as string}),
        loader: ({request}) => request.datasetId ? this.#datasetService.getDatasetById(request) : of(null)
    });
    protected datasetChanged = signal<boolean>(false);

    // Dataset search properties
    protected datasetTitleQuery = signal<string>('');
    protected selectedDataset = signal<Dataset | undefined>(undefined);
    protected projectDatasets = rxResource({
        request: () => ({projectId: this.cohort().projectId || undefined, titleContains: this.datasetTitleQuery() || undefined}),
        loader: ({request}) => this.#datasetService.getDatasets(request).pipe(map(response => response.items))
    })

    // Table pagination
    readonly pageSizeChoices: number[] = [10];
    protected pagination = signal({limit: this.pageSizeChoices[0], offset: 0})
    protected emptyDatasetPlaceholder = [1,2,3,4,5,6,7,8,9,10] as unknown as PatientCaseDataset[]

    // Dataset selection tree properties
    protected selectedRules = signal<TreeNode[]>([]);
    protected datasetRules = linkedSignal<any[]>(
        () => this.selectedRules()
            .map(
                (node: TreeNode) => ({key: node.key, data: node.data})
            ).filter(node => node.data)
            .map(node => node.data)
    )

    protected datasetTreeItems = this.#datasetComposerService.resourceItems
    protected downloadMenuItems: MenuItem[] = [
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

    constructor() {
        effect(() => {
            const currentState = this.#formChanges();
            const currentDataset = this.dataset.value();
            this.datasetChanged.set(this.hasDatasetChanged(currentState, currentDataset));
        });
        effect(() => {
            this.form.controls.projectId.setValue(this.cohort().projectId!);
        });
        effect(() => {
            this.form.controls.datasetRules.setValue(this.datasetRules());
        });
        effect(() => {
            const dataset = this.selectedDataset();
            if (dataset) {
                this.datasetId.set(dataset.id);
                this.form.controls.datasetId.setValue(dataset.id);
                this.form.controls.title.setValue(dataset.name);
                this.form.controls.summary.setValue(dataset.summary || '');
                this.form.controls.projectId.setValue(dataset.projectId);
                const rules = dataset.rules || [];
                try {
                    if (rules) {
                        this.selectedRules.set([
                            ...rules.map(rule => ({key: `${rule.resource}-${rule.field}`, data: rule})),
                            ...rules.map(rule => ({key: `${rule.resource}-properties`, partialSelected: true , checked: false})),
                            ...rules.map(rule => ({key: `${rule.resource}`, partialSelected: true, checked: false })),
                        ])
                    }
                    this.#messageService.add({ severity: 'success', summary: 'Success', detail: 'Dataset loaded successfully' });
                } catch (error) {
                    this.#messageService.add({ severity: 'error', summary: 'Dataset load failed', detail: 'An error ocurred while loading the dataset. The dataset may have been created in an outdated release.' });
                }
            }
        });
    }

    resetDataset() {
        this.selectedRules.set([]);
        this.form.setValue({datasetId: '', title: '', summary: '', projectId: this.cohort().projectId!, datasetRules: []});
        this.form.updateValueAndValidity()
        this.datasetId.set('');
    }
     
    submitDataset() {
        this.processing.set(true);
        const dataset = this.payload();
        if (this.form.value.datasetId) {
            this.#datasetService.updateDataset({datasetId: this.form.value.datasetId, datasetCreate: dataset}).pipe(first()).subscribe({
                next: (response) => {
                    this.processing.set(false);
                    this.datasetId.set(response.id);
                    this.form.controls.datasetId.setValue(response.id);
                    this.#messageService.add({ severity: 'success', summary: 'Success', detail: `Updated dataset "${this.form.value.title}".`});
                },
                error: (error) => {
                    this.processing.set(false);
                    this.#messageService.add({ severity: 'error', summary: 'Dataset update failed', detail: error.error.detail })
                },
            })
        } else {
            this.#datasetService.createDataset({datasetCreate: dataset}).pipe(first()).subscribe({
                next: () => {
                    this.processing.set(false);
                    this.dataset.reload();
                    this.#messageService.add({ severity: 'success', summary: 'Success', detail: `Saved dataset "${this.form.value.title}".`})
                },
                error: (error) => {
                    this.processing.set(false)
                    this.#messageService.add({ severity: 'error', summary: 'Dataset save failed', detail: error.error.detail })
                },
            })
        }
    }

    hasDatasetChanged(currentState: any, currentDataset: Dataset | undefined | null) {
        if (!currentState) return false
        if (!currentDataset) return true
        return !(currentDataset.id == currentState.datasetId 
            && currentDataset.projectId == currentState.projectId 
            && currentDataset.rules?.length == currentState.datasetRules?.length
            && currentDataset.rules?.every((rule: DatasetRule) => currentState.datasetRules?.some((existingRule: DatasetRule) => existingRule.resource == rule.resource && existingRule.field == rule.field && existingRule.transform == rule.transform))
            && currentDataset.name == currentState.title
            && currentDataset.summary == currentState.summary)
    }

    downloadDataset(mode: 'tree' | 'split' | 'flat') {
        this.processing.set(true);
        this.#messageService.add({ severity: 'info', summary: 'Downloading', detail: 'Please wait for the download to begin...' })
        this.#cohortService.exportCohortDataset({
            cohortId: this.cohort().id,
            datasetId: this.form.value.datasetId!,
          }).pipe(first()).subscribe({
            next: (data: any) => {
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
            complete: () => {
                this.#messageService.add({ severity: 'success', summary: 'Success', detail: 'Dataset downloaded successfully' })
                this.processing.set(false)
            },
            error: (error) => {
                this.#messageService.add({ severity: 'error', summary: 'Dataset download failed', detail: error.error.detail })
                this.processing.set(false)
            },
        });
    }

}   