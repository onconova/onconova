import resource
from typing import ClassVar
from pydantic import field_validator
from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Coding,
    Quantity,
    Extension,
)
from fhircraft.fhir.resources.base import FHIRBaseModel
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import CancerStage as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.oncology.models.staging import StagingDomain
from onconova.core.schemas import CodedConcept, Measure


class CancerStageProfile(OnconovaFhirBaseSchema, fhir.OnconovaCancerStage):

    __model__ = models.Staging
    __schemas__: ClassVar = {
        StagingDomain.FIGO: schemas.FIGOStaging,
        StagingDomain.BINET: schemas.BinetStaging,
        StagingDomain.RAI: schemas.RaiStaging,
        StagingDomain.BRESLOW: schemas.BreslowDepth,
        StagingDomain.CLARK: schemas.ClarkStaging,
        StagingDomain.ISS: schemas.ISSStaging,
        StagingDomain.RISS: schemas.RISSStaging,
        StagingDomain.INSS: schemas.INSSStage,
        StagingDomain.INRGSS: schemas.INRGSSStage,
        StagingDomain.GLEASON: schemas.GleasonGrade,
        StagingDomain.RHABDO: schemas.RhabdomyosarcomaClinicalGroup,
        StagingDomain.WILMS: schemas.WilmsStage,
    }

    __create_schemas__: ClassVar = {
        StagingDomain.FIGO: schemas.FIGOStagingCreate,
        StagingDomain.BINET: schemas.BinetStagingCreate,
        StagingDomain.RAI: schemas.RaiStagingCreate,
        StagingDomain.BRESLOW: schemas.BreslowDepthCreate,
        StagingDomain.CLARK: schemas.ClarkStagingCreate,
        StagingDomain.ISS: schemas.ISSStagingCreate,
        StagingDomain.RISS: schemas.RISSStagingCreate,
        StagingDomain.INSS: schemas.INSSStageCreate,
        StagingDomain.INRGSS: schemas.INRGSSStageCreate,
        StagingDomain.GLEASON: schemas.GleasonGradeCreate,
        StagingDomain.RHABDO: schemas.RhabdomyosarcomaClinicalGroupCreate,
        StagingDomain.WILMS: schemas.WilmsStageCreate,
    }

    @field_validator("code", mode="after", check_fields=False)
    @classmethod
    def discriminator(cls, concept: fhir.CodeableConcept) -> fhir.CodeableConcept:
        rules = cls.__registry__.get_rules("stagingDomain")
        allowed_codes = [rule.fhir_value.code for rule in rules]
        if not concept.coding:
            raise ValueError("The concept has no coding")
        if (coding := concept.coding[0]).code not in allowed_codes:
            raise ValueError(
                f"The code {coding.system}#{coding.code} is not a valid staging code discriminator"
            )
        return concept

    @classmethod
    def get_orm_model(cls, obj):  # type: ignore[override]
        try:
            domain = cls.map_to_internal(
                "stagingDomain", obj.fhirpath_single("Observation.code.coding")
            )
            return cls.__schemas__[domain].get_orm_model()
        except:
            return models.Staging

    @classmethod
    def get_orm_schema(cls, obj):
        domain = None
        if hasattr(obj, "fhirpath_single"):
            domain = cls.map_to_internal(
                "stagingDomain", obj.fhirpath_single("Observation.code.coding")
            )
        if hasattr(obj, "stagingDomain"):
            domain = obj.stagingDomain
        if hasattr(obj, "staging_domain"):
            domain = obj.staging_domain
        return (
            cls.__schemas__.get(domain, schemas.Staging) if domain else schemas.Staging
        )

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaCancerStage
    ) -> (
        schemas.FIGOStagingCreate
        | schemas.BinetStagingCreate
        | schemas.RaiStagingCreate
        | schemas.BreslowDepthCreate
        | schemas.ClarkStagingCreate
        | schemas.ISSStagingCreate
        | schemas.RISSStagingCreate
        | schemas.GleasonGradeCreate
        | schemas.INSSStageCreate
        | schemas.INRGSSStageCreate
        | schemas.WilmsStageCreate
        | schemas.RhabdomyosarcomaClinicalGroupCreate
    ):
        create_schema = cls.__create_schemas__[
            cls.map_to_internal(
                "stagingDomain", obj.fhirpath_single("Observation.code.coding")
            )
        ]
        common = {
            "externalSource": None,
            "externalSourceId": None,
            "caseId": obj.fhirpath_single(
                "Observation.subject.reference.replace('Patient/', '')"
            ),
            "stagedEntitiesIds": obj.fhirpath_values(
                "Observation.focus.reference.replace('Condition/', '')"
            ),
            "date": obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
        }
        if create_schema is schemas.BreslowDepthCreate:
            return create_schema(
                **common,
                depth=Measure(
                    value=obj.fhirpath_single(
                        "value.extension('https://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-stage-breslow-depth').valueQuantity.value.getValue()"
                    ),
                    unit=obj.fhirpath_single(
                        "value.extension('https://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-stage-breslow-depth').valueQuantity.code.getValue()"
                    ),
                ),
                isUlcered=obj.fhirpath_single(
                    "Observation.component.where(code.coding.code='105600-1').valueCodeableConcept.coding.code='LA9633-4'"
                ),
            )
        elif (
            create_schema is schemas.FIGOStagingCreate
            or create_schema is schemas.RaiStagingCreate
        ):
            return create_schema(
                **common,
                stage=CodedConcept.model_validate(
                    obj.fhirpath_single(
                        "Observation.valueCodeableConcept.coding"
                    ).model_dump()
                ),
                methodology=(
                    CodedConcept.model_validate(method.model_dump())
                    if (method := obj.fhirpath_single("Observation.method.coding"))
                    else None
                ),
            )
        else:
            return create_schema(
                **common,
                stage=CodedConcept.model_validate(obj.fhirpath_single("Observation.valueCodeableConcept.coding").model_dump()),  # type: ignore
            )

    @classmethod
    def onconova_to_fhir(
        cls,
        obj: (
            schemas.FIGOStaging
            | schemas.BinetStaging
            | schemas.RaiStaging
            | schemas.BreslowDepth
            | schemas.ClarkStaging
            | schemas.ISSStaging
            | schemas.RISSStaging
            | schemas.GleasonGrade
            | schemas.INSSStage
            | schemas.INRGSSStage
            | schemas.WilmsStage
            | schemas.RhabdomyosarcomaClinicalGroup
        ),
    ) -> fhir.OnconovaCancerStage:
        if obj.stagingDomain in [StagingDomain.TNM, StagingDomain.LYMPHOMA]:
            raise ValueError(
                "Lymphoma and TNM staging are handled separately in Lymphoma Stage Profile and TNM Stage Group Profile, respectively."
            )

        resource = fhir.OnconovaCancerStage.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )

        resource.code = construct_fhir_codeable_concept(
            cls.map_to_fhir("stagingDomain", obj.stagingDomain)
        )
        resource.focus = [
            Reference(
                reference=f"Condition/{conditionId}",
            )
            for conditionId in obj.stagedEntitiesIds or []
        ]
        resource.valueCodeableConcept = (
            fhir.OnconovaCancerStageValueCodeableConcept.model_validate(
                construct_fhir_codeable_concept(obj.stage).model_dump()
            )
        )
        if methodology := getattr(obj, "methodology", None):
            resource.method = construct_fhir_codeable_concept(methodology)

        if obj.stagingDomain == StagingDomain.BRESLOW:
            resource.component = [
                fhir.OnconovaCancerStageUlceration(
                    valueCodeableConcept=(
                        construct_fhir_codeable_concept(
                            Coding(
                                code="LA9633-4",
                                system="http://loinc.org",
                                display="Present",
                            )
                        )
                        if obj.isUlcered
                        else construct_fhir_codeable_concept(
                            Coding(
                                code="LA11902-6",
                                system="http://loinc.org",
                                display="Not identified",
                            )
                        )
                    ),
                ),
            ]
            resource.valueCodeableConcept.extension = [
                Extension(
                    url="https://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-stage-breslow-depth",
                    valueQuantity=Quantity(
                        value=obj.depth.value,
                        code="mm",
                        system="http://unitsofmeasure.org",
                    ),
                ),
            ]
        return resource


CancerStageProfile.register_mapping(
    "stagingDomain",
    [
        MappingRule(
            StagingDomain.FIGO,
            Coding(
                code="385361009",
                system="http://snomed.info/sct",
                display="International Federation of Gynecology and Obstetrics stage for gynecological malignancy (observable entity)",
            ),
        ),
        MappingRule(
            StagingDomain.BINET,
            Coding(
                code="C141212",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Binet Stage",
            ),
        ),
        MappingRule(
            StagingDomain.RAI,
            Coding(
                code="C141207",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Rai Stage",
            ),
        ),
        MappingRule(
            StagingDomain.BRESLOW,
            Coding(
                code="106243009",
                system="http://snomed.info/sct",
                display="Breslow depth staging for melanoma of skin (observable entity)",
            ),
        ),
        MappingRule(
            StagingDomain.CLARK,
            Coding(
                code="103419001",
                system="http://snomed.info/sct",
                display="Clark melanoma level of invasion of excised malignant melanoma of skin (observable entity)",
            ),
        ),
        MappingRule(
            StagingDomain.ISS,
            Coding(
                code="C139007",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="International Staging System Stage",
            ),
        ),
        MappingRule(
            StagingDomain.RISS,
            Coding(
                code="C139C141392007",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Revised International Staging System Stage",
            ),
        ),
        MappingRule(
            StagingDomain.INSS,
            Coding(
                code="409720004",
                system="http://snomed.info/sct",
                display="International neuroblastoma staging system stage (observable entity)",
            ),
        ),
        MappingRule(
            StagingDomain.INRGSS,
            Coding(
                code="C133427",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="International Neuroblastoma Risk Group Staging System",
            ),
        ),
        MappingRule(
            StagingDomain.GLEASON,
            Coding(
                code="385377005",
                system="http://snomed.info/sct",
                display="Gleason grade finding for prostatic cancer (finding)",
            ),
        ),
        MappingRule(
            StagingDomain.RHABDO,
            Coding(
                code="405916000",
                system="http://snomed.info/sct",
                display="Intergroup rhabdomyosarcoma study post-surgical clinical group (observable entity)",
            ),
        ),
        MappingRule(
            StagingDomain.WILMS,
            Coding(
                code="405931009",
                system="http://snomed.info/sct",
                display="National Wilms Tumor Study Group Stage (observable entity) ",
            ),
        ),
    ],
)
