import { Component, Input, ViewEncapsulation, OnInit, inject, DestroyRef,ChangeDetectionStrategy, Output, EventEmitter, Signal, signal, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, first, of, map, startWith} from 'rxjs';
import { rxResource, takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';

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
import { PatientCasesService, PatientCaseDataCategories } from 'src/app/shared/openapi';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';
import { CaseManagerPanelTimelineComponent } from "./components/case-manager-panel-timeline.component";
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { ModalFormComponent } from 'src/app/shared/components/modal-form/modal-form.component';
import { ModalFormHeaderComponent } from 'src/app/features/forms/modal-form-header.component';


export interface DataService {
    get: (caseId: string) => Observable<{items: any[]}>;
    delete: (id: string) => Observable<any>;
    history: (id: string) => Observable<any>;
}

@Component({
    selector: 'pop-case-manager-panel',
    templateUrl: './case-manager-panel.component.html',
    imports: [
        CaseManagerDrawerComponent,
        CommonModule,
        LucideAngularModule,
        Panel,
        AvatarModule,
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

    private readonly patienCaseService = inject(PatientCasesService);
    private readonly modalFormService = inject(ModalFormService);
    private readonly messageService = inject(MessageService);
    public readonly authService = inject(AuthService)
    private readonly confirmationService = inject(ConfirmationService)
    #dialogservice = inject(DialogService)

    @Input() formComponent!: any;


    public caseId = input.required<string>();
    public category = input.required<PatientCaseDataCategories>();
    public service = input.required<DataService>();
    public title = input<string>();
    public icon = input.required<LucideIconData>();

    private dataCompletionStatus = rxResource({
        request: () => ({caseId: this.caseId(), category: this.category()}),
        loader: ({request}) => this.patienCaseService.getPatientCaseDataCompletionStatus(request),
    })
    public isCompleted = computed(() => this.dataCompletionStatus.value()?.status)
    public data = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.service().get(request.caseId).pipe(map(response => response.items)),
    })

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
        width: '35vw',
        styleClass: 'pop-modal-form',
        breakpoints: {
            '1300px': '50vw',
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
                disabled: this.isCompleted(),
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
            ...this.#modalFormConfig()
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
                this.messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: id })
            },
            error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error.error.detail })
        })
    }

    confirmDataComplete(event: any) {
        this.confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Close data category',
            icon: 'pi pi-question-circle',
            message: `Do you confirm that all data entries have been collected? 
            <div class="flex gap-3 my-2">
                <div class="">
                    <small class="text-muted">Total entries</small> 
                    <div>${this.data.value()?.entries.length}</div>
                </div>
                <div class="">
                    <small class="text-muted">Data category</small> 
                    <div class="text-monospace">${this.category()}</div>
                </div>
            </div>
            `,
            rejectButtonProps: {label: 'Cancel', severity: 'secondary', outlined: true},
            acceptButtonProps: {label: 'Confirm complete', severity: 'primary',},
            accept: () => {
                this.patienCaseService.createPatientCaseDataCompletion({caseId:this.caseId(), category: this.category()})
                    .pipe(first()).subscribe({
                        complete: () => {
                            this.dataCompletionStatus.reload();
                            this.messageService.add({ severity: 'success', summary: 'Success', detail: `Category ${this.category()} marked as complete.`})
                            this.onCompletionChange.emit(true)
                        }
                    })
            }
        });
    }

    confirmDataIncomplete(event: any) {
        this.confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Open data category',
            icon: 'pi pi-question-circle',
            message: `Do you confirm that there are data entries missing? 
            <div class="flex gap-3 my-2">
                <div class="">
                    <small class="text-muted">Total entries</small> 
                    <div>${this.data.value()?.entries.length}</div>
                </div>
                <div class="">
                    <small class="text-muted">Data category</small> 
                    <div class="text-monospace">${this.category()}</div>
                </div>
            </div>            
            <div class="flex gap-3 my-2">
                <div class="">
                    <small class="text-muted">Previously completed by</small> 
                    <div>${this.dataCompletionStatus.value()?.username} (${this.dataCompletionStatus.value()?.timestamp})</div>
                </div>
            </div>
            `,
            rejectButtonProps: {label: 'Cancel', severity: 'secondary', outlined: true},
            acceptButtonProps: {label: 'Confirm & Open category', severity: 'primary'},
            accept: () => {
                this.patienCaseService.deletePatientCaseDataCompletion({caseId: this.caseId(), category: this.category()})
                    .pipe(first()).subscribe({
                        complete: () => {
                            this.dataCompletionStatus.reload();
                            this.messageService.add({ severity: 'success', summary: 'Success', detail: `Category ${this.category} marked as incomplete.`})
                            this.onCompletionChange.emit(false)
                        }
                    })
            }
        });
    }

}