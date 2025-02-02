import { Component, Input, EventEmitter, Output, ViewEncapsulation, inject, ChangeDetectionStrategy, Pipe,PipeTransform  } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DrawerModule } from 'primeng/drawer';
import { AvatarModule } from 'primeng/avatar';
import { DividerModule } from 'primeng/divider';
import { Button } from 'primeng/button'
import { SplitButton } from 'primeng/splitbutton';
import { MenuItem } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ConfirmationService } from 'primeng/api';
import { Tree } from 'primeng/tree';

import { AuthService, CodedConceptSchema } from 'src/app/shared/openapi';

import { LucideAngularModule } from 'lucide-angular';
import { LucideIconData } from 'lucide-angular/icons/types';

import { map, first, Observable, share } from 'rxjs';


@Pipe({
    standalone: true,
    name: 'getConceptTree'
  })
export class GetConceptTreePipe implements PipeTransform {
  
    transform(concept: CodedConceptSchema) {
        let nodes =  [{
            key: '0',
            label: concept.display,
            children: [
                { key: '0-0', label: 'Code', icon: 'pi pi-qr-code', children:[
                    { key: '0-0-0', label: concept.code, style: 'font-family: monospace; font-size: .8rem'}
                ]},
                { key: '0-1', label: 'Code System', icon: 'pi pi-link', children:[
                    { key: '0-1-0', label: concept.system, style: 'font-family: monospace; font-size: .8rem'}
                ]},
                { key: '0-2', label: `Synonyms`, icon: 'pi pi-language', children: concept.synonyms?.map((synonym, index) => (
                    {key: `0-2-${index}`, label: synonym}
                ))},
            ]
        }]
        return nodes
    }
}


@Pipe({
    standalone: true,
    name: 'getObjectProperties'
  })
export class getObjectPropertiesPipe implements PipeTransform {
  
    transform(object: object) {
        return Object.entries(object).map(
            (pair) => {
                let key = pair[0]
                let value = pair[1] 
                if (!value || ['caseId', 'createdById', 'updatedByIds', 'id', 'createdAt', 'updatedAt', 'description'].includes(key)) {
                    return null
                }
                return {
                    label: key.replace(/([A-Z])/g, " $1"),
                    value: value
                }
            }
        )
    }
}

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
        GetConceptTreePipe,
        getObjectPropertiesPipe,
        Tree,
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

    public readonly isCodeableConcept = (value: CodedConceptSchema): value is CodedConceptSchema => !!value?.code;
    public readonly isObject = (x: any) => typeof x === 'object' && !Array.isArray(x) && x !== null
    public readonly isArray = (x: any) => x instanceof Array

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