import { CommonModule } from "@angular/common";
import { Component, inject, Input, ViewEncapsulation } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { map, Observable, of } from "rxjs";

import { MegaMenu } from 'primeng/megamenu';
import { MegaMenuItem, MenuItem } from "primeng/api";
import { TableModule } from 'primeng/table';
import { Avatar } from "primeng/avatar";

import { CohortsService } from "src/app/shared/openapi";

import openApiSchema from "../../../../openapi.json"; // Import OpenAPI JSON (if possible)
import { NestedTableComponent } from "src/app/shared/components";
import { NgxJdenticonModule } from "ngx-jdenticon";


@Component({
    standalone: true,
    selector: 'pop-dataset-composer',
    templateUrl: './dataset-composer.component.html',
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        Avatar,
        MegaMenu,
        TableModule,
        NgxJdenticonModule,
        NestedTableComponent,
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


    private cohortService = inject(CohortsService);

    @Input({required: true}) cohortId!: string;

    public selectedFields: any[] = []
    public pageSizeChoices: number[] = [10, 20, 50, 100];
    public pageSize: number = this.pageSizeChoices[0];
    public totalEntries: number = 0;

    public currentOffset: number = 0;
    public dataset$: Observable<any[]> = of([]);

    // Extract keys from OpenAPI schema
    private apiSchemaKeys = Object.fromEntries(
      Object.entries(openApiSchema.components.schemas).map(([key, schema]: any) => [
        key,
        Object.keys(schema.properties || {}).filter(property => !this.createMetadataItems('').map(item => item['field']).includes(property) && property !== 'caseId')
            .map(property => this.createMenuItem(key, schema.properties[property].title, property, schema.properties[property].type) )
      ])
    )
      

    public resourceItems: MegaMenuItem[] = [
        {label: 'Patient Case', items: this.createSchemaMegaMenuItems('PatientCase')},
        {label: 'Neoplastic Entities', items: this.createSchemaMegaMenuItems('NeoplasticEntity')},
        {label: 'Systemic Therapy', items: this.createSchemaMegaMenuItems('SystemicTherapy')},
    ]

    
    private createSchemaMegaMenuItems(schema: string): MenuItem[][] {
        return [
            [{label: "Properties", items: this.apiSchemaKeys[schema]}],
            [{label: "Metadata", items: this.createMetadataItems(schema)}],
        ]
    }

    private refreshDatasetObservable() {
        this.dataset$ = this.cohortService.getCohortDatasetDynamically({cohortId: this.cohortId, datasetRule: this.selectedFields, limit: this.pageSize, offset: this.currentOffset}).pipe(
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
     
    private createMenuItem(resource: string, label: string, field: string, type: string): MenuItem {
        return {label: label, field: field, command: () => {
            this.selectedFields.push({resource: resource, field: field, type: type})
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