
from django.db.models import Q
from typing import Iterator
from pop.oncology import models as oncological_models
from pop.core import filters as filters
from pop.analytics.schemas import CohortFilterRuleset, CohortFilterRule, RulesetCondition


def convert_rule_into_query(rule: CohortFilterRule) -> Q:
    model = getattr(oncological_models, rule.entity, None)
    if not model:
        raise KeyError(f"The model entity '{rule.entity}' specified by the rule does not exist.")
    filter = getattr(filters, rule.operator, None)
    if not filter:
        raise KeyError(f"The filter '{rule.operator}' specified by the rule does not exist.")
    field = rule.field.split('.')[1]
    if model is oncological_models.PatientCase:
        return filter.get_query(field, rule.value)
    else:
        subquery = filter.get_query(field, rule.value)
        subqueryset = model.objects.filter(subquery)
        related_name = model._meta.get_field('case')._related_name
        return Q(**{f"{related_name}__in": subqueryset})

def build_query(data: CohortFilterRuleset | CohortFilterRule) -> Iterator[Q]:
    if isinstance(data, CohortFilterRule):
        yield convert_rule_into_query(data)

    elif isinstance(data, CohortFilterRuleset):
        query = Q()
        for rule in data.rules:
            # Get next() result from generator above
            # (bc recursive yields) and process logic:
            for rule_instance in build_query(rule):
                if data.condition == RulesetCondition.AND:
                    query = rule_instance & query
                if data.condition == RulesetCondition.OR:
                    query = rule_instance | query
        # Yield the completed, compiled logic for this branch of query back up the pipe:
        yield query