import { Component, Input, ViewEncapsulation, OnInit, inject  } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ModalFormService } from '../../../core/components/modal-form/modal-form.service';

import { PanelModule } from 'primeng/panel';
import { AvatarModule } from 'primeng/avatar';
import { BadgeModule } from 'primeng/badge';
import { MenuModule } from 'primeng/menu';
import { TimelineModule } from 'primeng/timeline';


import { LucideAngularModule } from 'lucide-angular';


@Component({
    standalone: true,
    selector: 'app-case-manager-panel',
    templateUrl: './case-manager-panel.component.html',
    styleUrl: './case-manager-panel.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule,
        LucideAngularModule,
        PanelModule,
        AvatarModule,
        MenuModule,
        BadgeModule,
        TimelineModule,
    ]
})
export class CaseManagerPanelComponent implements OnInit {

    private modalFormService = inject(ModalFormService)


    @Input() title!: string;
    @Input() icon!: string;
    @Input() formComponent!: any;
    @Input() dataService!: any;

    public entries: any[] = [];



    public menuItems = [
        {
            label: 'Add',
            icon: 'pi pi-plus',
            command: () => {
                this.addNewEntry()
            }
        },
        {
            label: 'Refresh',
            icon: 'pi pi-refresh',
            command: () => {
                this.refreshEntries()
            }
        },
        {
            separator: true
        },
        {
            label: 'Finalize',
            icon: 'pi pi-star',
            command: () => {
                console.log('Finalized', this.title)
            }
        }
    ];
    

    ngOnInit(): void {
        if (this.dataService) {
            this.refreshEntries()
        }
    }

    addNewEntry() {    
        console.log(this.formComponent)
        this.modalFormService.open(this.formComponent, {});
      }

    refreshEntries() {
        this.dataService.subscribe(
            (response: any) => {
                console.log(response)
                this.entries = response.items;
            },
            (error: Error) => {
                console.log(error)
            }
        )
    }

}