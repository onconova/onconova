import { Component, computed, inject, input, ViewEncapsulation  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CodedConceptTreeComponent } from './coded-concept-tree.component';
import { ReplacePipe } from 'src/app/shared/pipes/replace.pipe';
import { TypeCheckService } from 'src/app/shared/services/type-check.service';
import { ResolveResourcePipe } from 'src/app/shared/pipes/resolve-resource.pipe';
import { Skeleton } from 'primeng/skeleton';

@Component({
    selector: 'pop-drawer-properties',
    template: `
        @switch (dataType()) {
            @case ('null') {
                <div class="text-muted">-</div> 
            }
            @case ('boolean') {
                <div>{{ data() ? 'Yes' : 'No' }}</div> 
            }
            @case ('Range') {
                <div>{{ data().start || 'Unknown' }} - {{ data().end || 'Unknown' }}</div> 
            }
            @case ('Period') {
                <div>{{ data().start | date }} - {{ (data().end | date) ?? 'ongoing' }}</div> 
            }
            @case ('Measure') {
                <div>{{ data().value | number: '1.0-4' }} {{ data().unit | replace:'__':'/' }}</div> 
            }
            @case ('number') {
                <div>{{ data() | number: '1.0-4' }}</div> 
            }
            @case ('Date') {
                <div>{{ data() | date }}</div> 
            }
            @case ('UUID') {
                @let reference = data() | resolve | async;
                @if (reference) {
                    <div>{{ reference }}</div> 
                } @else {
                    <p-skeleton height="1.5rem" width="10rem"/>
                }
            }
            @case ('CodedConcept') {
                <div>
                    <pop-coded-concept-tree [concept]="data()"/>
                </div> 
            }
            @case ('Array') {
                <div>
                    <ul class="list-property">
                        @for (item of data(); track $index; let idx = $index; let first = $first;) {
                            <li [ngClass]="first ? 'mt-2' : ''">
                                @if (label(); as label) {
                                    <small class="text-muted"><i class="pi pi-box"></i> {{ label | slice:0:-1 | titlecase | replace:'Id':' ' }} #{{idx+1}}</small>
                                }
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
                    @for (property of subProperties(); track $index;) {
                        <div class="property">             
                            <div class="property-label text-muted text-sm">
                                {{ property.label | titlecase | replace:'Ids':' ' | replace:'Id':' '}}
                            </div>
                            <pop-drawer-properties [data]="property.value" [label]='property.label'/>
                        </div>
                    }
                </div> 
            }
            @default {
                <div>{{ data() }}</div>
            }
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

    // Input values
    public data = input.required<any>();
    public label = input<string>();

    // Services injected
    readonly #typeCheckService = inject(TypeCheckService);

    // Dynamically determine the type of data variable 
    public dataType  = computed((): string => {
        if (this.#typeCheckService.isArray(this.data())) {
            return this.data().length > 0 ? 'Array' : 'null';
        } else if (this.#typeCheckService.isObject(this.data())) {
            if (this.#typeCheckService.isCodeableConcept(this.data())){
                return 'CodedConcept';
            } else if (this.#typeCheckService.isBoolean(this.data())) {
                return 'boolean';                
            }else if (this.#typeCheckService.isMeasure(this.data())) {
                return 'Measure';                
            } else if (this.#typeCheckService.isRange(this.data())) {
                return 'Range';  
            } else if (this.#typeCheckService.isPeriod(this.data())) {
                return 'Period';               
            } else {
                return 'object';             
            }                    
        } else if (this.#typeCheckService.isUUID(this.data())) {
            return 'UUID';    
        } else if (this.#typeCheckService.isDate(this.data()) || this.#typeCheckService.isDateString(this.data())) {
            return 'Date';                                
        } else {
            return `${typeof(this.data())}`;
        }
    });
    // Dynamically determine any properties the data might habe, if any
    public subProperties = computed((): any[] => {
        if (this.dataType() === 'object') {
            return Object.entries(this.data()).map(
                (pair) => {
                    let key = pair[0]
                    let value = pair[1] 
                    if (value===null || value===undefined || ['caseId', 'createdBy', 'updatedBy', 'id', 'createdAt', 'updatedAt', 'description', 'externalSource', 'externalSourceId','anonymized'].includes(key)) {
                        return null
                    }
                    if (this.#typeCheckService.isArray(value) && value.length==0) {
                        return null
                    }
                    return {
                        label: key.replace(/([a-z])([A-Z])/g, "$1 $2"),
                        value: value
                    }
                }
            ).filter(property => property !== null)     
        } else {
            return []
        }

    });

}