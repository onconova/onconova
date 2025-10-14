from datetime import datetime
from enum import Enum
from typing import Any, List, Tuple, Type, Union, get_args
from uuid import UUID
import inspect 

from django.db.models import Q
from ninja import Field, Schema
from pydantic import AliasChoices
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, create_model, field_validator

from onconova.core.measures import Measure
from onconova.core.schemas import CodedConcept as CodedConceptSchema, MetadataAnonymizationMixin, MetadataMixin
from onconova.core.serialization import transforms as tfs
from onconova.core.serialization.factory import create_filters_schema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.core.utils import is_list, is_optional
from onconova.interoperability.schemas import ExportMetadata
from onconova.oncology import schemas as oncology_schemas
from onconova.research.models import dataset as orm

# Dynamically generate Enum from oncology schemas (excluding 'GenomicSignature')
DataResource = Enum(
    "DataResource",
    {
        model.__name__.upper(): model.__name__
        for model in oncology_schemas.ONCOLOGY_SCHEMAS
        if (issubclass(model, (MetadataAnonymizationMixin, MetadataMixin)) or issubclass(model, ModelGetSchema)) and model.__name__ != "GenomicSignature"
    },
    type=str,
)


class DatasetRule(Schema):
    """
    Schema representing a rule applied to a dataset resource.

    Attributes:
        resource (DataResource): The oncology resource this rule references.
        field (str): Dot-separated path of the field within the resource (e.g. 'medications.drug').
        transform (Nullable[str | Tuple[str, Any]]): Nullable transform expression or mapping applied to the field's value.
    """

    resource: DataResource = Field(  # type: ignore
        title="Resource", description="The oncology resource this rule references."
    )

    field: str = Field(
        title="Field",
        description="Dot-separated path of the field within the resource (e.g. 'medications.drug').",
    )

    transform: Nullable[str | Tuple[str, Any]] = Field(
        default=None,
        title="Transform",
        description="Nullable transform expression or mapping applied to the field's value.",
    )


class Dataset(ModelGetSchema):
    """
    Represents a dataset schema with composition rules, export metadata, and associated cohorts.

    Attributes:
        rules (List[DatasetRule]): List of composition rules that define the dataset's structure.
        lastExport (Nullable[datetime]): The datetime of the last export of this dataset.
        totalExports (int): The total number of times this dataset has been exported.
        cohortsIds (List[str]): List of cohort IDs that have been exported with this dataset.
        config (SchemaConfig): Configuration linking the schema to the ORM Dataset model.
    """

    rules: List[DatasetRule] = Field(
        default=[],
        title="Rules",
        description="List of composition rules that define the dataset's structure.",
    )
    lastExport: Nullable[datetime] = Field(
        default=None,
        title="Last Export",
        description="The datetime of the last export of this dataset",
        serialization_alias="last_export",
        validation_alias=AliasChoices("lastExport", "last_export"),
    )
    totalExports: int = Field(
        default=0,
        title="Total Exports",
        description="The total number times this dataset has been exported",
        serialization_alias="total_exports",
        validation_alias=AliasChoices("totalExports", "total_exports"),
    )
    cohortsIds: List[str] = Field(
        default=[],
        title="Cohorts",
        description="List of cohort IDs that have been exported with this dataset",
        serialization_alias="cohorts_ids",
        validation_alias=AliasChoices("cohortsIds", "cohorts_ids"),
    )
    config = SchemaConfig(model=orm.Dataset)


class DatasetCreate(ModelCreateSchema):
    """
    Schema for creating a new Dataset instance.

    Attributes:
        rules (List[DatasetRule]): List of composition rules that define the dataset's structure.
        config (SchemaConfig): Configuration specifying the ORM model associated with this schema.
    """

    rules: List[DatasetRule] = Field(
        default=[],
        title="Rules",
        description="List of composition rules that define the dataset's structure.",
    )

    config = SchemaConfig(model=orm.Dataset)


# Base filters schema generated from the Dataset schema
DatasetFiltersBase = create_filters_schema(schema=Dataset, name="DatasetFilters")


class DatasetFilters(DatasetFiltersBase):

    createdBy: Nullable[str] = Field(
        default=None,
        title="Created By",
        description="Filter datasets by the creator's username.",
    )

    def filter_createdBy(self, value: str) -> Q:
        """
        Apply a filter for the creator's username.
        """
        return Q(created_by=self.createdBy) if value is not None else Q()


def _create_partial_schema(schema: Type[Schema]) -> Type[Schema]:
    """
    Given a Pydantic model class, return a new model class with the same fields and validators,
    but all fields are optional (default=None).
    """
    # Prepare new fields dict, ensure they all are anonymized
    new_fields = {}

    for field_name, model_field in schema.model_fields.items():
        if field_name in ["anonymized"]:
            continue

        # Get schema field annotation
        annotation = model_field.annotation

        if is_optional(annotation):
            annotation = get_args(annotation)
            if len(annotation) > 1:
                annotation = Union[annotation]
            else:
                annotation = get_args(annotation)[0]

        if is_list(annotation):
            list_annotation = get_args(annotation)[0]
            if issubclass(list_annotation, PydanticBaseModel) and not issubclass(
                list_annotation, CodedConceptSchema
            ):
                related_schema_partial = _create_partial_schema(list_annotation)
                annotation = List[related_schema_partial]

        if inspect.isclass(annotation) and issubclass(annotation, PydanticBaseModel) and not issubclass(
            annotation, CodedConceptSchema
        ):
            annotation = _create_partial_schema(annotation)

        # Set default to None
        if "CodedConcept" in str(annotation):
            transforms = [
                tfs.GetCodedConceptDisplay,
                tfs.GetCodedConceptCode,
                tfs.GetCodedConceptSystem,
            ]
            new_fields[field_name] = (
                Nullable[str | List[Nullable[str]]],
                Field(
                    default=None,
                    validation_alias=AliasChoices(
                        *[
                            f"{model_field.alias}.{transform.name}"
                            for transform in transforms
                        ]
                    ),
                ),
            )
        elif "Measure" in str(annotation):
            new_fields[field_name] = (
                Nullable[Measure],
                Field(default=None, validation_alias=model_field.validation_alias),
            )
        elif "Period" in str(annotation):
            new_fields[field_name] = (
                Nullable[str],
                Field(default=None, validation_alias=model_field.validation_alias),
            )
        else:
            new_fields[field_name] = (
                Nullable[annotation],
                Field(default=None, validation_alias=model_field.validation_alias),
            )

    validators = None
    if "anonymized" in schema.model_fields:
        validators = {
            "always_anonymized": field_validator("anonymized")(lambda cls, v: True),
        }

    # Create a new model dynamically with the modified fields
    partial_schema = create_model(
        schema.__name__ + "Partial",
        __base__=schema,
        __validators__=validators,
        __config__=ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            arbitrary_types_allowed=True,
            exclude_unset=True,
        ),  # type: ignore
        **new_fields,
    )

    return partial_schema


partial_schemas = {
    schema.__name__.replace('Schema',''): _create_partial_schema(schema)
    for schema in oncology_schemas.ONCOLOGY_SCHEMAS
    if issubclass(schema, (MetadataAnonymizationMixin, MetadataMixin)) or issubclass(schema, ModelGetSchema)
}

class PatientCaseDataset(partial_schemas["PatientCase"]):
    """
    PatientCaseDataset schema representing a comprehensive dataset for a patient case in oncological research.

    Attributes:
        pseudoidentifier (str): Unique pseudoidentifier for the patient case.
        neoplasticEntities (Optional[List[NeoplasticEntity]]): List of neoplastic entities associated with the case.
        tnmStagings (Optional[List[TNMStaging]]): List of TNM staging resources.
        figoStagings (Optional[List[TNMStaging]]): List of FIGO staging resources.
        binetStagings (Optional[List[BinetStaging]]): List of Binet staging resources.
        raiStagings (Optional[List[RaiStaging]]): List of Rai staging resources.
        breslowStagings (Optional[List[BreslowDepth]]): List of Breslow depth resources.
        clarkStagings (Optional[List[ClarkStaging]]): List of Clark staging resources.
        issStagings (Optional[List[ISSStaging]]): List of ISS staging resources.
        rissStagings (Optional[List[RISSStaging]]): List of RISS staging resources.
        inssStagings (Optional[List[INSSStage]]): List of INSS staging resources.
        inrgssStagings (Optional[List[INRGSSStage]]): List of INRGSS staging resources.
        gleasonStagings (Optional[List[GleasonGrade]]): List of Gleason grade resources.
        rhabdomyosarcomaGroups (Optional[List[RhabdomyosarcomaClinicalGroup]]): List of rhabdomyosarcoma clinical group resources.
        wilmsStagings (Optional[List[WilmsStage]]): List of Wilms staging resources.
        lymphomaStagings (Optional[List[LymphomaStaging]]): List of lymphoma staging resources.
        tumorMarkers (Optional[List[TumorMarker]]): List of tumor marker resources.
        riskAssessments (Optional[List[RiskAssessment]]): List of risk assessment resources.
        therapyLines (Optional[List[TherapyLine]]): List of therapy line resources.
        systemicTherapies (Optional[List[SystemicTherapy]]): List of systemic therapy resources.
        surgeries (Optional[List[Surgery]]): List of surgery resources.
        radiotherapies (Optional[List[Radiotherapy]]): List of radiotherapy resources.
        adverseEvents (Optional[List[AdverseEvent]]): List of adverse event resources.
        treatmentResponses (Optional[List[TreatmentResponse]]): List of treatment response resources.
        performanceStatus (Optional[List[PerformanceStatus]]): List of performance status resources.
        comorbidities (Optional[List[ComorbiditiesAssessment]]): List of comorbidities assessment resources.
        genomicVariants (Optional[List[GenomicVariant]]): List of genomic variant resources.
        tumorMutationalBurdens (Optional[List[TumorMutationalBurden]]): List of tumor mutational burden resources.
        microsatelliteInstabilities (Optional[List[MicrosatelliteInstability]]): List of microsatellite instability resources.
        lossesOfHeterozygosity (Optional[List[LossOfHeterozygosity]]): List of loss of heterozygosity resources.
        homologousRecombinationDeficiencies (Optional[List[HomologousRecombinationDeficiency]]): List of homologous recombination deficiency resources.
        tumorNeoantigenBurdens (Optional[List[TumorNeoantigenBurden]]): List of tumor neoantigen burden resources.
        aneuploidScores (Optional[List[AneuploidScore]]): List of aneuploid score resources.
        vitals (Optional[List[Vitals]]): List of vital sign resources.
        lifestyles (Optional[List[Lifestyle]]): List of lifestyle resources.
        familyHistory (Optional[List[FamilyHistory]]): List of family history resources.
        unspecifiedTumorBoards (Optional[List[UnspecifiedTumorBoard]]): List of unspecified tumor board resources.
        molecularTumorBoards (Optional[List[UnspecifiedTumorBoard]]): List of molecular tumor board resources.

    Note:
        All attributes are nullable and may contain lists of corresponding schema resources.
    """

    id: Nullable[UUID] = Field(default=None, title="Unique identifier of the patient case")
    description: Nullable[str] = Field(default=None, title="Human-readable summary")
    pseudoidentifier: str = Field(title="Pseudoidentifier")
    neoplasticEntities: Nullable[List[partial_schemas["NeoplasticEntity"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "neoplasticEntities", "neoplastic_entities_resources"
        ),
    )
    tnmStagings: Nullable[List[partial_schemas["TNMStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("tnmStagings", "tnm_stagings_resources"),
    )
    figoStagings: Nullable[List[partial_schemas["TNMStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("figoStagings", "figo_stagings_resources"),
    )
    binetStagings: Nullable[List[partial_schemas["BinetStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("binetStagings", "binet_stagings_resources"),
    )
    raiStagings: Nullable[List[partial_schemas["RaiStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("raiStagings", "rai_stagings_resources"),
    )
    breslowStagings: Nullable[List[partial_schemas["BreslowDepth"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("breslowStagings", "breslow_depths_resources"),
    )
    clarkStagings: Nullable[List[partial_schemas["ClarkStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("clarkStagings", "clark_stagings_resources"),
    )
    issStagings: Nullable[List[partial_schemas["ISSStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("issStagings", "iss_stagings_resources"),
    )
    rissStagings: Nullable[List[partial_schemas["RISSStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("rissStagings", "riss_stagings_resources"),
    )
    inssStagings: Nullable[List[partial_schemas["INSSStage"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("inssStagings", "inss_stagings_resources"),
    )
    inrgssStagings: Nullable[List[partial_schemas["INRGSSStage"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("inrgssStagings", "inrgss_stagings_resources"),
    )
    gleasonStagings: Nullable[List[partial_schemas["GleasonGrade"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("gleasonStagings", "gleason_grades_resources"),
    )
    rhabdomyosarcomaGroups: Nullable[List[partial_schemas["RhabdomyosarcomaClinicalGroup"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "rhabdomyosarcomaGroups", "rhabdomyosarcoma_clinical_groups_resources"
        ),
    )
    wilmsStagings: Nullable[List[partial_schemas["WilmsStage"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("wilmsStagings", "wilms_stagings_resources"),
    )
    lymphomaStagings: Nullable[List[partial_schemas["LymphomaStaging"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "lymphomaStagings", "lymphoma_stagings_resources"
        ),
    )
    tumorMarkers: Nullable[List[partial_schemas["TumorMarker"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("tumorMarkers", "tumor_markers_resources"),
    )
    riskAssessments: Nullable[List[partial_schemas["RiskAssessment"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("riskAssessments", "risk_assessments_resources"),
    )
    therapyLines: Nullable[List[partial_schemas["TherapyLine"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("therapyLines", "therapy_lines_resources"),
    )
    systemicTherapies: Nullable[List[partial_schemas["SystemicTherapy"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "systemicTherapies", "systemic_therapies_resources"
        ),
    )
    surgeries: Nullable[List[partial_schemas["Surgery"]]] = Field(  # type: ignore
        default=None, validation_alias=AliasChoices("surgeries", "surgeries_resources")
    )
    radiotherapies: Nullable[List[partial_schemas["Radiotherapy"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("radiotherapies", "radiotherapies_resources"),
    )
    adverseEvents: Nullable[List[partial_schemas["AdverseEvent"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("adverseEvents", "adverse_events_resources"),
    )
    treatmentResponses: Nullable[List[partial_schemas["TreatmentResponse"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "treatmentResponses", "treatment_responses_resources"
        ),
    )
    performanceStatus: Nullable[List[partial_schemas["PerformanceStatus"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "performanceStatus", "performance_status_resources"
        ),
    )
    comorbidities: Nullable[List[partial_schemas["ComorbiditiesAssessment"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("comorbidities", "comorbidities_resources"),
    )
    genomicVariants: Nullable[List[partial_schemas["GenomicVariant"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("genomicVariants", "genomic_variants_resources"),
    )
    tumorMutationalBurdens: Nullable[List[partial_schemas["TumorMutationalBurden"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "tumorMutationalBurdens", "tumor_mutational_burdens_resources"
        ),
    )
    microsatelliteInstabilities: Nullable[List[partial_schemas["MicrosatelliteInstability"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "microsatelliteInstabilities", "microsatellite_instabilities_resources"
        ),
    )
    lossesOfHeterozygosity: Nullable[List[partial_schemas["LossOfHeterozygosity"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "lossesOfHeterozygosity", "losses_of_heterozygosity_resources"
        ),
    )
    homologousRecombinationDeficiencies: Nullable[List[partial_schemas["HomologousRecombinationDeficiency"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "homologousRecombinationDeficiencies",
            "homologous_recombination_deficiencies_resources",
        ),
    )
    tumorNeoantigenBurdens: Nullable[List[partial_schemas["TumorNeoantigenBurden"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "tumorNeoantigenBurdens", "tumor_neoantigen_burdens_resources"
        ),
    )
    aneuploidScores: Nullable[List[partial_schemas["AneuploidScore"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("aneuploidScores", "aneuploid_scores_resources"),
    )
    vitals: Nullable[List[partial_schemas["Vitals"]]] = Field(  # type: ignore
        default=None, validation_alias=AliasChoices("vitals", "vitals_resources")
    )
    lifestyles: Nullable[List[partial_schemas["Lifestyle"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("lifestyles", "lifestyles_resources"),
    )
    familyHistory: Nullable[List[partial_schemas["FamilyHistory"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices("familyHistory", "family_histories_resources"),
    )
    vitals: Nullable[List[partial_schemas["Vitals"]]] = Field(  # type: ignore
        default=None, validation_alias=AliasChoices("vitals", "vitals_resources")
    )
    unspecifiedTumorBoards: Nullable[List[partial_schemas["UnspecifiedTumorBoard"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "unspecifiedTumorBoards", "unspecified_tumor_boards_resources"
        ),
    )
    molecularTumorBoards: Nullable[List[partial_schemas["UnspecifiedTumorBoard"]]] = Field(  # type: ignore
        default=None,
        validation_alias=AliasChoices(
            "molecularTumorBoards", "molecular_tumor_boards_resources"
        ),
    )


class ExportedPatientCaseDataset(ExportMetadata):
    dataset: List[PatientCaseDataset] = Field(
        title="Dataset",
        description="The dataset that was exported",
    )
