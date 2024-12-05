import { Component, Input, ViewEncapsulation, OnInit, inject  } from '@angular/core';

import { ModalFormService } from '../../../core/components/modal-form/modal-form.service';


@Component({
    selector: 'app-case-manager-panel',
    templateUrl: './case-manager-panel.component.html',
    styleUrl: './case-manager-panel.component.css',
    encapsulation: ViewEncapsulation.None
})
export class CaseManagerPanelComponent implements OnInit {
    @Input() title!: string;
    @Input() icon!: string;

    @Input() formComponent!: any;
    @Input() dataService!: any;

    public entries: any[] = [];

    private modalFormService = inject(ModalFormService)


    public menuItems = [
        {
            label: 'Add',
            icon: 'pi pi-plus',
            command: () => {
                console.log('Add new', this.title)
                this.addNewEntry()
            }
        },
        {
            label: 'Refresh',
            icon: 'pi pi-refresh',
            command: () => {
                console.log('Refresh', this.title)
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
                response.items.forEach((entry: any) => {
                    this.entries.push(entry)
                });
            },
            (error: Error) => {
                console.log(error)
            }
        )
    }

}