import pghistory
from ninja import Query
from ninja.schema import Schema, Field
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.auth.models import User
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent
from pop.research.models.project import Project, ProjectDataManagerGrant

from django.shortcuts import get_object_or_404

from pop.research.schemas.project import (
    ProjectSchema,
    ProjectCreateSchema,
    ProjectFilters,
    ProjectDataManagerGrantSchema,
    ProjectDataManagerGrantCreateSchema,
)


@api_controller(
    "projects",
    auth=[XSessionTokenAuth()],
    tags=["Projects"],
)
class ProjectController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[ProjectSchema],
        },
        permissions=[perms.CanViewProjects],
        operation_id="getProjects",
    )
    @paginate()
    def get_all_projects_matching_the_query(self, query: Query[ProjectFilters]):  # type: ignore
        queryset = Project.objects.all().order_by("-created_at")
        return query.filter(queryset)

    @route.post(
        path="",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageProjects],
        operation_id="createProject",
    )
    def create_project(self, payload: ProjectCreateSchema):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{projectId}",
        response={
            200: ProjectSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewProjects],
        operation_id="getProjectById",
    )
    def get_project_by_id(self, projectId: str):
        return get_object_or_404(Project, id=projectId)

    @route.put(
        path="/{projectId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageProjects],
        operation_id="updateProjectById",
    )
    def update_project(self, projectId: str, payload: ProjectCreateSchema):  # type: ignore
        instance = get_object_or_404(Project, id=projectId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{projectId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanDeleteProjects],
        operation_id="deleteProjectById",
    )
    def delete_project(self, projectId: str):
        get_object_or_404(Project, id=projectId).delete()
        return 204, None

    @route.get(
        path="/{projectId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(ProjectCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewProjects],
        operation_id="getAllProjectHistoryEvents",
    )
    @paginate()
    def get_all_project_history_events(self, projectId: str):
        instance = get_object_or_404(Project, id=projectId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{projectId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(ProjectCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewProjects],
        operation_id="getProjectHistoryEventById",
    )
    def get_project_history_event_by_id(self, projectId: str, eventId: str):
        instance = get_object_or_404(Project, id=projectId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{projectId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageProjects],
        operation_id="revertProjectToHistoryEvent",
    )
    def revert_project_to_history_event(self, projectId: str, eventId: str):
        instance = get_object_or_404(Project, id=projectId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{projectId}/members/{memberId}/data-management/grants",
        response={
            200: Paginated[ProjectDataManagerGrantSchema],
        },
        permissions=[perms.CanViewProjects],
        operation_id="getProjectDataManagerGrant",
    )
    @paginate()
    def get_all_project_data_manager_grant(self, projectId: str, memberId: str):  # type: ignore
        return ProjectDataManagerGrant.objects.filter(
            project=get_object_or_404(Project, id=projectId),
            member=get_object_or_404(User, id=memberId),
        ).order_by("-created_at")

    @route.post(
        path="/{projectId}/members/{memberId}/data-management/grants",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageProjects],
        operation_id="createProjectDataManagerGrant",
    )
    def create_project_data_manager_grant(self, projectId: str, memberId: str, payload: ProjectDataManagerGrantCreateSchema):  # type: ignore
        project = get_object_or_404(Project, id=projectId)
        member = get_object_or_404(User, id=memberId)
        instance = ProjectDataManagerGrant(project=project, member=member)
        return 201, payload.model_dump_django(instance=instance)

    @route.get(
        path="/{projectId}/members/{memberId}/data-management/grants/{grantId}",
        response={
            200: ProjectDataManagerGrantSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewProjects],
        operation_id="getProjectDataManagerGrantById",
    )
    def check_project_data_manager_grant(
        self, projectId: str, memberId: str, grantId: str
    ):
        return 200, get_object_or_404(
            ProjectDataManagerGrant,
            id=grantId,
            project_id=projectId,
            member_id=memberId,
        )

    @route.delete(
        path="/{projectId}/members/{memberId}/data-management/grants/{grantId}",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageProjects],
        operation_id="revokeProjectDataManagerGrant",
    )
    def revoke_project_data_manager_grant(
        self, projectId: str, memberId: str, grantId: str
    ):
        instance = get_object_or_404(
            ProjectDataManagerGrant,
            id=grantId,
            project_id=projectId,
            member_id=memberId,
        )
        instance.revoked = True
        instance.save()
        return 201, instance

    @route.get(
        path="/{projectId}/members/{memberId}/data-management/grants/{grantId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(ProjectCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewProjects],
        operation_id="getAllProjectDataManagementGrantHistoryEvents",
    )
    @paginate()
    def get_all_project_data_management_grant_history_events(
        self, projectId: str, memberId: str, grantId: str
    ):
        instance = get_object_or_404(
            ProjectDataManagerGrant,
            id=grantId,
            project_id=projectId,
            member_id=memberId,
        )
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{projectId}/members/{memberId}/data-management/grants/{grantId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(ProjectCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewProjects],
        operation_id="getProjectDataManagementGrantHistoryEventById",
    )
    def get_project_data_management_grant_history_event_by_id(
        self, projectId: str, memberId: str, grantId: str, eventId: str
    ):
        instance = get_object_or_404(
            ProjectDataManagerGrant,
            id=grantId,
            project_id=projectId,
            member_id=memberId,
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{projectId}/members/{memberId}/data-management/grants/{grantId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageProjects],
        operation_id="revertProjectDataManagementGrantToHistoryEvent",
    )
    def revert_project_data_management_grant_to_history_event(
        self, projectId: str, memberId: str, grantId: str, eventId: str
    ):
        instance = get_object_or_404(
            ProjectDataManagerGrant,
            id=grantId,
            project_id=projectId,
            member_id=memberId,
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
