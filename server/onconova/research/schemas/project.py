from typing import List, Dict, Any
from pydantic import Field 

from onconova.core.serialization.factory import create_filters_schema
from onconova.core.schemas import BaseSchema, MetadataMixin, Period
from onconova.core.types import Nullable, Username, UUID
from onconova.research.models import project as orm


class ProjectCreate(BaseSchema):
    
    __orm_model__ = orm.Project 
    
    externalSource: Nullable[str] = Field(
        None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    leader: Username = Field(
        ...,
        description='User responsible for the project and its members',
        title='Project leader',
    )
    clinicalCenters: List[str] = Field(
        ...,
        description='Clinical centers that are part of the project',
        max_length=100,
        title='Clinical Centers',
    )
    title: str = Field(
        ..., 
        description='Title of the project', 
        title='Project title', 
        max_length=200,
    )
    summary: str = Field(
        ...,
        description='Description of the project',
        title='Project description',
    )
    ethicsApprovalNumber: str = Field(
        ...,
        description='Ethics approval number of the project',
        title='Ethics approval number',
        max_length=100,
    )
    status: Nullable[orm.ProjectStatusChoices] = Field(
        orm.ProjectStatusChoices.PLANNED,
        description='Status of the project',
        title='Project status',
    )
    dataConstraints: Nullable[Dict[str, Any]] = Field(
        None,
        description='Data constraints of the project',
        title='Data constraints',
    )
    members: Nullable[List[Username]] = Field(
        None,
        description='Users that are part of the project',
        title='Project members',
    )


class Project(ProjectCreate, MetadataMixin):
    pass


# Filter schema for project search queries
ProjectFilters = create_filters_schema(
    schema=Project,
    name="ProjectFilters",
)


class ProjectDataManagerGrantCreate(BaseSchema):

    __orm_model__ = orm.ProjectDataManagerGrant 
    
    externalSource: Nullable[str] = Field(
        None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    revoked: Nullable[bool] = Field(
        False,
        description='A flag that indicated whether the authorization has been revoked',
        title='Revoked',
    )
    validityPeriod: Period = Field(
        ..., 
        description='Period of validity', 
        title='Validity period'
    )
    
class ProjectDataManagerGrant(ProjectDataManagerGrantCreate, MetadataMixin):

    isValid: bool = Field(
        title="Is valid",
        description="Whether the authorization grant is valid today",
    )
    member: Username = Field(
        ...,
        description='Manager of the project data',
        title='Manager',
    )
    projectId: UUID = Field(
        ...,
        description='Project under which the permission is granted',
        title='Project',
    )


# Filter schema for project data manager grant search queries
ProjectDataManagerGrantFilters = create_filters_schema(
    schema=ProjectDataManagerGrant, name="ProjectDataManagerGrantFilters"
)
