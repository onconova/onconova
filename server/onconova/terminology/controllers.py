from typing import List

from django.db.models import Case, CharField, F, Func, IntegerField, Q, Value, When
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast, Length, StrIndex
from ninja import Field, Query, Schema
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.schemas import CodedConcept as CodedConceptSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.terminology import models as terminologies


class TerminologyFilters(Schema):
    """
    Schema for filtering terminology queries.

    Attributes:
        search_term (str | None): Optional search term to filter results. Mapped from the "query" field in input.
        codes (List[str] | None): Optional list of codes to filter results. Mapped from the "codes" field in input.
    """
    search_term: str | None = Field(None, alias="query")
    codes: List[str] | None = Field(None, alias="codes")


def get_matching_score_expression(query: any, score):
    """
    Generates a Django Case expression that assigns a specified score when a condition is met.

    Args:
        query (Any): A Django Q object or condition to evaluate.
        score (int): The score to assign if the condition is true.

    Returns:
        Case (Expression): A Django Case expression that returns `score` when `query` is true, otherwise returns 0.
    """
    return Case(
        When(query, then=Value(score)),
        default=Value(0),
        output_field=IntegerField(),
    )


@api_controller("/terminologies", auth=[XSessionTokenAuth()], tags=["Terminology"])
class TerminologyController(ControllerBase):
    """Api controller for handling terminology-related endpoints."""    
    
    @route.get(
        path="/{terminologyName}/concepts",
        response={200: Paginated[CodedConceptSchema], **COMMON_HTTP_ERRORS},  # type: ignore
        operation_id="getTerminologyConcepts",
    )
    @paginate()
    def get_terminology_concepts(
        self, terminologyName: str, query: Query[TerminologyFilters]
    ):
        """        
        Retrieves terminology concepts from the specified terminology, applying optional filters and search criteria.

        Args:
            terminologyName (str): The name of the terminology to query.
            query (Query[TerminologyFilters]): An object containing filter parameters, including:

                - search_term (str, optional): A term to search for in concept codes, display names, or synonyms.
                - codes (List[str], optional): A list of codes to filter the concepts.

        Returns:
            (QuerySet): A Django QuerySet of filtered and annotated terminology concepts, ordered by matching score if a search term is provided.

        Notes:
            - If a search term is provided, concepts are matched against code, display, and synonyms fields.
            - Matching concepts are annotated with a matching score based on relevance.
            - If codes are provided, the queryset is further filtered to include only those codes.
        """
        queryset = getattr(terminologies, terminologyName).objects.all()
        if query.search_term:
            # Prepare the search term
            search_term = query.search_term.strip()
            # Query matching criteria
            match_code = Q(code__icontains=search_term)
            match_display = Q(display__icontains=search_term)
            match_synonyms = Q(synonym_match=True)
            # Prepare the filtered queryset
            queryset = (
                queryset.annotate(
                    # Aggreagate the matching of the search term against all synonyms in the array
                    synonym_match=RawSQL(
                        """
                    EXISTS (
                        SELECT 1
                        FROM unnest(synonyms) AS synonym
                        WHERE synonym ILIKE %s
                    )
                    """,
                        params=[f"%{search_term}%"],
                    )
                )
                .filter(match_code | match_display | match_synonyms)
                .distinct()
                .annotate(
                    matching_score=(
                        get_matching_score_expression(match_code, 10)
                        + get_matching_score_expression(match_display, 5)
                        + get_matching_score_expression(match_synonyms, 1)
                        - Cast(StrIndex("display", Value(search_term)), IntegerField())
                        - Cast(Length("display"), IntegerField())
                    ),
                )
                .order_by("-matching_score")
            )

        if query.codes:
            queryset = queryset.filter(code__in=query.codes).distinct()
        return queryset
