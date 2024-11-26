from typing import List

from ninja_extra import route, api_controller
from ninja_jwt import schema

from ninja_extra import (
    api_controller, 
    ControllerBase, 
    permissions, 
    route,
)
 
from pop.core.schemas.fields import CodedConceptSchema
from pop.terminology import models as terminologies

@api_controller("/terminologies", tags=["Terminology"])
class TerminologyController(ControllerBase):
    @route.get(
        path='/{terminology}/concepts', 
        response={
            200: List[CodedConceptSchema]
        },
        operation_id='getTerminologyConcepts',
    )
    def get_terminology_concepts(self, terminology: str):
        return getattr(terminologies, terminology).objects.all()

