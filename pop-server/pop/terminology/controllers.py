from typing import List

from django.db.models import Q

from ninja import Field, Schema, Query
from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route
 
from pop.core.schemas import Paginated, CodedConceptSchema
from pop.terminology import models as terminologies


class QueryParameters(Schema):
    query_string: str = Field(None, alias='query')
    codes: List[str] = Field(None, alias='codes') # type: ignore


@api_controller(
    "/terminologies", 
    # auth=[JWTAuth()], 
    tags=["Terminology"]
)
class TerminologyController(ControllerBase):
    @route.get(
        path='/{terminologyName}/concepts', 
        response={
            200: Paginated[CodedConceptSchema]
        },
        operation_id='getTerminologyConcepts',
    )
    @paginate()
    def get_terminology_concepts(self, terminologyName: str, query: Query[QueryParameters]):
        queryset = getattr(terminologies, terminologyName).objects.all()
        if query.query_string: 
            queryset = queryset.filter(
                Q(code__icontains=query.query_string) | Q(display__icontains=query.query_string) | Q(synonyms__contains=[query.query_string])
            ).distinct()
        if query.codes:
            queryset = queryset.filter(code__in=query.codes).distinct()
        return queryset

