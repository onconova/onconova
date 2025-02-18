import { NgModule, Component, Input, ViewEncapsulation, OnInit, inject, DestroyRef,ChangeDetectionStrategy, EventEmitter, Output, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ConceptSelectorComponent } from '../../shared/components';
import { DatePickerComponent } from '../../shared/components';
import { forwardRef } from '@angular/core';

import { 
    CohortsService,
    CohortBuilderEntity,
    CohortQueryFilter,
    CohortRuleType,
 } from 'src/app/shared/openapi';

import { Button } from 'primeng/button';
import { ButtonGroup } from 'primeng/buttongroup';
import { RadioButton } from 'primeng/radiobutton';
import { SelectButton } from 'primeng/selectbutton';
import { Select } from 'primeng/select';
import { MultiSelect } from 'primeng/multiselect';
import { InputNumber } from 'primeng/inputnumber';
import { InputText } from 'primeng/inputtext';

import { NgxAngularQueryBuilderModule, RuleSet, Field } from "ngx-angular-query-builder";

import { Pipe, PipeTransform } from '@angular/core';

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
        RadioButton,
        SelectButton,
        InputNumber,
        InputText,
        Select,
        MultiSelect,
        ConceptSelectorComponent,
        DatePickerComponent,
        MapOperatorsPipe,        
        filterByEntityPipe,
    ]
})
export class CohortQueryBuilderComponent implements ControlValueAccessor {

    @Input() disabled: boolean = false;

    private cohortsService = inject(CohortsService);
    public formControl: FormControl = new FormControl();

    public readonly CohortRuleType = CohortRuleType;
    
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

    config$ = this.cohortsService.getCohortBuilderConfig();

    getCodesFromEvent(event: any) {
        if (event){
            return event?.code ? event.code : event.map((item: any) => item.code)
        }
        return null
    }

    // Emit the updated query value when it changes in the query-builder
    onQueryChange(updatedQuery: any) {
        if ( updatedQuery.rules.length > 0){
            this.formControl.patchValue(updatedQuery);
        } else {
            this.formControl.patchValue(null);
        }
    }

    writeValue(value: any): void {
        this.query = value
        this.formControl.patchValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }

}