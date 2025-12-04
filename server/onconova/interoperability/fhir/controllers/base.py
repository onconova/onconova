from typing import List
from django.db import IntegrityError, models
from ninja_extra import ControllerBase
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
    OperationOutcomeIssue,
)
from fhircraft.fhir.resources.base import FHIRBaseModel
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
)
from pydantic_core import ValidationError

COMMON_READ_HTTP_ERRORS = {410: None, 404: None}
COMMON_UPDATE_HTTP_ERRORS = {
    400: OperationOutcome,
    405: OperationOutcome,
    409: OperationOutcome,
    402: None,
}
COMMON_DELETE_HTTP_ERRORS = {404: OperationOutcome}
COMMON_CREATE_HTTP_ERRORS = {
    400: OperationOutcome,
    409: OperationOutcome,
}


class FhirBaseController(ControllerBase):

    def read_fhir_resource(
        self, rid: str, models: type[models.Model] | List[type[models.Model]]
    ):
        """Read a FHIR resource by its ID"""
        if not isinstance(models, list):
            models = [models]
        # Get the instance from the database
        for model in models:
            if instance := model.objects.filter(id=rid).first():
                break
        else:
            for model in models:
                # If resource not found, check if it was deleted
                if model.pgh_event_model.objects.filter(pgh_obj_id=rid, pgh_label="delete").exists():  # type: ignore
                    return 410, None
            else:
                return 404, None
        # Set the Last-Modified header if the instance has an updated_at timestamp
        if getattr(instance, "updated_at", None):
            assert self.context and self.context.response
            self.context.response.headers["Last-Modified"] = instance.updated_at.isoformat()  # type: ignore
        return instance

    def update_fhir_resource(self, rid: str, payload: OnconovaFhirBaseSchema):
        """Update a FHIR resource by its ID"""
        assert self.context and self.context.response and self.context.request
        if not (
            instance := payload.__class__.get_orm_model(payload)  # type: ignore
            .objects.filter(id=rid)
            .first()
        ):
            return 405, OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="not-found",
                        diagnostics="Resource with given ID not found, and create-update is not supported.",
                    )
                ]
            )
        if instance and str(instance.id) != payload.id:  # type: ignore
            return 400, OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="invalid",
                        diagnostics="ID in payload does not match ID in URL.",
                    )
                ]
            )
        try:
            resource = payload.fhir_to_onconova(  # type: ignore
                payload
            ).model_dump_django(instance=instance)
        except ValidationError as ve:
            return 400, OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="invalid",
                        diagnostics=str(ve),
                    )
                ]
            )
        except IntegrityError as ie:
            return 409, OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="conflict",
                        diagnostics="One of the unique fields conflicts with an existing record.",
                    )
                ]
            )

        for child_instance, new_child_schema in payload.fhir_to_onconova_related(
            payload
        ):
            if not child_instance.pk:
                return 400, OperationOutcome(
                    issue=[
                        OperationOutcomeIssue(
                            severity="error",
                            code="invalid",
                            diagnostics="ID mismatch for child resource.",
                        )
                    ]
                )
            try:
                new_child_schema.model_dump_django(instance=child_instance)
            except ValidationError as ve:
                return 400, OperationOutcome(
                    issue=[
                        OperationOutcomeIssue(
                            severity="error",
                            code="invalid",
                            diagnostics=str(ve),
                        )
                    ]
                )
            except IntegrityError as ie:
                return 409, OperationOutcome(
                    issue=[
                        OperationOutcomeIssue(
                            severity="error",
                            code="conflict",
                            diagnostics="One of the unique fields conflicts with an existing record.",
                        )
                    ]
                )

        if (resourceType := getattr(payload, "resourceType", None)) and (
            resourceId := getattr(payload, "id", None)
        ):
            self.context.response.headers["Location"] = (
                f"/fhir/{resourceType}/{resourceId}"
            )
        preference = self.context.request.headers.get("Prefer", "return=representation")
        if preference == "return=representation":
            return 200, resource
        elif preference == "return=minimal":
            return 200, None
        elif preference == "return=OperationOutcome":
            return 200, OperationOutcome(
                issue=[OperationOutcomeIssue(severity="success")]
            )
        else:
            return 400, None

    def delete_fhir_resource(
        self, rid: str, models: type[models.Model] | List[type[models.Model]]
    ):
        """Delete a FHIR resource by its ID"""
        if not isinstance(models, list):
            models = [models]
        assert self.context and self.context.response and self.context.request
        for model in models:
            if instance := model.objects.filter(id=rid).first():
                break
        else:
            return 404, OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="not-found",
                        diagnostics="Resource with given ID not found.",
                    )
                ]
            )
        instance.delete()
        return 204, None

    def create_fhir_resource(self, payload: OnconovaFhirBaseSchema):
        assert self.context and self.context.response and self.context.request
        try:
            resource = payload.__class__.fhir_to_onconova(payload).model_dump_django()
        except ValidationError as ve:
            return 400, OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="invalid",
                        diagnostics=str(ve),
                    )
                ]
            )
        except IntegrityError as ie:
            return 409, OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="conflict",
                        diagnostics=str(ie),
                    )
                ]
            )
        payload.id = str(resource.id)  # type: ignore
        for instance, new_child_schema in payload.fhir_to_onconova_related(payload):
            try:
                new_child_schema.model_dump_django(instance=instance)
            except ValidationError as ve:
                return 400, OperationOutcome(
                    issue=[
                        OperationOutcomeIssue(
                            severity="error",
                            code="invalid",
                            diagnostics=str(ve),
                        )
                    ]
                )
            except IntegrityError as ie:
                return 409, OperationOutcome(
                    issue=[
                        OperationOutcomeIssue(
                            severity="error",
                            code="conflict",
                            diagnostics=str(ie),
                        )
                    ]
                )
        if resourceType := getattr(payload, "resourceType", None):
            self.context.response.headers["Location"] = (
                f"/fhir/{resourceType}/{resource.id}"
            )
        preference = self.context.request.headers.get("Prefer", "return=representation")
        if preference == "return=representation":
            return 200, resource
        elif preference == "return=minimal":
            return 200, None
        elif preference == "return=OperationOutcome":
            return 200, OperationOutcome(
                issue=[OperationOutcomeIssue(severity="success")]
            )
        else:
            return 400, None
