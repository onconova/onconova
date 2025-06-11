from typing import List

from django.db.models import Q, Value, Case, When, F, Func, IntegerField, CharField
from django.db.models.functions import StrIndex, Cast, Length
from django.db.models.expressions import RawSQL

from ninja import Field, Schema, Query
from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route
 
from pop.core.schemas import Paginated, CodedConcept as CodedConceptSchema
from pop.core.auth.token import XSessionTokenAuth
from pop.terminology import models as terminologies


class TerminologyFilters(Schema):
    search_term: str = Field(None, alias='query')
    codes: List[str] = Field(None, alias='codes') # type: ignore

def get_matching_score_expression(query, score): 
    return Case(
        When(query, then=Value(score)),
        default=Value(0),
        output_field=IntegerField(),
    )


@api_controller(
    "/terminologies", 
    auth=[XSessionTokenAuth()], 
    tags=["Terminology"]
)
class TerminologyController(ControllerBase):
    @route.get(
        path='/{terminologyName}/concepts', 
        response={
            200: Paginated[CodedConceptSchema],
            401: None, 403: None,
        },
        operation_id='getTerminologyConcepts',
    )
    @paginate()
    def get_terminology_concepts(self, terminologyName: str, query: Query[TerminologyFilters]):
        queryset = getattr(terminologies, terminologyName).objects.all()
        if query.search_term: 
            # Prepare the search term
            search_term = query.search_term.strip()
            # Query matching criteria
            match_code = Q(code__icontains=search_term)
            match_display = Q(display__icontains=search_term)
            match_synonyms = Q(synonym_match=True)
            # Prepare the filtered queryset
            queryset = queryset.annotate(
                # Aggreagate the matching of the search term against all synonyms in the array
                synonym_match=RawSQL(
                    """
                    EXISTS (
                        SELECT 1
                        FROM unnest(synonyms) AS synonym
                        WHERE synonym ILIKE %s
                    )
                    """,
                    params=[f"%{search_term}%"]
                )
            ).filter( 
                match_code | match_display | match_synonyms
            ).distinct().annotate(
                matching_score = (
                    get_matching_score_expression(match_code, 10) +
                    get_matching_score_expression(match_display, 5) +
                    get_matching_score_expression(match_synonyms, 1) -
                    Cast(StrIndex('display', Value(search_term)), IntegerField()) -
                    Cast(Length('display'), IntegerField())
                ),
            ).order_by('-matching_score')

        if query.codes:
            queryset = queryset.filter(code__in=query.codes).distinct()
        return queryset

