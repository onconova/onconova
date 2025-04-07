import { Pipe, PipeTransform } from "@angular/core";
import { CohortQueryFilter } from "src/app/shared/openapi";

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

@Pipe({
    standalone: true,
    name: 'mapOperators'
})
export class MapOperatorsPipe implements PipeTransform {
  transform(value: string[] | undefined): {name: string, value: string}[] {
    if (!value) {
        return [];
    }
    return value.map( (operator: string) => {
        return {name: mapOperator(operator), value: operator}
    });
  }
}
