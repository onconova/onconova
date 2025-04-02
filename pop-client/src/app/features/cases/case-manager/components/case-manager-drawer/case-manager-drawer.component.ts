import { Component, Input, EventEmitter, Output, ViewEncapsulation, inject, ChangeDetectionStrategy, Pipe,PipeTransform, SimpleChanges  } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DrawerModule } from 'primeng/drawer';
import { AvatarModule } from 'primeng/avatar';
import { DividerModule } from 'primeng/divider';
import { Button } from 'primeng/button'
import { SplitButton } from 'primeng/splitbutton';
import { MenuItem } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ConfirmationService } from 'primeng/api';

import { GetFullNamePipe } from 'src/app/shared/pipes/full-name.pipe';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';

import { Observable } from 'rxjs';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DrawerDataPropertiesComponent } from './components/drawer-data-properties.component';
import { DownloadService } from 'src/app/shared/services/download.service';
import { OncologicalResource } from 'src/app/shared/models/resource.type';


@Component({
    standalone: true,
    selector: 'pop-case-manager-drawer',
    templateUrl: './case-manager-drawer.component.html',
    styleUrl: './case-manager-drawer.component.css',
    encapsulation: ViewEncapsulation.None,
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
        GetFullNamePipe,
        SplitButton,
        ConfirmDialog,
        DrawerDataPropertiesComponent,
    ]
})
export class CaseManagerDrawerComponent {

    public authService = inject(AuthService)
    private confirmationService = inject(ConfirmationService)
    private downloadService = inject(DownloadService)

    @Output() visibleChange = new EventEmitter<boolean>();
    @Output() delete = new EventEmitter<string>();
    @Output() update = new EventEmitter<any>();

    @Input() data!: OncologicalResource;
    @Input() icon!: LucideIconData;
    @Input() visible!: boolean;
    @Input() editable: boolean = true;
    public createdBy$!: Observable<string>
    public lastUpdatedBy$!: Observable<string>
    public actionItems!: MenuItem[];
    
    ngOnChanges(changes:SimpleChanges){
        this.actionItems =  [
            {
                label: 'Delete',
                icon: 'pi pi-trash',
                disabled: !this.editable,
                styleClass: 'delete-action',
                command: (event) => {
                    this.confirmDelete(event);
                }
            },
            {
                label: 'Export',
                disabled: !this.authService.user.canExportData,
                icon: 'pi pi-file-export',
                command: () => {
                    this.downloadService.downloadAsJson(this.data, 'pop-resource-' + this.data.id)
                }
            },
        ]
    }

    confirmDelete(event: any) {
        this.confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Danger Zone',
            message: `Are you sure you want to delete this entry? 
            <div class="mt-1 font-bold text-secondary">
            <small>${this.data.description}</small>
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
                this.delete.emit(this.data.id);
                this.visibleChange.emit(false);
            }
        });
    }




}