import { Component, Input,inject, Output, EventEmitter, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EMPTY, Observable, expand, first, map, reduce} from 'rxjs';
import { rxResource } from '@angular/core/rxjs-interop';

import { Panel } from 'primeng/panel';
import { AvatarModule } from 'primeng/avatar';
import { BadgeModule } from 'primeng/badge';
import { Menu } from 'primeng/menu';
import { MessageService } from 'primeng/api';
import { MenuItem } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ConfirmationService } from 'primeng/api';
import { Skeleton } from 'primeng/skeleton';

import { AuthService } from 'src/app/core/auth/services/auth.service';
import { CaseManagerDrawerComponent } from '../case-manager-drawer/case-manager-drawer.component';
import { PatientCasesService, PatientCaseDataCategoryChoices } from 'onconova-api-client';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';
import { CaseManagerPanelTimelineComponent } from "./components/case-manager-panel-timeline.component";
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormHeaderComponent } from 'src/app/features/forms/modal-form-header.component';
import { Button } from 'primeng/button';
import { Tooltip } from 'primeng/tooltip';


export interface DataService {
    get: ({request} : any) => Observable<{items: any[]}>;
    delete: (id: string) => Observable<any>;
    history: (id: string) => Observable<any>;
}

@Component({
    selector: 'onconova-case-manager-panel',
    templateUrl: './case-manager-panel.component.html',
    imports: [
        CaseManagerDrawerComponent,
        CommonModule,
        LucideAngularModule,
        Panel,
        Tooltip,
        AvatarModule,
        Button,
        Menu,
        BadgeModule,
        Skeleton,
        ConfirmDialog,
        CaseManagerPanelTimelineComponent
    ],
    providers: [ConfirmationService]
})
export class CaseManagerPanelComponent {

    @Output() onCompletionChange = new EventEmitter<boolean>; 

    readonly #patienCaseService = inject(PatientCasesService);
    readonly #messageService = inject(MessageService);
    readonly #authService = inject(AuthService);
    readonly #confirmationService = inject(ConfirmationService)
    readonly #dialogservice = inject(DialogService);

    @Input() formComponent!: any;
    readonly anonymized = input<boolean>(true)


    public caseId = input.required<string>();
    public category = input.required<PatientCaseDataCategoryChoices>();
    public service = input.required<DataService>();
    public title = input<string>();
    public icon = input.required<LucideIconData>();

    protected dataCompletionStatus = rxResource({
        request: () => ({caseId: this.caseId(), category: this.category()}),
        loader: ({request}) => this.#patienCaseService.getPatientCaseDataCompletionStatus(request),
    });
    public currentUser = computed(() => this.#authService.user());
    public isCompleted = computed(() => this.dataCompletionStatus.value()?.status);
    public data = rxResource({
        request: () => ({caseId: this.caseId(), anonymized: this.anonymized(), offset: 0, limit: 20}),
        loader: ({request}) => this.service().get(request).pipe(
            expand((response: any) => {    
                const nextOffset = request.offset + request.limit;
                // Check if there are more entries
                if (nextOffset < response.count) {
                    const nextRequest = { ...request, offset: nextOffset };
                    request = nextRequest; 
                    return this.service().get(nextRequest);
                } else {
                    // No more entries, complete the stream
                    return EMPTY;
                }
            }),
            map(response => response.items),    
            reduce((allItems, items) => allItems.concat(items), [] as any[])
        )
    });

    #modalFormConfig = computed( () => ({
        data: {
            title: this.title(),
            subtitle: 'Add a new entry',
            icon: this.icon(),
        },
        templates: {
            header: ModalFormHeaderComponent,
        },   
        modal: true,
        closable: true,
        width: '45vw',
        styleClass: 'onconova-modal-form',
        breakpoints: {
            '1700px': '50vw',
            '960px': '75vw',
            '640px': '90vw'
        },
    }))
    #modalFormRef: DynamicDialogRef | undefined;

    public drawerVisible: boolean = false;
    public drawerData: any = {};
    public drawerHistory!: any;    

    public menuItems = computed(() => {
        let items: MenuItem[] = [
            {
                label: 'Add',
                icon: 'pi pi-plus',
                disabled: this.isCompleted() || this.anonymized(),
                command: () => this.addNewEntry()
            },
            {
                label: 'Refresh',
                icon: 'pi pi-refresh',
                command: () => this.data.reload()
            },
            {
                separator: true
            },
        ]
        if (this.category()) {
            items.push({
                label: this.isCompleted() ? 'Mark as incomplete' : 'Mark as complete',
                icon: this.isCompleted() ? 'pi pi-star-fill' : 'pi pi-star',
                styleClass: this.isCompleted() ? 'completed-category' : '',
                disabled: this.anonymized(),
                command: (event) => {
                    if (this.isCompleted()) {
                        this.confirmDataIncomplete(event);
                    } else {                        
                        this.confirmDataComplete(event);
                    }
                }
            })
        }
        return items
    })

    addNewEntry() {    
        this.#modalFormRef = this.#dialogservice.open(this.formComponent, {
            inputValues: {
                caseId: this.caseId(),
            },
            ...this.#modalFormConfig()
        })
        this.reloadDataIfClosedAndSaved(this.#modalFormRef)
    }

    updateEntry(data: any) {
        this.#modalFormRef = this.#dialogservice.open(this.formComponent, {
            inputValues: {
                caseId: this.caseId(),
                resourceId: data.id,
                initialData: data
            },
            ...this.#modalFormConfig(),
            data: {
                title: this.title(),
                subtitle: 'Update an existing entry',
                icon: this.icon(),
            },
        })
        this.reloadDataIfClosedAndSaved(this.#modalFormRef)
    }

    reloadDataIfClosedAndSaved(modalFormRef: DynamicDialogRef) {
        modalFormRef.onClose.subscribe((data: any) => {
            if (data?.saved) {
                this.data.reload()
            }
        })    
    }

    showDrawer(data: any) {
        this.drawerVisible = true;
        this.drawerData = data;
        this.drawerHistory = this.service().history(data.id).pipe(map((response: any) => response.items));
    }

    deleteEntry(id: string) {
        this.service().delete(id).pipe(first()).subscribe({
            complete: () => {
                this.data.reload()
                this.#messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: id })
            },
            error: (error: any) => this.#messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error.error.detail })
        })
    }

    confirmDataComplete(event: any) {
        this.#confirmationService.confirm({
            key: 'completeConfirmDialog',
            accept: () => {
                this.#patienCaseService.createPatientCaseDataCompletion({caseId:this.caseId(), category: this.category()})
                    .pipe(first()).subscribe({
                        complete: () => {
                            this.dataCompletionStatus.reload();
                            this.#messageService.add({ severity: 'success', summary: 'Success', detail: `Category "${this.category()}" marked as complete.`})
                            this.onCompletionChange.emit(true)
                        }
                    })
            }
        });
    }

    confirmDataIncomplete(event: any) {
        this.#confirmationService.confirm({
            key: 'incompleteConfirmDialog',
            accept: () => {
                this.#patienCaseService.deletePatientCaseDataCompletion({caseId: this.caseId(), category: this.category()})
                    .pipe(first()).subscribe({
                        complete: () => {
                            this.dataCompletionStatus.reload();
                            this.#messageService.add({ severity: 'success', summary: 'Success', detail: `Category "${this.category()}" marked as incomplete.`})
                            this.onCompletionChange.emit(false)
                        }
                    })
            }
        });
    }

}