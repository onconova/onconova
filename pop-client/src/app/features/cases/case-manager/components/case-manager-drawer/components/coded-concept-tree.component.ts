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
            <small class="property-label"> {{ node.label }}</small> <div class="monospace text-sm">{{ node.code }}</div>
        </ng-template>
        <ng-template let-node pTemplate="system">                        
            <small class="property-label">{{ node.label }}</small> <div class="monospace text-sm">{{ node.system }}</div>
        </ng-template>
        <ng-template let-node pTemplate="synonyms" > 
            <small class="property-label">{{ node.label }}</small> 
            <div>  
                @if (node.synonyms.length) {                    
                    <ul class="list-none pl-0">
                        @for (synonym of node.synonyms; track $index) {
                            <li class="text-sm">
                                {{ synonym }}
                            </li>
                        }
                    </ul>
                } @else {
                    -
                }     
            </div>                
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