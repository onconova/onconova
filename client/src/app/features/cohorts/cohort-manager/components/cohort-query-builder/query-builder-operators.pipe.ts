import { Pipe, PipeTransform } from "@angular/core";
import { CohortQueryFilter } from "onconova-api-client";

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
            return 'Is before';
        case CohortQueryFilter.AfterDateFilter:
            return 'Is after';
        case CohortQueryFilter.OnOrBeforeDateFilter:
            return 'On or before';
        case CohortQueryFilter.OnOrAfterDateFilter:
            return 'On or after';
        case CohortQueryFilter.OnDateFilter:
            return 'Is';
        case CohortQueryFilter.NotOnDateFilter:
            return 'Is not';
        case CohortQueryFilter.BetweenDatesFilter:
            return 'Is between';
        case CohortQueryFilter.NotBetweenDatesFilter:
            return 'Is not between';
        case CohortQueryFilter.OverlapsPeriodFilter:
            return 'Overlaps with';
        case CohortQueryFilter.NotOverlapsPeriodFilter:
            return 'Does not overlap with';
        case CohortQueryFilter.ContainsPeriodFilter:
            return 'Contains';
        case CohortQueryFilter.NotContainsPeriodFilter:
            return 'Does not contain';
        case CohortQueryFilter.ContainedByPeriodFilter:
            return 'Is contained by';
        case CohortQueryFilter.NotContainedByPeriodFilter:
            return 'Is not contained by';
        case CohortQueryFilter.OverlapsRangeFilter:
            return 'Overlaps with';
        case CohortQueryFilter.NotOverlapsRangeFilter:
            return 'Does not overlap with';
        case CohortQueryFilter.ContainsRangeFilter:
            return 'Contains';
        case CohortQueryFilter.NotContainsRangeFilter:
            return 'Does not contain';
        case CohortQueryFilter.ContainedByRangeFilter:
            return 'Is contained by';
        case CohortQueryFilter.NotContainedByRangeFilter:
            return 'Is not contained by';
        case CohortQueryFilter.LessThanIntegerFilter:
            return 'Is less than'
        case CohortQueryFilter.LessThanOrEqualIntegerFilter:
            return 'Is less than or equal'
        case CohortQueryFilter.GreaterThanIntegerFilter:
            return 'Is greater than'
        case CohortQueryFilter.GreaterThanOrEqualIntegerFilter:
            return 'Is greater than or equal'
        case CohortQueryFilter.EqualIntegerFilter:
            return 'Is equal to'
        case CohortQueryFilter.NotEqualIntegerFilter:
            return 'Is not equal to'
        case CohortQueryFilter.BetweenIntegerFilter:
            return 'Is between'
        case CohortQueryFilter.NotBetweenIntegerFilter:
            return 'Is not between'
        case CohortQueryFilter.LessThanFloatFilter:
            return 'Is less than'
        case CohortQueryFilter.LessThanOrEqualFloatFilter:
            return 'Is less than or equal'
        case CohortQueryFilter.GreaterThanFloatFilter:
            return 'Is greater than'
        case CohortQueryFilter.GreaterThanOrEqualFloatFilter:
            return 'Is greater than or equal'
        case CohortQueryFilter.EqualFloatFilter:
            return 'Is equal to'
        case CohortQueryFilter.NotEqualFloatFilter:
            return 'Is not equal to '
        case CohortQueryFilter.BetweenFloatFilter:
            return 'Is between'
        case CohortQueryFilter.NotBetweenFloatFilter:
            return 'Is not between'
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
            return 'Is exact reference';
        case CohortQueryFilter.NotExactRefereceFilter:
            return 'Is not exact reference';
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
