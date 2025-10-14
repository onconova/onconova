import hashlib
import json
from collections import Counter, OrderedDict
from datetime import datetime
from enum import Enum
from typing import List

import pghistory
from django.conf import settings
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja.errors import HttpError, ValidationError
from ninja_extra import ControllerBase, api_controller, route, status
from ninja_extra.exceptions import APIException
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS, camel_to_snake
from onconova.interoperability.schemas import ExportMetadata
from onconova.oncology import schemas as oncological_schemas
from onconova.research.compilers import construct_dataset
from onconova.research import (
    models as orm,
    schemas as scm,
)


def convert_api_path_to_snake_case_path(path):
    components = path.split(".")
    components = [camel_to_snake(component) for component in components]
    return "__".join(components)


class EmptyCohortException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable. Requested cohort is empty."


@api_controller("/cohorts", auth=[XSessionTokenAuth()], tags=["Cohorts"])
class CohortsController(ControllerBase):

    @route.get(
        path="",
        response={200: Paginated[scm.Cohort], **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohorts",
    )
    @paginate()
    @ordering()
    def get_all_cohorts_matching_the_query(self, query: Query[scm.CohortFilters]):
        queryset = orm.Cohort.objects.all().order_by("-created_at")
        return query.filter(queryset)  # type: ignore

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCohorts],
        operation_id="createCohort",
    )
    def create_cohort(self, payload: scm.CohortCreate):
        # Check that requesting user is a member of the project
        project = get_object_or_404(orm.Project, id=payload.projectId)  # type: ignore
        if (
            not project.is_member(self.context.request.user)  # type: ignore
            and self.context.request.user.access_level < 3  # type: ignore
        ):
            raise HttpError(403, "User is not a member of the project")
        # Create cohort for that project
        cohort = payload.model_dump_django()
        # Update cohort cases
        cohort.update_cohort_cases()
        return 201, cohort

    @route.get(
        path="/{cohortId}",
        response={200: scm.Cohort, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortById",
    )
    def get_cohort_by_id(self, cohortId: str):
        return get_object_or_404(orm.Cohort, id=cohortId)

    @route.delete(
        path="/{cohortId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanDeleteCohorts],
        operation_id="deleteCohortById",
    )
    def delete_cohort(self, cohortId: str):
        get_object_or_404(orm.Cohort, id=cohortId).delete()
        return 204, None

    @route.put(
        path="/{cohortId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCohorts],
        operation_id="updateCohort",
    )
    def update_cohort(self, cohortId: str, payload: scm.CohortCreate):
        cohort = self.get_object_or_exception(orm.Cohort, id=cohortId)
        cohort = payload.model_dump_django(instance=cohort)
        cohort.update_cohort_cases()
        return cohort

    @route.get(
        path="/{cohortId}/cases",
        response={
            200: Paginated[oncological_schemas.PatientCase],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortCases",
    )
    @paginate()
    @anonymize()
    def get_cohort_cases(self, cohortId: str):
        return get_object_or_404(orm.Cohort, id=cohortId).cases.all()

    @route.get(
        path="/{cohortId}/contributors",
        response={200: List[scm.CohortContribution], 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortContributors",
    )
    @paginate()
    def get_cohort_contributions(self, cohortId: str):
        cohort = get_object_or_404(orm.Cohort, id=cohortId)
        contributions = Counter(
            [
                contributor
                for case in cohort.valid_cases.all()
                for contributor in case.contributors
            ]
        )
        return 200, [
            scm.CohortContribution(contributor=contributor, contributions=contributions)
            for contributor, contributions in contributions.items()
            if contributor
        ]

    @route.post(
        path="/{cohortId}/export",
        response={200: scm.ExportedCohortDefinition, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanExportData],
        operation_id="exportCohortDefinition",
    )
    def export_cohort_definition(self, cohortId: str):
        cohort = get_object_or_404(orm.Cohort, id=cohortId)

        if not perms.CanManageCohorts().check_user_object_permission(
            self.context.request.user, None, cohort  # type: ignore
        ):
            raise HttpError(403, "User is not a member of the project")

        data = scm.CohortCreate.model_validate(cohort).model_dump(mode="json")

        checksum = hashlib.md5(
            json.dumps(
                data,
                sort_keys=True,
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        return 200, {
            **ExportMetadata(
                exportedAt=datetime.now(),
                exportedBy=self.context.request.user.username,  # type: ignore
                exportVersion=settings.VERSION,
                checksum=checksum,
            ).model_dump(mode="json", exclude_unset=True),
            "definition": data,
        }

    @route.get(
        path="/{cohortId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.CohortCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllCohortHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_cohort_history_events(self, cohortId: str):
        instance = get_object_or_404(orm.Cohort, id=cohortId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{cohortId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.CohortCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getCohortHistoryEventById",
    )
    def get_cohort_history_event_by_id(self, cohortId: str, eventId: str):
        instance = get_object_or_404(orm.Cohort, id=cohortId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{cohortId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCohorts],
        operation_id="revertCohortToHistoryEvent",
    )
    def revert_cohort_to_history_event(self, cohortId: str, eventId: str):
        instance = self.get_object_or_exception(orm.Cohort, id=cohortId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.post(
        path="/{cohortId}/dataset/{datasetId}/export",
        response={200: scm.ExportedPatientCaseDataset, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanExportData],
        operation_id="exportCohortDataset",
    )
    def export_cohort_dataset(self, cohortId: str, datasetId: str):
        cohort = get_object_or_404(orm.Cohort, id=cohortId)
        dataset = get_object_or_404(orm.Dataset, id=datasetId)

        if (
            self.context
            and self.context.request
            and (
                not perms.CanManageCohorts().check_user_object_permission(
                    self.context.request.user, None, cohort
                )
                or not perms.CanManageDatasets().check_user_object_permission(
                    self.context.request.user, None, dataset
                )
            )
        ):
            raise HttpError(403, "User is not a member of the project")

        try:
            rules = [scm.DatasetRule.model_validate(rule) for rule in dataset.rules]
        except ValidationError:
            raise HttpError(422, "Invalid or outdated dataset rules")

        data = [
            scm.PatientCaseDataset.model_validate(subset)
            for subset in construct_dataset(cohort=cohort, rules=rules)
        ]

        data = [subset.model_dump(mode="json", exclude_unset=True) for subset in data]
        checksum = hashlib.md5(
            json.dumps(
                data,
                sort_keys=True,
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        export = {
            **ExportMetadata(
                exportedAt=datetime.now(),
                exportedBy=self.context.request.user.username,  # type: ignore
                exportVersion=settings.VERSION,
                checksum=checksum,
            ).model_dump(mode="json", exclude_unset=True),
            "dataset": data,
        }
        with pghistory.context(
            cohort=cohortId,
            datasetId=datasetId,
            dataset=[rule.model_dump(mode="json") for rule in rules],
            checksum=checksum,
            version=settings.VERSION,
        ):
            pghistory.create_event(cohort, label="export")
            pghistory.create_event(dataset, label="export")
        return 200, export

    @route.post(
        path="/{cohortId}/dataset",
        response={200: Paginated[scm.PatientCaseDataset], 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        exclude_unset=True,
        operation_id="getCohortDatasetDynamically",
    )
    @paginate()
    def construct_cohort_dataset(self, cohortId: str, rules: List[scm.DatasetRule]):
        return construct_dataset(
            cohort=get_object_or_404(orm.Cohort, id=cohortId), rules=rules
        )

    @route.get(
        path="/{cohortId}/traits",
        response={200: scm.CohortTraits, 404: None, 422: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortTraitsStatistics",
    )
    def get_cohort_traits_statistics(self, cohortId: str):
        cohort = get_object_or_404(orm.Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException

        age_median, age_iqr = cohort.get_cohort_trait_median(cohort.cases.all(), "age") or (None,None)
        data_completion_median, data_completion_iqr = cohort.get_cohort_trait_median(
            cohort.cases.all(), "data_completion_rate"
        ) or (None,None)
        overall_survival_median, overall_survival_iqr = cohort.get_cohort_trait_median(
            cohort.cases.all(), "overall_survival"
        ) or (None,None)

        return 200, scm.CohortTraits(
            age=scm.CohortTraitMedian(median=age_median, interQuartalRange=age_iqr),
            dataCompletion=scm.CohortTraitMedian(
                median=data_completion_median, interQuartalRange=data_completion_iqr
            ),
            overallSurvival=(
                scm.CohortTraitMedian(
                    median=overall_survival_median,
                    interQuartalRange=overall_survival_iqr,
                )
                if overall_survival_median
                else None
            ),
            genders=[
                scm.CohortTraitCounts(
                    category=category, counts=count, percentage=percentage
                )
                for category, (count, percentage) in cohort.get_cohort_trait_counts(
                    cohort.cases.all(), "gender__display"
                ).items()
            ],
            neoplasticSites=[
                scm.CohortTraitCounts(
                    category=category, counts=count, percentage=percentage
                )
                for category, (count, percentage) in cohort.get_cohort_trait_counts(
                    cohort.cases.all(),
                    "neoplastic_entities__topography_group__display",
                ).items()
            ],
            therapyLines=[
                scm.CohortTraitCounts(
                    category=category, counts=count, percentage=percentage
                )
                for category, (count, percentage) in cohort.get_cohort_trait_counts(
                    cohort.cases.all(), "therapy_lines__label"
                ).items()
            ],
            consentStatus=[
                scm.CohortTraitCounts(
                    category=category, counts=count, percentage=percentage
                )
                for category, (count, percentage) in cohort.get_cohort_trait_counts(
                    cohort.cases.all(), "consent_status"
                ).items()
            ],
        )
