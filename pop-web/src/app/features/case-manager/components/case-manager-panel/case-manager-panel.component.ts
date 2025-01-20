import { Component, Input, ViewEncapsulation, OnInit, inject, DestroyRef  } from '@angular/core';
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

import { CaseManagerDrawerComponent } from '../case-manager-drawer/case-manager-drawer.component';

import { PatientCasesService, PatientCaseDataCategories } from 'src/app/shared/openapi';

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
        Timeline,
    ]
})
export class CaseManagerPanelComponent implements OnInit {

    private readonly patienCaseService = inject(PatientCasesService);
    private readonly modalFormService = inject(ModalFormService);
    private readonly messageService = inject(MessageService);
    public readonly destroyRef = inject(DestroyRef);

    @Input() title!: string;
    @Input() icon!: LucideIconData;
    @Input() caseId!: string;
    @Input() formComponent!: any;
    @Input() category!: PatientCaseDataCategories;
    @Input() service!: any; 
    public data$!: Observable<any>;
    public menuItems$: Observable<MenuItem[]> = of(this.getMenuItems());
    public complete: boolean = false;
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
                map(completed => {
                    this.complete = completed
                    return this.getMenuItems(completed)
                }),
                startWith(this.getMenuItems(false))
              );
        }        
    }

    addNewEntry() {    
        this.modalFormService.open(this.formComponent, {}, this.refreshEntries.bind(this));
      }

    refreshEntries() {
        this.data$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
            next: (response: any) => {
                console.log(response)
                this.entries = response.items;
            },
            error: (error: Error) => {
                console.log(error)
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
                command: () => {
                    if (completed) {
                        this.patienCaseService.deletePatientCaseDataCompletion(this.caseId, this.category)
                            .pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
                                complete: () => {
                                    this.complete = false;
                                    this.messageService.add({ severity: 'success', summary: 'Success', detail: `Category ${this.category} marked as incomplete.`})
                                    this.menuItems$ = of(this.getMenuItems(this.complete))
                                }
                            })
                    } else {
                        this.patienCaseService.createPatientCaseDataCompletion(this.caseId, this.category)
                            .pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
                                complete: () => {
                                    this.complete = true;
                                    this.messageService.add({ severity: 'success', summary: 'Success', detail: `Category ${this.category} marked as complete.`})
                                    this.menuItems$ = of(this.getMenuItems(this.complete))
                                }
                            })
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
}