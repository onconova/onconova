from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Coding,
    CodeableConcept,
)
from onconova.interoperability.fhir.schemas.base import (
    MappingRule,
    OnconovaFhirBaseSchema,
)
from onconova.interoperability.fhir.models import TumorMarker as fhir
from onconova.interoperability.fhir.utils import ucum_to_internal, internal_to_ucum
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept, Measure
from onconova.oncology.models.tumor_marker import (
    AnalyteResultType,
)


class TumorMarkerProfile(OnconovaFhirBaseSchema, fhir.OnconovaTumorMarker):

    __model__ = models.TumorMarker
    __schema__ = schemas.TumorMarker

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaTumorMarker
    ) -> schemas.TumorMarkerCreate:
        map = cls.map_to_internal(
            "tumorMarkerTestCode", obj.fhirpath_single("Observation.code.coding")
        )
        result_type = map.get("result_type")
        return schemas.TumorMarkerCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single("Observation.subject.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime"),
            analyte=CodedConcept.model_validate(
                obj.fhirpath_single(
                    "Observation.code.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-tumor-marker-analyte').valueCodeableConcept.coding"
                )
            ),
            relatedEntitiesIds=[
                ref.replace("Condition/", "")
                for ref in obj.fhirpath_values(
                    "Observation.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-related-condition').valueReference.reference"
                )
            ],
            massConcentration=(
                Measure(
                    value=(
                        quantity := obj.fhirpath_single("Observation.valueQuantity")
                    ).value,
                    unit=ucum_to_internal(quantity.code),
                )
                if result_type == AnalyteResultType.mass_concentration
                else None
            ),
            arbitraryConcentration=(
                Measure(
                    value=(
                        quantity := obj.fhirpath_single("Observation.valueQuantity")
                    ).value,
                    unit=ucum_to_internal(quantity.code),
                )
                if result_type == AnalyteResultType.arbitary_concentration
                else None
            ),
            substanceConcentration=(
                Measure(
                    value=(
                        quantity := obj.fhirpath_single("Observation.valueQuantity")
                    ).value,
                    unit=ucum_to_internal(quantity.code),
                )
                if result_type == AnalyteResultType.substance_concentration
                else None
            ),
            fraction=(
                Measure(
                    value=(
                        quantity := obj.fhirpath_single("Observation.valueQuantity")
                    ).value,
                    unit=ucum_to_internal(quantity.code),
                )
                if result_type == AnalyteResultType.fraction
                else None
            ),
            multipleOfMedian=(
                Measure(
                    value=(
                        quantity := obj.fhirpath_single("Observation.valueQuantity")
                    ).value,
                    unit=ucum_to_internal(quantity.code),
                )
                if result_type == AnalyteResultType.multiple_of_median
                else None
            ),
            tumorProportionScore=(
                obj.fhirpath_single("Observation.valueString")
                if result_type == AnalyteResultType.tumor_proportion_score
                else None
            ),
            immuneCellScore=(
                obj.fhirpath_single("Observation.valueString")
                if result_type == AnalyteResultType.immmune_cells_score
                else None
            ),
            combinedPositiveScore=(
                Measure(
                    value=(
                        quantity := obj.fhirpath_single("Observation.valueQuantity")
                    ).value,
                    unit=ucum_to_internal(quantity.code),
                )
                if result_type == AnalyteResultType.combined_positive_score
                else None
            ),
            immunohistochemicalScore=(
                obj.fhirpath_single("Observation.valueString")
                if result_type == AnalyteResultType.immunohistochemical_score
                else None
            ),
            presence=(
                obj.fhirpath_single("Observation.valueString")
                if result_type == AnalyteResultType.presence
                else None
            ),
            nuclearExpressionStatus=(
                obj.fhirpath_single("Observation.valueString")
                if result_type == AnalyteResultType.nuclear_expression_status
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.TumorMarker) -> fhir.OnconovaTumorMarker:
        resource: fhir.OnconovaTumorMarker = fhir.OnconovaTumorMarker.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.extension = resource.extension or []
        for cond_id in obj.relatedEntitiesIds or []:
            resource.extension.append(
                fhir.RelatedCondition(
                    valueReference=Reference(reference=f"Condition/{cond_id}")
                )
            )

        if obj.massConcentration:
            result_type = AnalyteResultType.mass_concentration
            resource.valueQuantity = fhir.Quantity(
                value=obj.massConcentration.value,
                code=internal_to_ucum(obj.massConcentration.unit),
                system="http://unitsofmeasure.org",
            )
        elif obj.arbitraryConcentration:
            result_type = AnalyteResultType.arbitary_concentration
            resource.valueQuantity = fhir.Quantity(
                value=obj.arbitraryConcentration.value,
                code=internal_to_ucum(obj.arbitraryConcentration.unit),
                system="http://unitsofmeasure.org",
            )
        elif obj.substanceConcentration:
            result_type = AnalyteResultType.substance_concentration
            resource.valueQuantity = fhir.Quantity(
                value=obj.substanceConcentration.value,
                code=internal_to_ucum(obj.substanceConcentration.unit),
                system="http://unitsofmeasure.org",
            )
        elif obj.multipleOfMedian:
            result_type = AnalyteResultType.multiple_of_median
            resource.valueQuantity = fhir.Quantity(
                value=obj.multipleOfMedian.value,
                code=internal_to_ucum(obj.multipleOfMedian.unit),
                system="http://unitsofmeasure.org",
            )
        elif obj.fraction:
            result_type = AnalyteResultType.fraction
            resource.valueQuantity = fhir.Quantity(
                value=obj.fraction.value,
                code=internal_to_ucum(obj.fraction.unit),
                system="http://unitsofmeasure.org",
            )
        elif obj.presence:
            result_type = AnalyteResultType.presence
            resource.valueString = obj.presence
        elif obj.combinedPositiveScore:
            result_type = AnalyteResultType.combined_positive_score
            resource.valueQuantity = fhir.Quantity(
                value=obj.combinedPositiveScore.value,
                code=internal_to_ucum(obj.combinedPositiveScore.unit),
                system="http://unitsofmeasure.org",
            )
        elif obj.immuneCellScore:
            result_type = AnalyteResultType.immmune_cells_score
            resource.valueString = obj.immuneCellScore
        elif obj.tumorProportionScore:
            result_type = AnalyteResultType.tumor_proportion_score
            resource.valueString = obj.tumorProportionScore
        elif obj.immunohistochemicalScore:
            result_type = AnalyteResultType.immunohistochemical_score
            resource.valueString = obj.immunohistochemicalScore
        elif obj.nuclearExpressionStatus:
            result_type = AnalyteResultType.nuclear_expression_status
            resource.valueString = obj.nuclearExpressionStatus
        else:
            result_type = None

        resource.code = fhir.OnconovaTumorMarkerCode(
            coding=[
                (
                    cls.map_to_fhir(
                        "tumorMarkerTestCode",
                        dict(code=obj.analyte.code, result_type=result_type),
                    )
                    if result_type
                    else Coding(
                        code="",
                        display="Tumor marker Cancer",
                        system="http://loinc.org",
                    )
                )
            ]
        )
        resource.code.extension = [
            fhir.TumorMarkerAnalyte(
                valueCodeableConcept=CodeableConcept(
                    coding=[Coding.model_validate(obj.analyte.model_dump())]
                )
            )
        ]

        return resource


TumorMarkerProfile.register_mapping(
    "tumorMarkerTestCode",
    [
        # Carcinoembryonic Antigen (CEA)
        MappingRule(
            dict(code="LP28643-2", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="2039-6",
                system="http://loinc.org",
                display="Carcinoembryonic Ag [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP28643-2", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="19166-8",
                system="http://loinc.org",
                display="Carcinoembryonic Ag [Units/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP28643-2", result_type=AnalyteResultType.substance_concentration
            ),
            Coding(
                code="19167-6",
                system="http://loinc.org",
                display="Carcinoembryonic Ag [Moles/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 125 (CA125)
        MappingRule(
            dict(
                code="LP14543-0", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="10334-1",
                system="http://loinc.org",
                display="Cancer Ag 125 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 15-3 (CA15-3)
        MappingRule(
            dict(
                code="LP15461-4", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="6875-9",
                system="http://loinc.org",
                display="Cancer Ag 15-3 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 19-9 (CA19-9)
        MappingRule(
            dict(
                code="LP14040-7", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="24108-3",
                system="http://loinc.org",
                display="Cancer Ag 19-9 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 242 (CA242)
        MappingRule(
            dict(
                code="LP15463-0", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="2011-5",
                system="http://loinc.org",
                display="Cancer Ag 242 [Presence] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 27-29 (CA27-29)
        MappingRule(
            dict(
                code="LP15464-8", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="17842-6",
                system="http://loinc.org",
                display="Cancer Ag 27-29 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 50 (CA50)
        MappingRule(
            dict(
                code="LP15465-5", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="34256-8",
                system="http://loinc.org",
                display="Cancer Ag 50 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 549 (CA549)
        MappingRule(
            dict(
                code="LP15466-3", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="19189-0",
                system="http://loinc.org",
                display="Cancer Ag 549 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen 72-4 (CA72-4)
        MappingRule(
            dict(
                code="LP15467-1", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="17843-4",
                system="http://loinc.org",
                display="Cancer Ag 72-4 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer Antigen DM/70K (CA DM/70K)
        MappingRule(
            dict(code="LP18274-", result_type=AnalyteResultType.arbitary_concentration),
            Coding(
                code="13127-6",
                system="http://loinc.org",
                display="Cancer Ag DM/70K [Units/volume] in Serum or Plasma",
            ),
        ),
        # Cancer-associated Serum Ag (CASA)
        MappingRule(
            dict(
                code="LP28642-4", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="24474-9",
                system="http://loinc.org",
                display="Cancer associated serum Ag [Units/volume] in Serum",
            ),
        ),
        # Circulating tumor cells (CTC)
        MappingRule(
            dict(
                code="LP135291-5", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="C96593",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Circulating Tumor Cell Count",
            ),
        ),
        # Fibroblast growth factor 2 (FGF-2)
        MappingRule(
            dict(code="LP428253-1", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="98117-5",
                system="http://loinc.org",
                display="Fibroblast growth factor 2 [Mass/volume] in Serum or Plasma",
            ),
        ),
        # Fibroblast growth factor 21 (FGF-21)
        MappingRule(
            dict(code="LP263758-7", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="87832-2",
                system="http://loinc.org",
                display="Fibroblast growth factor 21.intact [Mass/volume] in Serum or Plasma",
            ),
        ),
        # Fibroblast growth factor 23 (FGF-23)
        MappingRule(
            dict(
                code="LP40488-6", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="46699-5",
                system="http://loinc.org",
                display="Fibroblast growth factor 23 [Units/volume] in Plasma",
            ),
        ),
        MappingRule(
            dict(code="LP40488-6", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="54390-0",
                system="http://loinc.org",
                display="Fibroblast growth factor 23.intact [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(code="LP40488-6", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="104259-7",
                system="http://loinc.org",
                display="Fibroblast growth factor 23 [Presence] in Tissue by FISH",
            ),
        ),
        # Gastrin releasing polypeptide prohormone (GRP)
        MappingRule(
            dict(code="LP420752-0", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="96461-9",
                system="http://loinc.org",
                display="Gastrin releasing polypeptide prohormone [Mass/volume] in Serum or Plasma by Immunoassay",
            ),
        ),
        # Tumor necrosis factor binding protein 1 (TNFBP1)
        MappingRule(
            dict(
                code="LP89249-4", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="54165-6",
                system="http://loinc.org",
                display="Tumor necrosis factor binding protein [Units/volume] in Serum",
            ),
        ),
        # Chitinase-3-like protein 1 (TKL-40)
        MappingRule(
            dict(code="LP62856-7", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="48663-9",
                system="http://loinc.org",
                display="YKL-40 [Mass/volume] in Serum",
            ),
        ),
        # Neuron-specific enolase (NSE)
        MappingRule(
            dict(code="LP38032-6", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="15060-7",
                system="http://loinc.org",
                display="Enolase.neuron specific [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP38032-6", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="19193-2",
                system="http://loinc.org",
                display="Enolase.neuron specific [Units/volume] in Serum or Plasma",
            ),
        ),
        # Lactate dehydrogenase (LDH)
        MappingRule(
            dict(
                code="LP15033-1", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="2532-0",
                system="http://loinc.org",
                display="Lactate dehydrogenase [Enzymatic activity/volume] in Serum or Plasma",
            ),
        ),
        # Chromogranin A (CgA)
        MappingRule(
            dict(code="LP14652-9", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="9811-1",
                system="http://loinc.org",
                display="Chromogranin A [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP14652-9", result_type=AnalyteResultType.substance_concentration
            ),
            Coding(
                code="25587-7",
                system="http://loinc.org",
                display="Chromogranin A [Moles/volume] in Serum or Plasma",
            ),
        ),
        # S100 calcium binding protein B (S100B)
        MappingRule(
            dict(code="LP57672-5", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="47275-3",
                system="http://loinc.org",
                display="S100 calcium binding protein B [Mass/volume] in Serum",
            ),
        ),
        # Prostate specific Ag (PSA)
        MappingRule(
            dict(
                code="LP18193-0", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="19195-7",
                system="http://loinc.org",
                display="Prostate specific Ag [Units/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(code="LP18193-0", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="2857-1",
                system="http://loinc.org",
                display="Prostate specific Ag [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP18193-0", result_type=AnalyteResultType.substance_concentration
            ),
            Coding(
                code="19197-3",
                system="http://loinc.org",
                display="Prostate specific Ag [Moles/volume] in Serum or Plasma",
            ),
        ),
        # Alpha-1-Fetoprotein (AFP)
        MappingRule(
            dict(code="LP14331-0", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="1834-1",
                system="http://loinc.org",
                display="Alpha-1-Fetoprotein [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP14331-0", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="19176-7",
                system="http://loinc.org",
                display="Alpha-1-Fetoprotein [Units/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP14331-0", result_type=AnalyteResultType.substance_concentration
            ),
            Coding(
                code="19177-5",
                system="http://loinc.org",
                display="Alpha-1-Fetoprotein [Moles/volume] in Serum or Plasma",
            ),
        ),
        # Choriogonadotropin subunit β (β-hCG)
        MappingRule(
            dict(code="LP14329-4", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="55869-2",
                system="http://loinc.org",
                display="Choriogonadotropin.beta subunit [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP14329-4", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="21198-7",
                system="http://loinc.org",
                display="Choriogonadotropin.beta subunit [Units/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP14329-4", result_type=AnalyteResultType.substance_concentration
            ),
            Coding(
                code="2111-3",
                system="http://loinc.org",
                display="Choriogonadotropin.beta subunit [Moles/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(code="LP14329-4", result_type=AnalyteResultType.multiple_of_median),
            Coding(
                code="55868-4",
                system="http://loinc.org",
                display="Choriogonadotropin.beta subunit [Multiple of the median] in Serum or Plasma",
            ),
        ),
        # Cytokeratin 19 Fragment (CYFRA 21-1)
        MappingRule(
            dict(code="LP19423-0", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="25390-6",
                system="http://loinc.org",
                display="Cytokeratin 19 [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP19423-0", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="19182-5",
                system="http://loinc.org",
                display="Cytokeratin 19 [Units/volume] in Serum or Plasma",
            ),
        ),
        # Human epididymis protein 4 (HE4)
        MappingRule(
            dict(code="LP93517-8", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="96044-3",
                system="http://loinc.org",
                display="Human epididymis protein 4 [Mass/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(
                code="LP93517-8", result_type=AnalyteResultType.substance_concentration
            ),
            Coding(
                code="55180-4",
                system="http://loinc.org",
                display="Human epididymis protein 4 [Moles/volume] in Serum or Plasma",
            ),
        ),
        # Melanin (Mel)
        MappingRule(
            dict(
                code="LP15724-5", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="17248-6",
                system="http://loinc.org",
                display="Melanin [Units/volume] in Serum or Plasma",
            ),
        ),
        MappingRule(
            dict(code="LP15724-5", result_type=AnalyteResultType.mass_concentration),
            Coding(
                code="2607-0",
                system="http://loinc.org",
                display="Melanin [Mass/volume] in Urine",
            ),
        ),
        # Epstein Barr Virus Ab (EBV Ab)
        MappingRule(
            dict(
                code="LP38066-4", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="13238-1",
                system="http://loinc.org",
                display="Epstein Barr virus Ab [Units/volume] in Serum",
            ),
        ),
        MappingRule(
            dict(code="LP38066-4", result_type=AnalyteResultType.presence),
            Coding(
                code="49178-7",
                system="http://loinc.org",
                display="Epstein Barr virus Ab [Presence] in Serum",
            ),
        ),
        # Programmed cell death ligand 1 (PDL1)
        MappingRule(
            dict(code="LP220351-3", result_type=AnalyteResultType.immmune_cells_score),
            Coding(
                code="C199175",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="PD-L1 Immune Cell Score",
            ),
        ),
        MappingRule(
            dict(
                code="LP220351-3", result_type=AnalyteResultType.tumor_proportion_score
            ),
            Coding(
                code="C184941",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="PD-L1 Tumor Proportion Score",
            ),
        ),
        MappingRule(
            dict(
                code="LP220351-3", result_type=AnalyteResultType.combined_positive_score
            ),
            Coding(
                code="C176582",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="PD-L1 Combined Positive Score",
            ),
        ),
        # Human Epidermal Growth Factor Receptor 2 (HER2)
        MappingRule(
            dict(code="LP28442-9", result_type=AnalyteResultType.presence),
            Coding(
                code="72383-3",
                system="http://loinc.org",
                display="HER2 [Presence] in Tissue by Immunoassay",
            ),
        ),
        MappingRule(
            dict(
                code="LP28442-9",
                result_type=AnalyteResultType.immunohistochemical_score,
            ),
            Coding(
                code="C185751",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="HER2/Neu Status by Immunohistochemistry",
            ),
        ),
        # Estrogen receptor (ER)
        MappingRule(
            dict(code="LP18567-5", result_type=AnalyteResultType.fraction),
            Coding(
                code="14228-1",
                system="http://loinc.org",
                display="Cells.estrogen receptor/cells in Tissue by Immune stain",
            ),
        ),
        # Progesterone receptor (PR)
        MappingRule(
            dict(code="LP14902-8", result_type=AnalyteResultType.fraction),
            Coding(
                code="14230-7",
                system="http://loinc.org",
                display="Cells.progesterone receptor/cells in Tissue by Immune stain",
            ),
        ),
        # Androgen receptor (AR)
        MappingRule(
            dict(code="LP68364-6", result_type=AnalyteResultType.fraction),
            Coding(
                code="C157165",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="AR Status by Immunohistochemistry",
            ),
        ),
        # Ki-67 nuclear Ag (Ki67)
        MappingRule(
            dict(code="LP39016-8", result_type=AnalyteResultType.fraction),
            Coding(
                code="29593-1",
                system="http://loinc.org",
                display="Cells.Ki-67 nuclear Ag/cells in Tissue by Immune stain",
            ),
        ),
        # DNA mismatch repair protein MLH3 (MLH3)
        MappingRule(
            dict(
                code="LP420961-7",
                result_type=AnalyteResultType.nuclear_expression_status,
            ),
            Coding(
                code="96272-0",
                system="http://loinc.org",
                display="DNA mismatch repair protein Mlh3 [Presence] in Cancer specimen by Immune stain",
            ),
        ),
        # DNA mismatch repair protein MLH1 (MLH1)
        MappingRule(
            dict(
                code="LP212189-7",
                result_type=AnalyteResultType.nuclear_expression_status,
            ),
            Coding(
                code="81691-8",
                system="http://loinc.org",
                display="DNA mismatch repair protein Mlh1 [Presence] in Cancer specimen by Immune stain",
            ),
        ),
        # DNA mismatch repair protein MSH2 (MSH2)
        MappingRule(
            dict(
                code="LP212190-5",
                result_type=AnalyteResultType.nuclear_expression_status,
            ),
            Coding(
                code="81692-6",
                system="http://loinc.org",
                display="DNA mismatch repair protein Msh2 [Presence] in Cancer specimen by Immune stain",
            ),
        ),
        # DNA mismatch repair protein MSH6 (MSH6)
        MappingRule(
            dict(
                code="LP212191-3",
                result_type=AnalyteResultType.nuclear_expression_status,
            ),
            Coding(
                code="81693-4",
                system="http://loinc.org",
                display="DNA mismatch repair protein Msh6 [Presence] in Cancer specimen by Immune stain",
            ),
        ),
        # Mismatch repair endonuclease PMS2 (PMS2)
        MappingRule(
            dict(
                code="LP212192-1",
                result_type=AnalyteResultType.nuclear_expression_status,
            ),
            Coding(
                code="81694-2",
                system="http://loinc.org",
                display="Mismatch repair endonuclease PMS2 [Presence] in Cancer specimen by Immune stain",
            ),
        ),
        # Cyclin-dependent Kinase Inhibitor 2A (p16)
        MappingRule(
            dict(code="LP19646-6", result_type=AnalyteResultType.presence),
            Coding(
                code="21614-3",
                system="http://loinc.org",
                display="CDKN2A gene deletion [Presence] in Blood or Tissue by Molecular genetics method",
            ),
        ),
        # Human papilloma virus DNA (HPV DNA)
        MappingRule(
            dict(code="LP38570-5", result_type=AnalyteResultType.presence),
            Coding(
                code="105077-2",
                system="http://loinc.org",
                display="Human papilloma virus DNA [Presence] in Specimen",
            ),
        ),
        # Epstein Barr Virus DNA (EBV DNA)
        MappingRule(
            dict(code="LP38067-2", result_type=AnalyteResultType.presence),
            Coding(
                code="5003-9",
                system="http://loinc.org",
                display="Epstein Barr virus DNA [Presence] in Tissue by Probe",
            ),
        ),
        MappingRule(
            dict(
                code="LP38067-2", result_type=AnalyteResultType.arbitary_concentration
            ),
            Coding(
                code="108217-1",
                system="http://loinc.org",
                display="Epstein Barr virus DNA [Units/volume] (viral load) in Specimen by NAA with probe detection",
            ),
        ),
        # Somatostatin Receptor Type 2 (SSTR2)
        MappingRule(
            dict(code="C17922", result_type=AnalyteResultType.fraction),
            Coding(
                code="C165984",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Somatostatin Receptor Type 2 Measurement",
            ),
        ),
    ],
)
