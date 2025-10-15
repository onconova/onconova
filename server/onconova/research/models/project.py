import uuid

import pghistory
from django.contrib.postgres import fields as postgres
from django.db import models
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

from onconova.core.auth.models import User
from onconova.core.models import BaseModel

class ProjectStatusChoices(models.TextChoices):
    """
    An enumeration representing the possible statuses of a project.

    Attributes:
        PLANNED: Indicates the project is planned but not yet started.
        ONGOING: Indicates the project is currently in progress.
        COMPLETED: Indicates the project has been finished.
        ABORTED: Indicates the project was stopped before completion.
    """
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    ABORTED = "aborted"

@pghistory.track()
class Project(BaseModel):
    """
    Represents a research project with associated metadata, members, and status.

    Attributes:
        objects (QueryablePropertiesManager): Custom manager for querying project properties.
        leader (models.ForeignKey[User]): The user responsible for the project and its members.
        members (models.ManyToManyField[User]): Users that are part of the project, managed through ProjectMembership.
        clinical_centers (postgres.ArrayField[models.CharField]): List of clinical centers involved in the project.
        title (models.CharField): Unique title of the project.
        summary (models.CharField): Description of the project.
        ethics_approval_number (models.CharField): Ethics approval number for the project.
        status (models.CharField): Current status of the project, chosen from ProjectStatusChoices.
        data_constraints (models.JSONField): Data constraints associated with the project.
    """ 
    
    objects = QueryablePropertiesManager()

    leader = models.ForeignKey(
        verbose_name=_("Project leader"),
        help_text=_("User responsible for the project and its members"),
        to=User,
        on_delete=models.PROTECT,
        related_name="+",
    )
    members = models.ManyToManyField(
        verbose_name=_("Project members"),
        help_text=_("Users that are part of the project"),
        to=User,
        through="ProjectMembership",
        related_name="projects",
    )
    clinical_centers = postgres.ArrayField(
        verbose_name=_("Clinical centers"),
        help_text=_("Clinical centers that are part of the project"),
        base_field=models.CharField(max_length=100),
        default=list,
    )
    title = models.CharField(
        verbose_name=_("Project title"),
        help_text=_("Title of the project"),
        max_length=200,
        unique=True,
    )
    summary = models.TextField(
        verbose_name=_("Project description"),
        help_text=_("Description of the project"),
    )
    ethics_approval_number = models.CharField(
        verbose_name=_("Ethics approval number"),
        help_text=_("Ethics approval number of the project"),
        max_length=100,
    )
    status = models.CharField(
        verbose_name=_("Project status"),
        help_text=_("Status of the project"),
        max_length=20,
        choices=ProjectStatusChoices.choices,
        default=ProjectStatusChoices.PLANNED,
    )
    data_constraints = models.JSONField(
        verbose_name=_("Data constraints"),
        help_text=_("Data constraints of the project"),
        default=dict,
    )

    @property
    def description(self):
        """
        Returns the title of the project as its description.

        Returns:
            (str): The title of the project.
        """
        return f"{self.title}"

    def is_member(self, user: User) -> bool:
        """
        Checks if the given user is a member of the project.

        A user is considered a member if they are included in the project's members list
        or if they are the project leader.

        Args:
            user (User): The user to check for membership.

        Returns:
            (bool): True if the user is a member or the leader, False otherwise.
        """
        return user in self.members.all() or user == self.leader


class ProjectMembership(models.Model):
    """
    Represents the membership of a user in a project.

    Attributes:
        member (ForeignKey): Reference to the user who is part of the project.
        project (ForeignKey): Reference to the project the user is associated with.
        date_joined (DateField): The date when the user joined the project.

    Constraints:
        Ensures that each user can only be a member of a project once (unique combination of project and member).
    """
    member = models.ForeignKey(
        verbose_name=_("User"),
        help_text=_("User that is part of a project"),
        to=User,
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(
        verbose_name=_("Project"),
        help_text=_("Project that the user is part of"),
        to=Project,
        on_delete=models.CASCADE,
    )
    date_joined = models.DateField(
        verbose_name=_("Date joined"),
        help_text=_("Date when the user joined the project"),
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "member"], name="unique_project_members"
            )
        ]


@pghistory.track()
class ProjectDataManagerGrant(BaseModel):
    """
    Represents a grant of data management permissions for a specific user (manager) on a project.

    Attributes:
        member (ForeignKey): Reference to the User who is granted data management permissions.
        project (ForeignKey): Reference to the Project under which the permission is granted.
        revoked (BooleanField): Indicates whether the authorization has been revoked.
        validity_period (DateRangeField): The period during which the grant is valid.
        is_valid (AnnotationProperty): Annotated property indicating if the grant is currently valid,
            based on the revoked status and validity period.
    """

    member = models.ForeignKey(
        verbose_name=_("Manager"),
        help_text=_("Manager of the project data"),
        to=User,
        on_delete=models.CASCADE,
        related_name="data_management_grants",
    )
    project = models.ForeignKey(
        to="Project",
        on_delete=models.CASCADE,
        related_name="edit_permissions",
        verbose_name=_("Project"),
        help_text=_("Project under which the permission is granted"),
    )
    revoked = models.BooleanField(
        verbose_name=_("Revoked"),
        help_text=_("A flag that indicated whether the authorization has been revoked"),
        default=False,
    )
    validity_period = postgres.DateRangeField(
        verbose_name=_("Validity period"),
        help_text=_("Period of validity"),
    )
    is_valid = AnnotationProperty(
        annotation=models.Case(
            models.When(
                revoked=True,
                then=False,
            ),
            models.When(
                validity_period__startswith__lte=models.functions.Now(),
                validity_period__endswith__gte=models.functions.Now(),
                then=True,
            ),
            default=False,
            output_field=models.BooleanField(),
        )
    )

    @property
    def description(self):
        """
        Returns a formatted string describing the data manager role for a project member, including the member's username, project title, validity period, and revoked status if applicable.
        """
        return (
            f"Data manager role for {self.member.username} in project {self.project.title} from {self.validity_period.lower} to  {self.validity_period.upper}"
            + ("" if not self.revoked else " (revoked)")
        )
