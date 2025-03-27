import { Component, Input, SimpleChanges, ViewEncapsulation  } from '@angular/core';

import { CodedConcept, Measure, Period } from 'src/app/shared/openapi';
import { CommonModule } from '@angular/common';
import { CodedConceptTreeComponent } from './coded-concept-tree.component';
import { ReplacePipe } from 'src/app/shared/pipes/replace.pipe';

@Component({
    standalone: true,
    selector: 'pop-drawer-properties',
    template: `
        <ng-container [ngSwitch]="dataType">
            <div *ngSwitchCase="'null'" class="text-muted">-</div> 
            <div *ngSwitchCase="'Period'">{{ data.start | date }} - {{ data.end | date }}</div>
            <div *ngSwitchCase="'Measure'">{{ data.value }} {{ data.unit | replace:'__':'/' }}</div>
            <div *ngSwitchCase="'Date'">{{ data | date }}</div>
            <div *ngSwitchCase="'CodedConcept'"><pop-coded-concept-tree [concept]="data"/></div>
            <div *ngSwitchCase="'Array'">
                <ul class="list-property">
                    <li *ngFor="let item of data">
                        <pop-drawer-properties [data]="item"/>
                    </li>
                </ul>
            </div>
            <div *ngSwitchCase="'object'">
                <ng-container *ngFor="let property of subProperties">
                    <div class="property">             
                        <small class="property-label {{ data ? '' : 'text-muted'}}">
                            {{ property.label | titlecase }}
                        </small>
                        <pop-drawer-properties [data]="property.value"/>
                    </div>
                </ng-container>
            </div>
            <div *ngSwitchDefault>{{ data }}</div>
        </ng-container>
    `,
    styles: `
        ul.list-property {
            padding-left: 1rem !important;
        }
        ul.list-property > li {
            padding-left: .5rem !important;
            border-left: solid 2px var(--p-text-muted-color) !important;
            list-style: none;
        }
    `,
    encapsulation: ViewEncapsulation.None,
    imports: [CommonModule, CodedConceptTreeComponent, ReplacePipe]
})
export class DrawerDataPropertiesComponent {

    @Input({required: true}) data!: any;
    public dataType!: string;
    public subProperties: any[] = [];

    private readonly isCodeableConcept = (value: CodedConcept): value is CodedConcept => !!value?.code;
    private readonly isPeriod = (value: Period): value is Period => !!value?.start;
    private readonly isMeasure = (value: Measure): value is Measure => !!value?.value;
    private readonly isObject = (x: any) => typeof x === 'object' && !Array.isArray(x) && x !== null
    private readonly isArray = (x: any) => x instanceof Array
    private readonly isDateString = (value: any): boolean => typeof value === 'string' && !isNaN(Date.parse(value));
    private readonly isDate = (value: any): value is Date => Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime());

    ngOnChanges(changes: SimpleChanges) {
        if (changes['data'] && this.data) {
            this.processData();
        }
    }
    
    processData(){
        if (this.isArray(this.data)) {
            this.dataType = this.data.length > 0 ? 'Array' : 'null';
        } else if (this.isObject(this.data)) {
            if (this.isCodeableConcept(this.data)){
                this.dataType = 'CodedConcept';
            } else if (this.isPeriod(this.data)) {
                this.dataType = 'Period';                
            } else if (this.isMeasure(this.data)) {
                this.dataType = 'Measure';                
            } else if (this.isPeriod(this.data)) {
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
                        if (this.isArray(value) && value.length==0) {
                            return null
                        }
                        return {
                            label: key.replace(/([A-Z])/g, " $1"),
                            value: value
                        }
                    }
                ).filter(property => property !== null)             
            }      
        } else if (this.isDate(this.data) || this.isDateString(this.data)) {
            this.dataType = 'Date';                                
        } else {
            this.dataType = `${typeof(this.data)}`;
        }
    }
}