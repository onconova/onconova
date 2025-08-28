import { Component, Input, EventEmitter, Output, ViewEncapsulation, inject, ChangeDetectionStrategy, Pipe,PipeTransform, SimpleChanges, computed, input, model  } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DrawerModule } from 'primeng/drawer';
import { AvatarModule } from 'primeng/avatar';
import { DividerModule } from 'primeng/divider';
import { Button } from 'primeng/button'
import { SplitButton } from 'primeng/splitbutton';
import { MenuItem, MessageService } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ConfirmationService } from 'primeng/api';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';

import { first, map, Observable } from 'rxjs';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DrawerDataPropertiesComponent } from './components/drawer-data-properties.component';
import { DownloadService } from 'src/app/shared/services/download.service';
import { OncologicalResource } from 'src/app/shared/models/resource.type';
import { UserBadgeComponent } from "../../../../../shared/components/user-badge/user-badge.component";
import { HistoryEvent, InteroperabilityService, PaginatedHistoryEvent, User } from 'onconova-api-client';
import { Timeline } from 'primeng/timeline';
import { rxResource } from '@angular/core/rxjs-interop';
import { Skeleton } from 'primeng/skeleton';
import { ExportConfirmDialogComponent } from "../../../../../shared/components/export-confirm-dialog/export-confirm-dialog.component";

@Component({
    selector: 'onconova-case-manager-drawer',
    templateUrl: './case-manager-drawer.component.html',
    providers: [
        ConfirmationService,
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
    CommonModule,
    LucideAngularModule,
    DrawerModule,
    AvatarModule,
    DividerModule,
    Button,
    Skeleton,
    SplitButton,
    ConfirmDialog,
    DrawerDataPropertiesComponent,
    UserBadgeComponent,
    Timeline,
    ExportConfirmDialogComponent
]
})
export class CaseManagerDrawerComponent {
    // Component inputs
    public data = input.required<OncologicalResource>();
    public history$!: Observable<HistoryEvent[]>;
    public icon = input.required<LucideIconData>();
    public visible = model<boolean>(false);
    public editable = input<boolean>(true);
    public anonymized = computed<boolean>(()=> (this.data() as any).anonymized ? true : false);
    public styleClass = input<string>('');
    public historyService = input.required<(resourceId: string) => Observable<PaginatedHistoryEvent>>();

    // Service injections
    readonly #authService = inject(AuthService);
    readonly #confirmationService = inject(ConfirmationService);
    readonly #downloadService = inject(DownloadService);
    readonly #interoperabilityService = inject(InteroperabilityService);
    readonly #messageService = inject(MessageService);

    // Service injections
    @Output() visibleChange = new EventEmitter<boolean>();
    @Output() delete = new EventEmitter<string>();
    @Output() update = new EventEmitter<any>();

    public history = rxResource({
        request: () => this.data().id,
        loader: ({request}) => this.historyService()(request).pipe(map(response => response.items))
    })

    // Component properties for the UI 
    public currentUser = computed((): User => this.#authService.user())
    public actionItems = computed((): MenuItem[] => [
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            disabled: !this.editable(),
            styleClass: 'delete-action',
            command: (event: any) => this.confirmDelete(event),
        },
        {
            label: 'Export',
            disabled: !this.currentUser().canExportData,
            icon: 'pi pi-file-export',
            command: () => this.exportResource(),
        },
    ]);

    exportResource() {
        this.#confirmationService.confirm({
            key: 'exportConfirmation',
            accept: () => {
                this.#messageService.add({severity: 'info', summary: 'Export in progress', detail:'Preparing data for download. Please wait...'})
                this.#interoperabilityService.exportResource({resourceId: this.data().id}).pipe(first()).subscribe({
                    next: (response) => this.#downloadService.downloadAsJson(response, 'onconova-resource-' + response.id),
                    complete: () => this.#messageService.add({ severity: 'success', summary: 'Successfully exported', detail: this.data().description }),
                    error: (error: any) => this.#messageService.add({ severity: 'error', summary: 'Error exporting resource', detail: error.error.detail })
                })
            }
        })        
    }

    confirmDelete(event: any) {
        this.#confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Danger Zone',
            message: `Are you sure you want to delete this entry? 
            <div class="mt-1 font-medium text-secondary">
            <small>${this.data().description}</small>
            </div>
            `,
            icon: 'pi pi-exclamation-triangle',
            rejectButtonProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptButtonProps: {
                label: 'Delete',
                severity: 'danger',
            },
            accept: () => {
                this.delete.emit(this.data().id);
                this.visibleChange.emit(false);
            }
        });
    }




}