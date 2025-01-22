import { Component, Input, ViewEncapsulation, OnInit, inject, DestroyRef,ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, first, of, map, startWith} from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ModalFormService } from 'src/app/shared/components/modal-form/modal-form.service';

import { Panel } from 'primeng/panel';
import { AvatarModule } from 'primeng/avatar';
import { BadgeModule } from 'primeng/badge';
import { Menu } from 'primeng/menu';
import { MessageService } from 'primeng/api';
import { Timeline } from 'primeng/timeline';
import { MenuItem } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ConfirmationService } from 'primeng/api';
import { Skeleton } from 'primeng/skeleton';

import { AuthService } from 'src/app/core/auth/services/auth.service';

import { CaseManagerDrawerComponent } from '../case-manager-drawer/case-manager-drawer.component';

import { PatientCasesService, PatientCaseDataCategories, PatientCaseDataCompletionStatusSchema } from 'src/app/shared/openapi';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';
import { compileClassDebugInfo } from '@angular/compiler';

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
        Skeleton,
        Timeline,
        ConfirmDialog,
    ],
    providers: [ConfirmationService],
})
export class CaseManagerPanelComponent implements OnInit {

    private readonly patienCaseService = inject(PatientCasesService);
    private readonly modalFormService = inject(ModalFormService);
    private readonly messageService = inject(MessageService);
    private authService = inject(AuthService)
    private confirmationService = inject(ConfirmationService)
    public readonly destroyRef = inject(DestroyRef);

    @Input() title!: string;
    @Input() icon!: LucideIconData;
    @Input() caseId!: string;
    @Input() formComponent!: any;
    @Input() category!: PatientCaseDataCategories;
    @Input() service!: any; 
    public loadingData: boolean = false;
    public data$!: Observable<any>;
    public menuItems$: Observable<MenuItem[]> = of(this.getMenuItems());
    public completed: boolean = false;
    public completedBy: string | null = null;
    public completedAt:  string | null = null;
    public drawerVisible: boolean = false;
    public drawerData: any = {};
    public entries: any[] = [];
    

    ngOnInit(): void {
        if ( this.service ){
            this.data$ = this.service.get(this.caseId)
            if (this.data$) {
                this.refreshEntries()
            }
        }
        if (this.category) {
            this.menuItems$ = this.patienCaseService.getPatientCaseDataCompletionStatus(this.caseId, this.category).pipe(
                map((completed: PatientCaseDataCompletionStatusSchema) => {
                    this.completed = completed.status;
                    this.completedBy = completed.username as string;
                    this.completedAt = completed.timestamp as string;
                    return this.getMenuItems(this.completed)
                }),
                startWith(this.getMenuItems(false))
              );
        }        
    }

    addNewEntry() {    
        this.modalFormService.open(this.formComponent, {}, this.refreshEntries.bind(this));
      }

    refreshEntries() {
        this.loadingData = true;
        this.data$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
            next: (response: any) => {
                this.entries = response.items;
            },
            error: (error: Error) => {
                console.log(error)
            },
            complete: () => {
                this.loadingData = false;
            }
        })
    }

    getMenuItems(completed: boolean = false): MenuItem[] {
         let items: MenuItem[] = [
            {
                label: 'Add',
                icon: 'pi pi-plus',
                disabled: completed,
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
        ]
        if (this.category) {
            items.push({
                label: completed ? 'Mark as incomplete' : 'Mark as complete',
                icon: completed ? 'pi pi-star-fill' : 'pi pi-star',
                styleClass: completed ? 'completed-category' : '',
                command: (event) => {
                    if (completed) {
                        this.confirmDataIncomplete(event);
                    } else {                        
                        this.confirmDataComplete(event);
                    }
                }
            })
        }
        return items
    }

    showDrawer(data: any) {
        this.drawerVisible = true
        this.drawerData = data
    }

    updateEntry(data: any) {
        this.modalFormService.open(this.formComponent, data, this.refreshEntries.bind(this));
    }

    deleteEntry(id: string) {
        this.service.delete(id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
            complete: () => {
                this.refreshEntries()
                this.messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: id })
            },
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error.message })
        })
    }


    confirmDataComplete(event: any) {
        this.confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Close data category',
            message: `Do you confirm that all data entries have been collected? 
            <div class="flex gap-3 my-2">
                <div class="">
                    <small class="text-muted">Total entries</small> 
                    <div>${this.entries.length}</div>
                </div>
                <div class="">
                    <small class="text-muted">Data category</small> 
                    <div class="text-monospace">${this.category}</div>
                </div>
            </div>
            `,
            icon: 'pi pi-question-circle',
            rejectButtonProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptButtonProps: {
                label: 'Confirm complete',
                severity: 'primary',
            },
            accept: () => {
                this.patienCaseService.createPatientCaseDataCompletion(this.caseId, this.category)
                    .pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
                        complete: () => {
                            this.completed = true;
                            this.messageService.add({ severity: 'success', summary: 'Success', detail: `Category ${this.category} marked as complete.`})
                            this.menuItems$ = of(this.getMenuItems(this.completed))
                            this.completedBy = this.authService.getUsername();
                            this.completedAt = new Date().toISOString();
                        }
                    })
            }
        });
    }


    confirmDataIncomplete(event: any) {
        this.confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Open data category',
            message: `Do you confirm that there are data entries missing? 
            <div class="flex gap-3 my-2">
                <div class="">
                    <small class="text-muted">Total entries</small> 
                    <div>${this.entries.length}</div>
                </div>
                <div class="">
                    <small class="text-muted">Data category</small> 
                    <div class="text-monospace">${this.category}</div>
                </div>
            </div>            <div class="flex gap-3 my-2">
                <div class="">
                    <small class="text-muted">Previously completed by</small> 
                    <div>${this.completedBy} (${this.completedAt})</div>
                </div>
            </div>
            `,
            icon: 'pi pi-question-circle',
            rejectButtonProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptButtonProps: {
                label: 'Confirm & Open category',
                severity: 'primary',
            },
            accept: () => {
                this.patienCaseService.deletePatientCaseDataCompletion(this.caseId, this.category)
                    .pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
                        complete: () => {
                            this.completed = false;
                            this.messageService.add({ severity: 'success', summary: 'Success', detail: `Category ${this.category} marked as incomplete.`})
                            this.menuItems$ = of(this.getMenuItems(this.completed))
                        }
                    })
            }
        });
    }

}