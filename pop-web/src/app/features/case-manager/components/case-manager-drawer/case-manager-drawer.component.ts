import { Component, Input, EventEmitter, Output, ViewEncapsulation, inject  } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DrawerModule } from 'primeng/drawer';
import { AvatarModule } from 'primeng/avatar';
import { DividerModule } from 'primeng/divider';
import { Button } from 'primeng/button'
import { SplitButton } from 'primeng/splitbutton';
import { MenuItem } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ConfirmationService } from 'primeng/api';

import { AuthService } from 'src/app/shared/openapi';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';

import { map, first, Observable, share } from 'rxjs';


@Component({
    standalone: true,
    selector: 'app-case-manager-drawer',
    templateUrl: './case-manager-drawer.component.html',
    styleUrl: './case-manager-drawer.component.css',
    encapsulation: ViewEncapsulation.None,
    providers: [
        ConfirmationService,
    ],
    imports: [
        CommonModule,
        LucideAngularModule,
        DrawerModule,
        AvatarModule,
        DividerModule,
        Button,
        SplitButton,
        ConfirmDialog,
    ]
})
export class CaseManagerDrawerComponent {

    private userService = inject(AuthService)
    private confirmationService = inject(ConfirmationService)

    @Input() data!: any;
    @Input() icon!: LucideIconData;
    @Input() visible!: boolean;
    @Output() visibleChange = new EventEmitter<boolean>();
    @Output() delete = new EventEmitter<string>();
    @Output() update = new EventEmitter<any>();

    public properties: any[] = [];
    public createdBy$!: Observable<string>
    public lastUpdatedBy$!: Observable<string>

    public actionItems: MenuItem[] =  [
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            styleClass: 'delete-action',
            command: (event) => {
                this.confirmDelete(event);
            }
        },
        {
            label: 'Export',
            icon: 'pi pi-file-export',
            command: () => {
                console.log('export', this.data.id)
            }
        },
    ]

    prepareDisplayData() {
        this.createdBy$ = this.userService.getUserById(this.data.createdById).pipe(map(user => user.username), first())
        this.lastUpdatedBy$ = this.userService.getUserById(this.data.updatedByIds[this.data.updatedByIds.length-1]).pipe(map(user => user.username), first())
        this.properties = []
        Object.entries(this.data).forEach(
            (pair) => {
                let key = pair[0]
                let value = pair[1] 
                if (!value || ['caseId', 'createdById', 'updatedByIds', 'id', 'createdAt', 'updatedAt', 'description'].includes(key)) {
                    return
                }
                if (value instanceof Object && 'display' in value) {
                    value = value['display'];
                }
                console.log(key, value)
                this.properties.push({
                    label: key.replace(/([A-Z])/g, " $1"),
                    value: value
                })
            }
        )
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