import dataclasses
from typing import List

import pghistory
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate
from pop.core.anonymization import anonymize
from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.history.schemas import HistoryEvent
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema
from pop.core.schemas import Paginated
from pop.core.utils import COMMON_HTTP_ERRORS
from pop.oncology.models import ComorbiditiesAssessment, ComorbiditiesPanel
from pop.oncology.models.comorbidities import (
    ComorbidityPanelCategory as ComorbidityPanelCategoryType,
)
from pop.oncology.schemas import (
    ComorbiditiesAssessmentCreateSchema,
    ComorbiditiesAssessmentFilters,
    ComorbiditiesAssessmentSchema,
    ComorbiditiesPanel,
    ComorbidityPanelCategory,
)
from pop.terminology.models import ICD10Condition


@api_controller(
    "comorbidities-assessments",
    auth=[XSessionTokenAuth()],
    tags=["Comorbidities Assessments"],
)
class ComorbiditiesAssessmentController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[ComorbiditiesAssessmentSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id="getComorbiditiesAssessments",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_comorbidities_assessments_matching_the_query(self, query: Query[ComorbiditiesAssessmentFilters]):  # type: ignore
        queryset = ComorbiditiesAssessment.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createComorbiditiesAssessment",
    )
    def create_comorbidities_assessment(self, payload: ComorbiditiesAssessmentCreateSchema):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{comorbiditiesAssessmentId}",
        response={200: ComorbiditiesAssessmentSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getComorbiditiesAssessmentById",
    )
    @anonymize()
    def get_comorbidities_assessment_by_id(self, comorbiditiesAssessmentId: str):
        return get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)

    @route.delete(
        path="/{comorbiditiesAssessmentId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteComorbiditiesAssessment",
    )
    def delete_comorbidities_assessment(self, comorbiditiesAssessmentId: str):
        instance = get_object_or_404(
            ComorbiditiesAssessment, id=comorbiditiesAssessmentId
        )
        instance.delete()
        return 204, None

    @route.put(
        path="/{comorbiditiesAssessmentId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateComorbiditiesAssessment",
    )
    def update_comorbidities_assessment(self, comorbiditiesAssessmentId: str, payload: ComorbiditiesAssessmentCreateSchema):  # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(
                ComorbiditiesAssessment, id=comorbiditiesAssessmentId
            )
            return ComorbiditiesAssessmentCreateSchema.model_validate(
                payload.model_dump(exclude_unset=True)
            ).model_dump_django(instance=instance)

    @route.get(
        path="/{comorbiditiesAssessmentId}/history/events",
        response={
            200: Paginated[
                HistoryEvent.bind_schema(ComorbiditiesAssessmentCreateSchema)
            ],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllComorbiditiesAssessmentHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_comorbidities_assessment_history_events(
        self, comorbiditiesAssessmentId: str
    ):
        instance = get_object_or_404(
            ComorbiditiesAssessment, id=comorbiditiesAssessmentId
        )
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{comorbiditiesAssessmentId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(ComorbiditiesAssessmentCreateSchema),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getComorbiditiesAssessmentHistoryEventById",
    )
    def get_comorbidities_assessment_history_event_by_id(
        self, comorbiditiesAssessmentId: str, eventId: str
    ):
        instance = get_object_or_404(
            ComorbiditiesAssessment, id=comorbiditiesAssessmentId
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{comorbiditiesAssessmentId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertComorbiditiesAssessmentToHistoryEvent",
    )
    def revert_comorbidities_assessment_to_history_event(
        self, comorbiditiesAssessmentId: str, eventId: str
    ):
        instance = get_object_or_404(
            ComorbiditiesAssessment, id=comorbiditiesAssessmentId
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/meta/panels",
        response={200: List[ComorbiditiesPanel], **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getComorbiditiesPanels",
    )
    def get_all_comorbidities_panels(self):  # type: ignore
        return [
            ComorbiditiesPanel(
                name=name,
                categories=[
                    ComorbidityPanelCategory(
                        label=category.label,
                        conditions=list(
                            ICD10Condition.objects.filter(code__in=category.codes)
                        ),
                    )
                    for category in [
                        category
                        for category in panel.__dict__.values()
                        if isinstance(category, ComorbidityPanelCategoryType)
                    ]
                ],
            )
            for name, panel in ComorbiditiesAssessment.COMORBIDITY_PANELS_DETAILS.items()
        ]

    @route.get(
        path="/meta/panels/{panel}",
        response={200: ComorbiditiesPanel, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getComorbiditiesPanelsByName",
    )
    def get_comorbidities_panel_by_name(self, panel: str):
        panel_details = ComorbiditiesAssessment.COMORBIDITY_PANELS_DETAILS.get(panel)
        if not panel_details:
            return 404
        panel_categories = [
            category
            for category in panel_details.__dict__.values()
            if isinstance(category, ComorbidityPanelCategoryType)
        ]
        return 200, ComorbiditiesPanel(
            name=panel,
            categories=[
                ComorbidityPanelCategory(
                    label=category.label,
                    default=ICD10Condition.objects.filter(
                        code=category.default
                    ).first(),
                    conditions=list(
                        ICD10Condition.objects.filter(code__in=category.codes)
                    ),
                )
                for category in panel_categories
            ],
        )
