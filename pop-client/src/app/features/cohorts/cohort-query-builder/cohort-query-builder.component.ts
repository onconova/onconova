import { Component, Input, ViewEncapsulation, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ConceptSelectorComponent, DatePickerComponent, RangeInputComponent } from '../../../shared/components';
import { forwardRef } from '@angular/core';

import { 
    CohortsService,
    CohortQueryFilter,
 } from 'src/app/shared/openapi';

 import { TooltipModule } from 'primeng/tooltip';
import { Button } from 'primeng/button';
import { ButtonGroup } from 'primeng/buttongroup';
import { RadioButton } from 'primeng/radiobutton';
import { SelectButton } from 'primeng/selectbutton';
import { Select } from 'primeng/select';
import { MultiSelect } from 'primeng/multiselect';
import { InputNumber } from 'primeng/inputnumber';
import { InputText } from 'primeng/inputtext';


import OpenAPISpecification from "../../../../../openapi.json";
import { DataResource } from "src/app/shared/openapi";
import { NgxAngularQueryBuilderModule, QueryBuilderConfig, Field as FieldBase, Entity, EntityMap, FieldMap } from "ngx-angular-query-builder";

import { Pipe, PipeTransform } from '@angular/core';
import { map, ObjectUnsubscribedError } from 'rxjs';
import { MeasureInputComponent } from "../../../shared/components/measure-input/measure-input.component";
import { Avatar } from 'primeng/avatar';

type Field = FieldBase & {
    description: string;
  }

@Pipe({
    standalone: true,
    name: 'mapOperators'
})
export class MapOperatorsPipe implements PipeTransform {
  transform(value: string[]): {name: string, value: string}[] {
    return value.map( (operator: string) => {
        return {name: mapOperator(operator), value: operator}
    });
  }
}

@Pipe({
    standalone: true,
    name: 'filterByEntity'
})
export class filterByEntityPipe implements PipeTransform {
  transform(value: any[], entity: string): any[]{
    return value.filter( (field: any) => field.entity === entity);
  }
}

@Pipe({
    standalone: true,
    name: 'getDescription'
})
export class getDescriptionPipe implements PipeTransform {
  transform(value: any[], fields: any[]): string {
    return fields.find(f => f.value == value)?.description
  }
}

@Component({
    standalone: true,
    selector: 'pop-cohort-query-builder',
    templateUrl: './cohort-query-builder.component.html',
    styleUrl: './cohort-query-builder.component.css',
    encapsulation: ViewEncapsulation.None,  
    providers: [
      {
        provide: NG_VALUE_ACCESSOR,
        useExisting: forwardRef(() => CohortQueryBuilderComponent),
        multi: true,
      },
    ],
    imports: [
    CommonModule,
    FormsModule,
    NgxAngularQueryBuilderModule,
    Button,
    ButtonGroup,
    SelectButton,
    InputNumber,
    InputText,
    Avatar,
    Select,
    MultiSelect,
    TooltipModule,
    RangeInputComponent,
    ConceptSelectorComponent,
    DatePickerComponent,
    MapOperatorsPipe,
    filterByEntityPipe,
    getDescriptionPipe,
    MeasureInputComponent
]
})
export class CohortQueryBuilderComponent implements ControlValueAccessor {

    @Input() disabled: boolean = false;

    private cohortsService = inject(CohortsService);
    public formControl: FormControl = new FormControl();
    
    public readonly rulesetConditions = [
        {value: 'and', label: 'AND'},
        {value: 'or', label: 'OR'},
    ]
    public readonly booleanOptions = [
        {value: true, label: 'Yes'},
        {value: false, label: 'No'},
    ]
    public selectedCodedConcept = null; 
    public query = {rules: []};

    public operators = CohortQueryFilter 
    private entities = [
        DataResource.PatientCase, DataResource.NeoplasticEntity, DataResource.TnmStaging, DataResource.FigoStaging,
        DataResource.BinetStaging, DataResource.RaiStaging, DataResource.BreslowDepth, DataResource.ClarkStaging,
        DataResource.IssStaging, DataResource.RissStaging, DataResource.GleasonGrade, DataResource.InssStage,
        DataResource.InrgssStage, DataResource.WilmsStage, DataResource.RhabdomyosarcomaClinicalGroup, DataResource.LymphomaStaging,
        DataResource.TumorMarker, DataResource.RiskAssessment, DataResource.TreatmentResponse, DataResource.TherapyLine,
        DataResource.SystemicTherapy, DataResource.PerformanceStatus, DataResource.Surgery, DataResource.Radiotherapy,
        DataResource.Lifestyle, DataResource.ComorbiditiesAssessment,  DataResource.FamilyHistory, DataResource.MolecularTumorBoard,
        DataResource.UnspecifiedTumorBoard, DataResource.AdverseEvent, DataResource.Vitals, DataResource.GenomicVariant,
        DataResource.TumorMutationalBurden, DataResource.MicrosatelliteInstability, DataResource.LossOfHeterozygosity,
        DataResource.HomologousRecombinationDeficiency,  DataResource.TumorNeoantigenBurden, DataResource.AneuploidScore
    ];    

    public config: QueryBuilderConfig = {
        allowEmptyRulesets: false,
        entities: this.entities.reduce(
            (entityMap: any, resource: DataResource) => {
                entityMap[resource] = {value: resource, name: resource.replace(/([a-z])([A-Z])/g, '$1 $2')}
                return entityMap
            }, {} as EntityMap
        ),
        fields: this.entities.flatMap(entity => this.getEntityFields(entity)).reduce(
            (fieldsMap: any, field: Field) => {                
                fieldsMap[field.value as string] = field
                return fieldsMap
            }, {} as FieldMap
        ),
    } 

    getEntityFields(entity: DataResource): Field[] {
        const ignoredFields: string[] = ['description', 'caseId', 'id','createdAt','updatedAt', 'createdBy', 'updatedBy', 'externalSourceId']
        // Get the schema definition of the entity from the OpenAPISpecification object
        const schemas = OpenAPISpecification.components.schemas
        // Get a list of all fields/properties in that schema
        const properties = schemas[entity].properties || {};
        // Iterate over each property
        return Object.entries(properties).filter(
            ([propertyKey,_]) => !ignoredFields.includes(propertyKey)
        ).flatMap(
            ([propertyKey,property]): Field | Field[] => {
                let title: string = property.title; 
                let description: string = property.description; 
                
                let isArray: boolean = false;
                const nullable = property.anyOf && property.anyOf[property.anyOf.length-1].type === 'null'
                if (nullable) {
                    property = property.anyOf[0];
                } else if (property.items) {
                    property = property.items;                    
                    isArray = true;
                } else {
                    property = property;
                }
                let propertyType: string;
                if (property.type === undefined && property.$ref) {
                    propertyType = property.$ref.split('/').pop();
                } else {
                    propertyType = property.type;
                }        
                
                // Handle nested resources
                if ([
                    DataResource.SystemicTherapyMedication,
                    DataResource.RadiotherapyDosage,
                    DataResource.RadiotherapySetting,
                    DataResource.AdverseEventMitigation,
                    DataResource.AdverseEventSuspectedCause,
                    DataResource.MolecularTherapeuticRecommendation,

                ].includes(propertyType as DataResource)) {
                    return this.getEntityFields(propertyType as DataResource).map((nested_field: Field) => ({
                        name: `${property.title} - ${nested_field.name}`,
                        entity: entity,
                        value: `${entity}.${propertyKey}.${nested_field.value?.split('.').pop()}`,
                        options: nested_field.options,
                        type: nested_field.type,
                        operators: nested_field.operators,
                        description: nested_field.description,
                    }))
                }

                // Determine any selection options if the property has an enumeration
                // @ts-ignore
                let propertyEnum = property.enum || schemas[propertyType]?.enum;
                let options: any[] = [];
                if (propertyEnum) {
                    options = propertyEnum.map((option: any) => ({ value: option, label: option }));
                    propertyType = 'enum';
                }
                if (propertyType == 'string' && property.format) {
                    propertyType = property.format
                }
                if (propertyType == 'CodedConcept') {
                    options = [{value: property['x-terminology']}];
                }
                if (propertyType == 'Measure') {
                    options = [
                        {value: property['x-measure']},
                        {value: property['x-default-unit']}
                    ];
                }
                propertyType = (isArray ? "Multi" : "") + propertyType;

                // Create a field object and add it to the array
                return {
                    name: title,
                    entity: entity,
                    value: `${entity}.${propertyKey}`,
                    options: options,
                    type: propertyType,
                    operators: this.getTypeFilterOperators(propertyType),
                    description: description,
                }
        }) as Field[];
    }

    getCodesFromEvent(event: any) {
        if (event){
            return event?.code ? event.code : event.map((item: any) => item.code)
        }
        return null
    }

    // Emit the updated query value when it changes in the query-builder
    onQueryChange(updatedQuery: any) {
        if ( updatedQuery?.rules && updatedQuery.rules.length){
            let value = {...updatedQuery}
            value.rules = this.convertRule(value.rules, false)
            this.formControl.patchValue(value);
        } else {
            this.formControl.patchValue(null);
        }
    }

    writeValue(value: any): void {
        this.query = {...value};
        if (this.query?.rules) {
            this.query.rules = this.convertRule(this.query.rules, true);
        }
        this.formControl.patchValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }

    private convertRule(rules: any, toInternal: boolean = true) {
        return rules.map((rule_: any) => {
            let rule = {...rule_};
            if (rule.field) {
                if (toInternal) {
                    rule.field = `${rule.entity}.${rule.field}`
                } else {
                    rule.field = rule.field.split('.').pop();
                }
            }
            // Recursively apply to nested rules
            if (rule.rules && rule.rules.length > 0) {
                rule.rules = this.convertRule(rule.rules, toInternal);
            }
            return rule
        });
      }

    private getTypeFilterOperators(type: string): CohortQueryFilter[]  {
        switch (type) {
            case 'string':
                return [ 
                    CohortQueryFilter.ExactStringFilter,
                    CohortQueryFilter.NotExactStringFilter,
                    CohortQueryFilter.ContainsStringFilter, 
                    CohortQueryFilter.NotContainsStringFilter, 
                    CohortQueryFilter.BeginsWithStringFilter, 
                    CohortQueryFilter.NotBeginsWithStringFilter, 
                    CohortQueryFilter.EndsWithStringFilter, 
                    CohortQueryFilter.NotEndsWithStringFilter
                ]
            case 'enum':
                return [ 
                    CohortQueryFilter.EqualsEnumFilter,
                    CohortQueryFilter.NotEqualsEnumFilter,
                    CohortQueryFilter.AnyOfEnumFilter,
                    CohortQueryFilter.NotAnyOfEnumFilter,    
                ]
            case 'number':
                return [ 
                    CohortQueryFilter.EqualFloatFilter,
                    CohortQueryFilter.NotEqualFloatFilter,
                    CohortQueryFilter.LessThanFloatFilter,
                    CohortQueryFilter.LessThanOrEqualFloatFilter,
                    CohortQueryFilter.GreaterThanFloatFilter,
                    CohortQueryFilter.GreaterThanOrEqualFloatFilter,
                    CohortQueryFilter.BetweenFloatFilter,
                    CohortQueryFilter.NotBetweenFloatFilter
                ]
            case 'integer':
                return [ 
                    CohortQueryFilter.EqualIntegerFilter,
                    CohortQueryFilter.NotEqualIntegerFilter,
                    CohortQueryFilter.LessThanIntegerFilter,
                    CohortQueryFilter.LessThanOrEqualIntegerFilter,
                    CohortQueryFilter.GreaterThanIntegerFilter,
                    CohortQueryFilter.GreaterThanOrEqualIntegerFilter,
                    CohortQueryFilter.BetweenIntegerFilter,
                    CohortQueryFilter.NotBetweenIntegerFilter
                ]
            case 'date-time':
                return [ 
                    CohortQueryFilter.BeforeDateFilter,
                    CohortQueryFilter.AfterDateFilter,
                    CohortQueryFilter.OnOrBeforeDateFilter,
                    CohortQueryFilter.OnOrAfterDateFilter,
                    CohortQueryFilter.OnDateFilter,
                    CohortQueryFilter.NotOnDateFilter,
                ]
            case 'date':
                return [ 
                    CohortQueryFilter.BeforeDateFilter,
                    CohortQueryFilter.AfterDateFilter,
                    CohortQueryFilter.OnOrBeforeDateFilter,
                    CohortQueryFilter.OnOrAfterDateFilter,
                    CohortQueryFilter.OnDateFilter,
                    CohortQueryFilter.NotOnDateFilter,
                ]
            case 'Period':
                return [ 
                    CohortQueryFilter.OverlapsPeriodFilter,
                    CohortQueryFilter.NotOverlapsPeriodFilter,
                    CohortQueryFilter.ContainsPeriodFilter,
                    CohortQueryFilter.NotContainsPeriodFilter,
                    CohortQueryFilter.ContainedByPeriodFilter,
                    CohortQueryFilter.NotContainedByPeriodFilter
                ]
            case 'CodedConcept':
                return [ 
                    CohortQueryFilter.EqualsConceptFilter,
                    CohortQueryFilter.NotEqualsConceptFilter,
                    CohortQueryFilter.AnyOfConceptFilter,
                    CohortQueryFilter.NotAnyOfConceptFilter,
                    CohortQueryFilter.DescendantsOfConceptFilter
                ]
            case 'Measure':
                return [ 
                    CohortQueryFilter.EqualFloatFilter,
                    CohortQueryFilter.NotEqualFloatFilter,
                    CohortQueryFilter.LessThanFloatFilter,
                    CohortQueryFilter.LessThanOrEqualFloatFilter,
                    CohortQueryFilter.GreaterThanFloatFilter,
                    CohortQueryFilter.GreaterThanOrEqualFloatFilter,
                    CohortQueryFilter.BetweenFloatFilter,
                    CohortQueryFilter.NotBetweenFloatFilter
                ]
            case 'MultiCodedConcept':
                return [ 
                    CohortQueryFilter.AllOfConceptFilter,
                    CohortQueryFilter.NotAllOfConceptFilter,
                    CohortQueryFilter.NotEqualsConceptFilter,
                    CohortQueryFilter.AnyOfConceptFilter,
                    CohortQueryFilter.NotAnyOfConceptFilter,
                    CohortQueryFilter.DescendantsOfConceptFilter
                ]
            default:
                return []
        }
    }

}


function mapOperator(operator: string): string {
    switch (operator) {
        case CohortQueryFilter.ExactStringFilter:
            return 'Matches exactly'
        case CohortQueryFilter.NotExactStringFilter:
            return 'Does not match exactly'
        case CohortQueryFilter.ContainsStringFilter: 
            return 'Contains'
        case CohortQueryFilter.NotContainsStringFilter: 
            return 'Does not contain'
        case CohortQueryFilter.BeginsWithStringFilter: 
            return 'Begins with'
        case CohortQueryFilter.NotBeginsWithStringFilter: 
            return 'Does not begin with'
        case CohortQueryFilter.EndsWithStringFilter: 
            return 'Ends with'
        case CohortQueryFilter.NotEndsWithStringFilter: 
            return 'Does not end with'
        case CohortQueryFilter.BeforeDateFilter:
            return 'Before';
        case CohortQueryFilter.AfterDateFilter:
            return 'After';
        case CohortQueryFilter.OnOrBeforeDateFilter:
            return 'On or before';
        case CohortQueryFilter.OnOrAfterDateFilter:
            return 'On or after';
        case CohortQueryFilter.OnDateFilter:
            return 'On date';
        case CohortQueryFilter.NotOnDateFilter:
            return 'Not on';
        case CohortQueryFilter.BetweenDatesFilter:
            return 'Between';
        case CohortQueryFilter.NotBetweenDatesFilter:
            return 'Not between';
        case CohortQueryFilter.OverlapsPeriodFilter:
            return 'Overlaps with';
        case CohortQueryFilter.NotOverlapsPeriodFilter:
            return 'Does not overlap with';
        case CohortQueryFilter.ContainsPeriodFilter:
            return 'Contains folowing period';
        case CohortQueryFilter.NotContainsPeriodFilter:
            return 'Does not contain following period';
        case CohortQueryFilter.ContainedByPeriodFilter:
            return 'Contained by following period';
        case CohortQueryFilter.NotContainedByPeriodFilter:
            return 'Not contained by following period';
        case CohortQueryFilter.LessThanIntegerFilter:
            return 'Less than'
        case CohortQueryFilter.LessThanOrEqualIntegerFilter:
            return 'Less than or equal'
        case CohortQueryFilter.GreaterThanIntegerFilter:
            return 'Greater than'
        case CohortQueryFilter.GreaterThanOrEqualIntegerFilter:
            return 'Greater than or equal'
        case CohortQueryFilter.EqualIntegerFilter:
            return 'Equals'
        case CohortQueryFilter.NotEqualIntegerFilter:
            return 'Not equal'
        case CohortQueryFilter.BetweenIntegerFilter:
            return 'Between'
        case CohortQueryFilter.NotBetweenIntegerFilter:
            return 'Not between'
        case CohortQueryFilter.LessThanFloatFilter:
            return 'Less than'
        case CohortQueryFilter.LessThanOrEqualFloatFilter:
            return 'Less than or equal'
        case CohortQueryFilter.GreaterThanFloatFilter:
            return 'Greater than'
        case CohortQueryFilter.GreaterThanOrEqualFloatFilter:
            return 'Greater than or equal'
        case CohortQueryFilter.EqualFloatFilter:
            return 'Equals'
        case CohortQueryFilter.NotEqualFloatFilter:
            return 'Not equal'
        case CohortQueryFilter.BetweenFloatFilter:
            return 'Between'
        case CohortQueryFilter.NotBetweenFloatFilter:
            return 'Not between'
        case CohortQueryFilter.EqualsBooleanFilter:
            return 'Is';
        case CohortQueryFilter.EqualsConceptFilter:
            return 'Is';
        case CohortQueryFilter.NotEqualsConceptFilter:
            return 'Is not';
        case CohortQueryFilter.AllOfConceptFilter:
            return 'Is exactly';
        case CohortQueryFilter.NotAllOfConceptFilter:
            return 'Is exactly not';
        case CohortQueryFilter.AnyOfConceptFilter:
            return 'Is any of';
        case CohortQueryFilter.NotAnyOfConceptFilter:
            return 'Is not any of';
        case CohortQueryFilter.DescendantsOfConceptFilter:
            return 'Is any descendant of';
        case CohortQueryFilter.ExactRefereceFilter:
            return 'Exact reference';
        case CohortQueryFilter.NotExactRefereceFilter:
            return 'Not exact reference';
        case CohortQueryFilter.EqualsEnumFilter:
            return 'Is';
        case CohortQueryFilter.NotEqualsEnumFilter:
            return 'Is not';
        case CohortQueryFilter.AnyOfEnumFilter:
            return 'Is any of';
        case CohortQueryFilter.NotAnyOfEnumFilter:
            return 'Is not any of';
        case CohortQueryFilter.IsNullFilter:
            return 'Is empty (unset)';
        case CohortQueryFilter.NotIsNullFilter:
            return 'Is not empty (unset)';
        default:
            return operator;
    }
}
