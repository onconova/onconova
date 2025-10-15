from typing import List 
from pydantic import Field
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept, Measure
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import tumor_marker as orm


class TumorMarkerCreate(BaseSchema):
    
    __orm_model__ = orm.TumorMarker

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
    caseId: UUID = Field(
        ...,
        description='Indicates the case of the patient related to the tumor marker result',
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date at which the tumor marker was analyzed.',
        title='Date',
    )
    analyte: CodedConcept = Field(
        ...,
        description='The chemical or biological substance/agent that is analyzed.',
        title='Analyte',
        json_schema_extra={'x-terminology': 'TumorMarkerAnalyte'},
    )
    massConcentration: Nullable[Measure] = Field(
        None,
        description='Mass concentration of the analyte (if revelant/measured)',
        title='Mass concentration',
        json_schema_extra={
            'x-measure': 'MassConcentration',
            'x-default-unit': 'g/l',
        },
    )
    arbitraryConcentration: Nullable[Measure] = Field(
        None,
        description='Arbitrary concentration of the analyte (if revelant/measured)',
        title='Arbitrary concentration',
        json_schema_extra={
            'x-measure': 'ArbitraryConcentration',
            'x-default-unit': 'kIU/l',
        },
    )
    substanceConcentration: Nullable[Measure] = Field(
        None,
        description='Substance concentration of the analyte (if revelant/measured)',
        title='Substance concentration',
        json_schema_extra={
            'x-measure': 'SubstanceConcentration',
            'x-default-unit': 'mol/l',
        },
    )
    fraction: Nullable[Measure] = Field(
        None,
        description='Analyte fraction (if revelant/measured)',
        title='Fraction',
        json_schema_extra={
            'x-measure': 'Fraction',
            'x-default-unit': '%',
        },
    )
    multipleOfMedian: Nullable[Measure] = Field(
        None,
        description='Multiples of the median analyte (if revelant/measured)',
        title='Multiples of the median',
        json_schema_extra={
            'x-measure': 'MultipleOfMedian',
            'x-default-unit': 'multiple_of_median',
        },
    )
    tumorProportionScore: Nullable[orm.TumorMarkerTumorProportionScoreChoices] = Field(
        None,
        description='Categorization of the percentage of cells in a tumor that express PD-L1',
        title='Immune Cells Score (ICS)',
    )
    immuneCellScore: Nullable[orm.TumorMarkerImmuneCellScoreChoices] = Field(
        None,
        description='Categorization of the percentage of PD-L1 positive immune cells',
        title='Immune Cells Score (ICS)',
    )
    combinedPositiveScore: Nullable[Measure] = Field(
        None,
        description='The number of PD-L1 positive cells, including tumor cells, lymphocytes, and macrophages divided by the total number of viable tumor cells multiplied by 100',
        title='Combined Positive Score (CPS)',
        json_schema_extra={
            'x-measure': 'Fraction',
            'x-default-unit': '%',
        },
    )
    immunohistochemicalScore: Nullable[orm.TumorMarkerImmunohistochemicalScoreChoices] = (
        Field(
            None,
            description='Categorization of the number of analyte-positive cells in a sample',
            title='Immunohistochemical Score',
        )
    )
    presence: Nullable[orm.TumorMarkerPresenceChoices] = Field(
        None,
        description='Whether an analyte has tested positive or negative.',
        title='Presence',
    )
    nuclearExpressionStatus: Nullable[orm.TumorMarkerNuclearExpressionStatusChoices] = (
        Field(
            None,
            description='Categorization of the status of expression of the analyte',
            title='Nuclear expression status',
        )
    )
    relatedEntitiesIds: Nullable[List[UUID]] = Field(
        None,
        description='References to the neoplastic entities that are related or the focus of the tumor marker analysis.',
        title='Related neoplastic entities',
    )


class TumorMarker(TumorMarkerCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"