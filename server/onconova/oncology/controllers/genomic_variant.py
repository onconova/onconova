from typing import List

import pghistory
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja.schema import Field, Schema
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology import (
    models as orm,
    schemas as scm,
)


@api_controller(
    "genomic-variants",
    auth=[XSessionTokenAuth()],
    tags=["Genomic Variants"],
)
class GenomicVariantController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[scm.GenomicVariant],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getGenomicVariants",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_genomic_variants_matching_the_query(self, query: Query[scm.GenomicVariantFilters]):  # type: ignore
        queryset = orm.GenomicVariant.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createGenomicVariant",
    )
    def create_genomic_variant(self, payload: scm.GenomicVariantCreate):  
        return 201, payload.model_dump_django()

    @route.get(
        path="/{genomicVariantId}",
        response={200: scm.GenomicVariant, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getGenomicVariantById",
    )
    @anonymize()
    def get_genomic_variant_by_id(self, genomicVariantId: str):
        return get_object_or_404(orm.GenomicVariant, id=genomicVariantId)

    @route.put(
        path="/{genomicVariantId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateGenomicVariant",
    )
    def update_genomic_variant(self, genomicVariantId: str, payload: scm.GenomicVariantCreate):  
        instance = get_object_or_404(orm.GenomicVariant, id=genomicVariantId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{genomicVariantId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteGenomicVariant",
    )
    def delete_genomic_variant(self, genomicVariantId: str):
        get_object_or_404(orm.GenomicVariant, id=genomicVariantId).delete()
        return 204, None

    @route.get(
        path="/{genomicVariantId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.GenomicVariantCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllGenomicVariantHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_genomic_variant_history_events(self, genomicVariantId: str):
        instance = get_object_or_404(orm.GenomicVariant, id=genomicVariantId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{genomicVariantId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.GenomicVariantCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getGenomicVariantHistoryEventById",
    )
    def get_genomic_variant_history_event_by_id(
        self, genomicVariantId: str, eventId: str
    ):
        instance = get_object_or_404(orm.GenomicVariant, id=genomicVariantId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{genomicVariantId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertGenomicVariantToHistoryEvent",
    )
    def revert_genomic_variant_to_history_event(
        self, genomicVariantId: str, eventId: str
    ):
        instance = get_object_or_404(orm.GenomicVariant, id=genomicVariantId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()


@api_controller(
    "autocomplete",
    auth=[XSessionTokenAuth()],
    tags=["Genomic Variants"],
)
class GenePanelController(ControllerBase):

    @route.get(
        path="/gene-panels",
        response={200: List[str], **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getAllGenomicPanels",
    )
    def gell_all_genomic_panels(self, query: str = ""):
        variants = orm.GenomicVariant.objects.all()
        if query:
            variants = variants.filter(gene_panel__icontains=query)
        return 200, variants.values_list("gene_panel", flat=True).distinct()
