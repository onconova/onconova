import { Component, Input, ViewEncapsulation, OnInit, inject  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, first } from 'rxjs';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';

import { Panel } from 'primeng/panel';
import { AvatarModule } from 'primeng/avatar';
import { BadgeModule } from 'primeng/badge';
import { Menu } from 'primeng/menu';
import { MessageService } from 'primeng/api';
import { Timeline } from 'primeng/timeline';

import { CaseManagerDrawerComponent } from '../case-manager-drawer/case-manager-drawer.component';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';

@Component({
    standalone: true,
    selector: 'app-case-manager-panel',
    templateUrl: './case-manager-panel.component.html',
    styleUrl: './case-manager-panel.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CaseManagerDrawerComponent,
        CommonModule,
        LucideAngularModule,
        Panel,
        AvatarModule,
        Menu,
        BadgeModule,
        Timeline,
    ]
})
export class CaseManagerPanelComponent implements OnInit {

    private modalFormService = inject(ModalFormService);
    private messageService = inject(MessageService);

    @Input() title!: string;
    @Input() icon!: LucideIconData;
    @Input() caseId!: string;
    @Input() formComponent!: any;
    @Input() service!: any; 
    public data$!: Observable<any>;

    drawerVisible: boolean = false;
    drawerData: any = {};
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
        if ( this.service ){
            console.log(this.caseId)
            this.data$ = this.service.get(this.caseId)
            if (this.data$) {
                this.refreshEntries()
            }
        }

    }

    addNewEntry() {    
        this.modalFormService.open(this.formComponent, {}, this.refreshEntries.bind(this));
      }

    refreshEntries() {
        this.data$.subscribe(
            (response: any) => {
                console.log(response)
                this.entries = response.items;
            },
            (error: Error) => {
                console.log(error)
            }
        )
    }

    showDrawer(data: any) {
        this.drawerVisible = true
        this.drawerData = data
    }

    updateEntry(data: any) {
        console.log('UPDATE', data)
        this.modalFormService.open(this.formComponent, data, this.refreshEntries.bind(this));
    }

    deleteEntry(id: string) {
        this.service.delete(id).pipe(first()).subscribe({
            complete: () => {
                this.refreshEntries()
                this.messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: id })
            },
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error.message })
        })
    }
}