from pydantic import field_validator
from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference, Coding
from fhircraft.fhir.resources.datatypes.R4.core import Observation
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import TNMStageGroup as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept

from onconova.interoperability.fhir.models.TNMPrimaryTumorCategory import (
    OnconovaTNMPrimaryTumorCategory,
)
from onconova.interoperability.fhir.models.TNMRegionalNodesCategory import (
    OnconovaTNMRegionalNodesCategory,
)
from onconova.interoperability.fhir.models.TNMDistantMetastasesCategory import (
    OnconovaTNMDistantMetastasesCategory,
)
from onconova.interoperability.fhir.models.TNMLymphaticInvasionCategory import (
    OnconovaTNMLymphaticInvasionCategory,
)
from onconova.interoperability.fhir.models.TNMResidualTumorCategory import (
    OnconovaTNMResidualTumorCategory,
)
from onconova.interoperability.fhir.models.TNMSerumTumorMarkerLevelCategory import (
    OnconovaTNMSerumTumorMarkerLevelCategory,
)
from onconova.interoperability.fhir.models.TNMGradeCategory import (
    OnconovaTNMGradeCategory,
)
from onconova.interoperability.fhir.models.TNMVenousInvasionCategory import (
    OnconovaTNMVenousInvasionCategory,
)
from onconova.interoperability.fhir.models.TNMPerineuralInvasionCategory import (
    OnconovaTNMPerineuralInvasionCategory,
)


class TNMStageGroupProfile(OnconovaFhirBaseSchema, fhir.OnconovaTNMStageGroup):

    __model__ = models.TNMStaging
    __schema__ = schemas.TNMStaging

    @field_validator("code", mode="after")
    @classmethod
    def discriminator(cls, concept: fhir.CodeableConcept) -> fhir.CodeableConcept:
        allowed_codes = ["399390009", "399537006", "399588009"]
        if (
            not concept.coding
            or not (coding := concept.coding[0])
            or coding.code not in allowed_codes
        ):
            raise ValueError(
                f"The code {coding.system}#{coding.code} is not a valid staging code discriminator"
            )
        return concept

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaTNMStageGroup
    ) -> schemas.TNMStagingCreate:
        instance = schemas.TNMStagingCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.replace('Patient/', '')"
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime"),
            methodology=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.method.coding")
            ),
            stagedEntitiesIds=obj.fhirpath_values(
                "Observation.focus.reference.replace('Condition/', '')"
            ),
            stage=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.valueCodeableConcept.coding")
            ),
            pathological=(
                True
                if (code := obj.fhirpath_single("Observation.code.coding.code"))
                == "399588009"
                else False if code == "399537006" else None
            ),
        )
        for member in obj.hasMember or []:
            if not member.reference or not "#" in member.reference:
                raise ValueError(
                    'The Observation.hasMember.reference element must be provided and be an internal reference, i.e. "#{internal_id}"'
                )
            internal_id = member.reference.lstrip("#")
            contained_resource = obj.fhirpath_single(
                f"Observation.contained.where(id='{internal_id}' and resourceType='Observation')"
            )
            if not contained_resource:
                raise RuntimeError(
                    f"Could not resolve referenced member with ID '{internal_id}' within the contained resources."
                )
            value = CodedConcept.model_validate(
                contained_resource.fhirpath_single(
                    "Observation.valueCodeableConcept.coding"
                )
            )
            code = contained_resource.fhirpath_single("Observation.code.coding.code")
            if code in ("78873005", "399504009", "384625004"):
                instance.primaryTumor = value
            elif code in ("277206009", "399534004", "371494008"):
                instance.regionalNodes = value
            elif code in ("277208005", "399387003", "371497001"):
                instance.distantMetastases = value
            elif code == "385414009":
                instance.lymphaticInvasion = value
            elif code == "396394004":
                instance.perineuralInvasion = value
            elif code == "37161004":
                instance.residualTumor = value
            elif code == "396701002":
                instance.serumTumorMarkerLevel = value
            elif code in ("1222598000", "1222599008", "1222600006"):
                instance.grade = value
            elif code == "369732007":
                instance.venousInvasion = value
        return instance

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.TNMStaging) -> fhir.OnconovaTNMStageGroup:
        resource = fhir.OnconovaTNMStageGroup.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueCodeableConcept = construct_fhir_codeable_concept(obj.stage)
        if obj.stagedEntitiesIds:
            resource.focus = Reference(
                reference=f"Condition/{obj.stagedEntitiesIds[0]}",
            )
        if obj.methodology:
            resource.method = construct_fhir_codeable_concept(obj.methodology)
        resource.code = construct_fhir_codeable_concept(
            Coding(
                code="399588009",
                system="http://snomed.info/sct",
                display="Pathologic TNM stage grouping",
            )
            if obj.pathological
            else Coding(
                code="399537006",
                system="http://snomed.info/sct",
                display="Clinical TNM stage grouping",
            )
        )
        if obj.primaryTumor:
            resource = cls.add_fhir_tnm_category(
                resource, obj.primaryTumor, OnconovaTNMPrimaryTumorCategory
            )
        if obj.regionalNodes:
            resource = cls.add_fhir_tnm_category(
                resource, obj.regionalNodes, OnconovaTNMRegionalNodesCategory
            )
        if obj.distantMetastases:
            resource = cls.add_fhir_tnm_category(
                resource, obj.distantMetastases, OnconovaTNMDistantMetastasesCategory
            )
        if obj.grade:
            resource = cls.add_fhir_tnm_category(
                resource, obj.grade, OnconovaTNMGradeCategory
            )
        if obj.residualTumor:
            resource = cls.add_fhir_tnm_category(
                resource, obj.residualTumor, OnconovaTNMResidualTumorCategory
            )
        if obj.lymphaticInvasion:
            resource = cls.add_fhir_tnm_category(
                resource, obj.lymphaticInvasion, OnconovaTNMLymphaticInvasionCategory
            )
        if obj.perineuralInvasion:
            resource = cls.add_fhir_tnm_category(
                resource, obj.perineuralInvasion, OnconovaTNMPerineuralInvasionCategory
            )
        if obj.venousInvasion:
            resource = cls.add_fhir_tnm_category(
                resource, obj.venousInvasion, OnconovaTNMVenousInvasionCategory
            )
        if obj.serumTumorMarkerLevel:
            resource = cls.add_fhir_tnm_category(
                resource,
                obj.serumTumorMarkerLevel,
                OnconovaTNMSerumTumorMarkerLevelCategory,
            )
        return resource

    @classmethod
    def add_fhir_tnm_category(
        cls, resource: fhir.OnconovaTNMStageGroup, value: CodedConcept, profile
    ):
        contained_resource = profile.model_construct()
        internal_id = profile.__name__
        # Inherit base elements from parent resource
        contained_resource.subject = resource.subject
        contained_resource.effectiveDateTime = resource.effectiveDateTime
        contained_resource.focus = resource.focus
        contained_resource.method = resource.method
        # Insert specifics
        contained_resource.id = internal_id
        contained_resource.code = construct_fhir_codeable_concept(
            cls.map_to_fhir("TNMCategories", profile)
        )
        contained_resource.valueCodeableConcept = construct_fhir_codeable_concept(value)
        # Construct internal references
        resource.contained = resource.contained or []
        resource.contained.append(contained_resource)
        resource.hasMember = resource.hasMember or []

        # Construct reference
        ref = Reference.model_construct()
        ref.reference = f"#{internal_id}"
        resource.hasMember.append(ref)
        return resource


TNMStageGroupProfile.register_mapping(
    "TNMCategories",
    [
        MappingRule(
            OnconovaTNMPrimaryTumorCategory,
            Coding(
                code="78873005", system="http://snomed.info/sct", display="T category"
            ),
        ),
        MappingRule(
            OnconovaTNMRegionalNodesCategory,
            Coding(
                code="277206009", system="http://snomed.info/sct", display="N category"
            ),
        ),
        MappingRule(
            OnconovaTNMDistantMetastasesCategory,
            Coding(
                code="277208005", system="http://snomed.info/sct", display="M category"
            ),
        ),
        MappingRule(
            OnconovaTNMLymphaticInvasionCategory,
            Coding(
                code="385414009",
                system="http://snomed.info/sct",
                display="Lymphatic (small vessel) tumor invasion finding (finding)",
            ),
        ),
        MappingRule(
            OnconovaTNMPerineuralInvasionCategory,
            Coding(
                code="396394004",
                system="http://snomed.info/sct",
                display="Perineural invasion finding (finding)",
            ),
        ),
        MappingRule(
            OnconovaTNMResidualTumorCategory,
            Coding(
                code="37161004",
                system="http://snomed.info/sct",
                display="Finding of residual tumor (finding)",
            ),
        ),
        MappingRule(
            OnconovaTNMSerumTumorMarkerLevelCategory,
            Coding(
                code="396701002",
                system="http://snomed.info/sct",
                display="Finding of serum tumor marker level (finding)",
            ),
        ),
        MappingRule(
            OnconovaTNMGradeCategory,
            Coding(
                code="1222598000",
                system="http://snomed.info/sct",
                display="American Joint Committee on Cancer clinical grade allowable value",
            ),
        ),
        MappingRule(
            OnconovaTNMVenousInvasionCategory,
            Coding(
                code="369732007",
                system="http://snomed.info/sct",
                display="Venous (large vessel) tumor invasion finding (finding)",
            ),
        ),
    ],
)
