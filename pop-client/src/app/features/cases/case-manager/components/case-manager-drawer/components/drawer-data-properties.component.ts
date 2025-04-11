import { Component, inject, Input, SimpleChanges, ViewEncapsulation  } from '@angular/core';

import { CodedConcept, Measure, Period } from 'src/app/shared/openapi';
import { CommonModule } from '@angular/common';
import { CodedConceptTreeComponent } from './coded-concept-tree.component';
import { ReplacePipe } from 'src/app/shared/pipes/replace.pipe';
import { TypeCheckService } from 'src/app/shared/services/type-check.service';
import { ResolveResourcePipe } from 'src/app/shared/pipes/resolve-resource.pipe';
import { Skeleton } from 'primeng/skeleton';

@Component({
    standalone: true,
    selector: 'pop-drawer-properties',
    template: `
        @switch (dataType) {
            @case ('null') {
                <div class="text-muted">-</div> 
            }
            @case ('Period') {
                <div>{{ data.start | date }} - {{ data.end | date }}</div> 
            }
            @case ('Measure') {
                <div>{{ data.value | number: '1.0-4' }} {{ data.unit | replace:'__':'/' }}</div> 
            }
            @case ('number') {
                <div>{{ data | number: '1.0-4' }}</div> 
            }
            @case ('Date') {
                <div>{{ data | date }}</div> 
            }
            @case ('UUID') {
                @let reference = data | resolve | async;
                @if (reference) {
                    <div>{{ reference }}</div> 
                } @else {
                    <p-skeleton height="1.5rem" width="10rem"/>
                }
            }
            @case ('CodedConcept') {
                <div>
                    <pop-coded-concept-tree [concept]="data"/>
                </div> 
            }
            @case ('Array') {
                <div>
                    <ul class="list-property">
                        @for (item of data; track $index; let idx = $index; let first = $first;) {
                            <li [ngClass]="first ? 'mt-2' : ''">
                                <small class="text-muted"><i class="pi pi-box"></i> {{ label | slice:0:-1 | titlecase | replace:'Id':' ' }} #{{idx+1}}</small>
                                <div class="nested-properties">
                                    <pop-drawer-properties [data]="item"/>
                                </div>
                            </li>                            
                        }
                    </ul>
                </div> 
            }
            @case ('object') {
                <div>
                    @for (property of subProperties; track $index;) {
                        <div class="property">             
                            <small class="property-label {{ data ? '' : 'text-muted'}}">
                                {{ property.label | titlecase | replace:'Ids':' ' | replace:'Id':' '}}
                            </small>
                            <pop-drawer-properties [data]="property.value" [label]='property.label'/>
                        </div>
                    }
                </div> 
            }
            @default {
                <div>{{ data }}</div>
            }
        }
    `,
    styles: `
        ul.list-property {
            padding-left: .25rem;
            margin-top: .25rem;
        }
        ul.list-property > li {
            list-style: none;
        }
        .nested-properties {
            margin-left: .45rem;
            padding-left: .5rem;
            padding-top: .5rem;
            border-left: .1rem solid color-mix(in srgb, var(--p-content-color), transparent 55%);
        }
    `,
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule, 
        Skeleton,
        CodedConceptTreeComponent, 
        ReplacePipe, 
        ResolveResourcePipe
    ]
})
export class DrawerDataPropertiesComponent {

    private readonly typeCheckService = inject(TypeCheckService)

    @Input({required: true}) data!: any;
    @Input() label!: string;
    public dataType!: string;
    public subProperties: any[] = [];

    ngOnChanges(changes: SimpleChanges) {
        if (changes['data'] && this.data) {
            this.processData();
        }
    }
    
    processData(){
        if (this.typeCheckService.isArray(this.data)) {
            this.dataType = this.data.length > 0 ? 'Array' : 'null';
        } else if (this.typeCheckService.isObject(this.data)) {
            if (this.typeCheckService.isCodeableConcept(this.data)){
                this.dataType = 'CodedConcept';
            } else if (this.typeCheckService.isPeriod(this.data)) {
                this.dataType = 'Period';                
            } else if (this.typeCheckService.isMeasure(this.data)) {
                this.dataType = 'Measure';                
            } else if (this.typeCheckService.isPeriod(this.data)) {
                this.dataType = 'Period';                                   
            } else {
                this.dataType = 'object';     
                this.subProperties = Object.entries(this.data).map(
                    (pair) => {
                        let key = pair[0]
                        let value = pair[1] 
                        if (!value || ['caseId', 'createdBy', 'updatedBy', 'id', 'createdAt', 'updatedAt', 'description', 'externalSource', 'externalSourceId'].includes(key)) {
                            return null
                        }
                        if (this.typeCheckService.isArray(value) && value.length==0) {
                            return null
                        }
                        return {
                            label: key.replace(/([A-Z])/g, " $1"),
                            value: value
                        }
                    }
                ).filter(property => property !== null)             
            }                    
        } else if (this.typeCheckService.isUUID(this.data)) {
            this.dataType = 'UUID';    
        } else if (this.typeCheckService.isDate(this.data) || this.typeCheckService.isDateString(this.data)) {
            this.dataType = 'Date';                                
        } else {
            this.dataType = `${typeof(this.data)}`;
        }
    }
}