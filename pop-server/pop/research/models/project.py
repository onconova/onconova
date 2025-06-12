import pghistory
import uuid
from django.db import models
from django.contrib.postgres import fields as postgres
from django.utils.translation import gettext_lazy as _

from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

from pop.core.models import BaseModel
from pop.core.auth.models import User


@pghistory.track()
class Project(BaseModel):

    objects = QueryablePropertiesManager()

    class ProjectStatus(models.TextChoices):
        PLANNED = "planned"
        ONGOING = "ongoing"
        COMPLETED = "completed"
        ABORTED = "aborted"

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
        choices=ProjectStatus.choices,
        default=ProjectStatus.PLANNED,
    )
    data_constraints = models.JSONField(
        verbose_name=_("Data constraints"),
        help_text=_("Data constraints of the project"),
        default=dict,
    )

    @property
    def description(self):
        return f"{self.title}"


class ProjectMembership(models.Model):
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

    member = models.ForeignKey(
        verbose_name=_("Manager"),
        help_text=_("Manager of the project data"),
        to=User,
        on_delete=models.CASCADE,
        related_name="data_management_grants",
    )
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="edit_permissions"
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
        return (
            f"Data manager role for {self.member.username} in project {self.project.title} from {self.validity_period.lower} to  {self.validity_period.upper}"
            + ("" if not self.revoked else " (revoked)")
        )
