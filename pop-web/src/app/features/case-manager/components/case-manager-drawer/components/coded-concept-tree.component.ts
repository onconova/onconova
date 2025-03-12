import { Component, Input, ViewEncapsulation, ChangeDetectionStrategy  } from '@angular/core';
import { TreeModule } from 'primeng/tree';
import { TreeNode } from 'primeng/api';

import { CodedConcept } from 'src/app/shared/openapi';
import { CommonModule } from '@angular/common';

@Component({
    standalone: true,
    selector: 'pop-coded-concept-tree',
    template: `
    <p-tree class="drawer-property-tree" [value]="nodes">
        <ng-template let-node pTemplate="code">                        
            <small class="property-label"> {{ node.label }}</small> <div style="font-family: monospace; font-size: .8rem">{{ node.code }}</div>
        </ng-template>
        <ng-template let-node pTemplate="system">                        
            <small class="property-label">{{ node.label }}</small> <div style="font-family: monospace; font-size: .8rem">{{ node.system }}</div>
        </ng-template>
        <ng-template let-node pTemplate="synonyms" > 
            <ng-container>
                <small class="property-label">{{ node.label }}</small> 
                <div *ngIf="node.synonyms.length === 0">-</div>
                <div>                            
                    <ul class="list-none pl-0">
                        <li *ngFor="let synonym of node.synonyms" style="font-size: .8rem">
                            {{ synonym }}
                        </li>
                    </ul>
                </div>
            </ng-container>                       
        </ng-template>
    </p-tree>
    `,
    imports: [CommonModule, TreeModule]
})
export class CodedConceptTreeComponent {

    @Input({required: true}) concept!: CodedConcept;
    public nodes: TreeNode[] | any[] = [];

    ngOnInit(){
        this.nodes =  [{
            key: '0',
            label: this.concept.display as string,
            children: [
                { key: '0-0', label: 'Code',  type: 'code', code: this.concept.code},
                { key: '0-1', label: 'Code System', type: 'system', system: this.concept.system},
                { key: '0-2', label: 'Synonyms', type: 'synonyms', synonyms: this.concept.synonyms},
            ]
        }]
    }
}