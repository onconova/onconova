from typing import List

from django.db.models import Q

from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra import api_controller, ControllerBase, route
 
from pop.core.schemas.fields import CodedConceptSchema
from pop.terminology import models as terminologies

@api_controller(
    "/terminologies", 
    auth=[JWTAuth()], 
    tags=["Terminology"]
)
class TerminologyController(ControllerBase):
    @route.get(
        path='/{terminologyName}/concepts', 
        response={
            200: List[CodedConceptSchema]
        },
        operation_id='getTerminologyConcepts',
    )
    def get_terminology_concepts(self, terminologyName: str, query: str = None):
        queryset = getattr(terminologies, terminologyName).objects.all()
        if query: 
            queryset = queryset.filter(
                Q(code__icontains=query) | Q(display__icontains=query) | Q(synonyms__contains=[query])
            ).distinct()
        return queryset

