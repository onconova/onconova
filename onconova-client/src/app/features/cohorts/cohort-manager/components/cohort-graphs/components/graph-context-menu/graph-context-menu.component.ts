import { CommonModule } from '@angular/common';
import { Component, inject, Input } from '@angular/core';
import { Chart,ChartConfiguration, ChartType } from 'chart.js';
import { MenuItem } from 'primeng/api';
import { ContextMenuModule } from 'primeng/contextmenu';
import { DownloadService } from 'src/app/shared/services/download.service';

@Component({
    imports: [
        CommonModule,
        ContextMenuModule
    ],
    selector: 'onconova-cohort-graph-context-menu',
    template: `<p-contextmenu [target]="target" [model]="items" />`
})
export class CohortGraphsContextMenu{

    private downloadService = inject(DownloadService);

    @Input() target!: any;
    @Input() data!: any;
    @Input() chart!: any;

    public items: MenuItem[] = []; 
    
    ngOnInit() {
        this.items = [
            {label: 'Download data', icon: 'pi pi-download', items: [
                {label: 'As JSON', icon: 'pi pi-sitemap', disabled: !this.data, command: () => {
                    this.downloadService.downloadAsJson(this.data);
                }},
                {label: 'As table', icon: 'pi pi-table', disabled: !this.data, command: () => {
                    this.downloadService.downloadAsFlatCsv(this.data);
                }},            
            ]},       
            {label: 'Download image', icon: 'pi pi-images', items: [
                {label: 'Low-resolution', icon: 'pi pi-image', disabled: !this.chart, command: () => {
                    this.downloadService.downloadChart(this.chart)
                }},
                {label: 'High-resolution', icon: 'pi pi-sparkles', disabled: !this.chart, command: () => {
                    this.downloadService.downloadHighResChart(this.chart)
                }},            
            ]}             
        ]
    }

}

