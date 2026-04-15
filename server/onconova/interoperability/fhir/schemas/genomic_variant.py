from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Quantity,
    Coding,
)
from onconova.interoperability.fhir.schemas.base import (
    MappingRule,
    OnconovaFhirBaseSchema,
)
import re
from onconova.interoperability.fhir.models import GenomicVariant as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept
from onconova.oncology.models.genomic_variant import (
    DNAChangeType,
    GenomicVariantAssessmentChoices,
    GenomicVariantClinicalRelevanceChoices,
    GenomicVariantConfidenceChoices,
    HGVSRegex,
    ProteinChangeType,
)


class GenomicVariantProfile(OnconovaFhirBaseSchema, fhir.OnconovaGenomicVariant):

    __model__ = models.GenomicVariant
    __schema__ = schemas.GenomicVariant

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaGenomicVariant
    ) -> schemas.GenomicVariantCreate:

        if (
            version := obj.fhirpath_single(
                "Observation.component.where(code.coding.code='81303-0').valueString.getValue()"
            )
        ) != HGVSRegex.VERSION:
            raise ValueError(
                f"Unsupported HGVS version: {version}. Only version {HGVSRegex.VERSION} is supported."
            )

        return schemas.GenomicVariantCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            genes=[
                CodedConcept.model_validate(coding.model_dump())
                for coding in obj.fhirpath_values(
                    "Observation.component.where(code.coding.code='48018-6').valueCodeableConcept.coding"
                )
            ],
            assessmentDate=obj.fhirpath_single(
                "Observation.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-genomic-variant-assessment-date').valueDateTime.getValue()",
            ),
            genePanel=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='C165600').valueString.getValue()",
            ),
            dnaHgvs=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='48004-6').valueCodeableConcept.coding.code.getValue()"
            )
            or obj.fhirpath_single(
                "Observation.component.where(code.coding.code='81290-9').valueCodeableConcept.coding.code.getValue()"
            ),
            proteinHgvs=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='48005-3').valueCodeableConcept.coding.code.getValue()"
            ),
            rnaHgvs=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='rna-hgvs').valueCodeableConcept.coding.code.getValue()"
            ),
            assessment=(
                cls.map_to_internal("GenomicVariantAssessment", assessment)
                if (
                    assessment := obj.fhirpath_single(
                        "Observation.valueCodeableConcept.coding",
                    )
                )
                else None
            ),
            confidence=(
                cls.map_to_internal("Confidence", confidence)
                if (
                    confidence := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='variant-confidence-status').valueCodeableConcept.coding",
                    )
                )
                else None
            ),
            analysisMethod=(
                CodedConcept.model_validate(method.model_dump())
                if (method := obj.fhirpath_single("Observation.method.coding"))
                else None
            ),
            clinicalRelevance=(
                cls.map_to_internal("ClinicalRelevance", relevance)
                if (
                    relevance := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='LL4034-6').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            genomeAssemblyVersion=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='62374-4').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            molecularConsequence=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='molecular-consequence').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            copyNumber=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='82155-3').valueQuantity.value.getValue()"
            ),
            alleleFrequency=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='81258-6').valueQuantity.value / 100"
            ),
            alleleDepth=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='82121-5').valueQuantity.value.getValue()"
            ),
            zygosity=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='53034-5').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            source=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='48002-0').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            inheritance=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='variant-inheritance').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            coordinateSystem=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='92822-6').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            clinvar=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='81252-9').valueCodeableConcept.coding.code.getValue()"
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.GenomicVariant
    ) -> fhir.OnconovaGenomicVariant:
        resource = fhir.OnconovaGenomicVariant.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.component = [
            fhir.OnconovaGenomicVariantHgvsVersion(
                valueString=obj.hgvsVersion,
            )
        ]
        if obj.assessmentDate:
            resource.extension = [
                fhir.GenomicVariantAssessmentDate(
                    valueDateTime=obj.assessmentDate.isoformat(),
                )
            ]
        if obj.assessment:
            resource.valueCodeableConcept = construct_fhir_codeable_concept(
                cls.map_to_fhir("GenomicVariantAssessment", obj.assessment)
            )
        if obj.analysisMethod:
            resource.method = construct_fhir_codeable_concept(obj.analysisMethod)

        if obj.genePanel:
            resource.component.append(
                fhir.OnconovaGenomicVariantGenePanelSequencing(
                    valueString=obj.genePanel,
                )
            )
        for gene in obj.genes:
            resource.component.append(
                fhir.GenomicFindingGeneStudied(
                    valueCodeableConcept=construct_fhir_codeable_concept(gene),
                )
            )
        if obj.clinicalRelevance is not None:
            if coding := cls.map_to_fhir("ClinicalRelevance", obj.clinicalRelevance):
                resource.component.append(
                    fhir.OnconovaGenomicVariantClinicalRelevance(
                        valueCodeableConcept=construct_fhir_codeable_concept(coding)
                    )
                )
        if obj.cytogeneticLocation is not None:
            resource.component.append(
                fhir.GenomicFindingCytogeneticLocation(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(
                            code=obj.cytogeneticLocation,
                            system="https://iscn.karger.com",
                        )
                    )
                )
            )
        if obj.chromosomes is not None:
            resource.component.extend(
                [
                    fhir.VariantChromosomeIdentifier(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            cls.map_to_fhir("Chromosomes", chr)
                        )
                    )
                    for chr in obj.chromosomes
                ]
            )
        if obj.genomeAssemblyVersion is not None:
            resource.component.append(
                fhir.GenomicFindingReferenceSequenceAssembly(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.genomeAssemblyVersion
                    )
                )
            )
        if obj.dnaHgvs and "c." in obj.dnaHgvs:
            resource.component.append(
                fhir.VariantCodingHgvs(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(code=obj.dnaHgvs, system="http://varnomen.hgvs.org")
                    ),
                )
            )
        if obj.dnaHgvs and "g." in obj.dnaHgvs:
            resource.component.append(
                fhir.OnconovaGenomicVariantGenomicHgvs(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(code=obj.dnaHgvs, system="http://varnomen.hgvs.org")
                    ),
                )
            )
        if obj.proteinHgvs is not None:
            resource.component.append(
                fhir.VariantProteinHgvs(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(code=obj.proteinHgvs, system="http://varnomen.hgvs.org")
                    ),
                )
            )
        if obj.rnaHgvs is not None:
            resource.component.append(
                fhir.OnconovaGenomicVariantRnaHgvs(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(code=obj.rnaHgvs, system="http://varnomen.hgvs.org")
                    ),
                )
            )
        if obj.dnaReferenceSequence is not None:
            if re.search(
                rf"{HGVSRegex.GENOMIC_REFSEQ}",
                obj.dnaReferenceSequence,
            ):
                component = fhir.VariantGenomicRefSeq
            else:
                component = fhir.VariantTranscriptRefSeq
            resource.component.append(
                component(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(
                            code=obj.dnaReferenceSequence,
                            system="http://www.ncbi.nlm.nih.gov/refseq",
                        )
                    )
                )
            )
        if obj.coordinateSystem is not None:
            resource.component.append(
                fhir.VariantCoordinateSystem(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.coordinateSystem
                    )
                )
            )
        if obj.dnaChangeType is not None:
            mapped_code = cls.map_to_fhir("CodingChangeType", obj.dnaChangeType)
            if mapped_code is not None:
                resource.component.append(
                    fhir.VariantCodingChangeType(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            mapped_code
                        )
                    )
                )
        if obj.proteinChangeType is not None:
            mapped_code = cls.map_to_fhir("AminoAcidChangeType", obj.proteinChangeType)
            if mapped_code is not None:
                resource.component.append(
                    fhir.VariantAminoAcidChangeType(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            mapped_code
                        )
                    )
                )
        if obj.molecularConsequence is not None:
            resource.component.append(
                fhir.VariantMolecularConsequence(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.molecularConsequence
                    )
                )
            )
        if obj.confidence is not None:
            resource.component.append(
                fhir.VariantVariantConfidenceStatus(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        cls.map_to_fhir("Confidence", obj.confidence)
                    )
                )
            )
        if obj.zygosity is not None:
            resource.component.append(
                fhir.VariantAllelicState(
                    valueCodeableConcept=construct_fhir_codeable_concept(obj.zygosity)
                )
            )
        if obj.inheritance is not None:
            resource.component.append(
                fhir.VariantVariantInheritance(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.inheritance
                    )
                )
            )
        if obj.alleleDepth is not None:
            resource.component.append(
                fhir.VariantAllelicReadDepth(
                    valueQuantity=Quantity(
                        value=obj.alleleDepth,
                        code="{reads}",
                        system="http://unitsofmeasure.org",
                        unit="reads",
                    ),
                )
            )
        if obj.alleleFrequency is not None:
            resource.component.append(
                fhir.VariantSampleAllelicFrequency(
                    valueQuantity=fhir.VariantValueQuantity(
                        value=obj.alleleFrequency * 100,
                        code="%",
                        system="http://unitsofmeasure.org",
                    ),
                )
            )
        if obj.source is not None:
            resource.component.append(
                fhir.GenomicVariantGenomicSourceClass(
                    valueCodeableConcept=construct_fhir_codeable_concept(obj.source)
                )
            )
        if obj.copyNumber is not None:
            resource.component.append(
                fhir.VariantCopyNumber(
                    valueQuantity=Quantity(
                        value=obj.copyNumber,
                        code="{copies}",
                        system="http://unitsofmeasure.org",
                        unit="copies",
                    ),
                )
            )
        if obj.nucleotidesLength is not None:
            resource.component.append(
                fhir.OnconovaGenomicVariantNucleotidesCount(
                    valueInteger=obj.nucleotidesLength,
                )
            )
        if obj.regions is not None:
            resource.component.extend(
                [
                    fhir.OnconovaGenomicVariantGeneRegion(valueString=region)
                    for region in obj.regions
                ]
            )
        if obj.clinvar is not None:
            resource.component.append(
                fhir.GenomicVariantVariationCode(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(
                            code=obj.clinvar,
                            system="https://www.ncbi.nlm.nih.gov/clinvar",
                        )
                    )
                )
            )
        return resource


GenomicVariantProfile.register_mapping(
    "ClinicalRelevance",
    [
        MappingRule(
            GenomicVariantClinicalRelevanceChoices.PATHOGENIC,
            Coding(
                code="LA6668-3",
                system="http://loinc.org",
                display="Pathogenic",
            ),
        ),
        MappingRule(
            GenomicVariantClinicalRelevanceChoices.LIKELY_PATHOGENIC,
            Coding(
                code="LA26332-9",
                system="http://loinc.org",
                display="Likely pathogenic",
            ),
        ),
        MappingRule(
            GenomicVariantClinicalRelevanceChoices.UNCERTAIN_SIGNIFICANCE,
            Coding(
                code="LA26333-7",
                system="http://loinc.org",
                display="Uncertain significance",
            ),
        ),
        MappingRule(
            GenomicVariantClinicalRelevanceChoices.AMBIGUOUS,
            Coding(
                code="C70429",
                display="Ambiguity",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
            ),
        ),
        MappingRule(
            GenomicVariantClinicalRelevanceChoices.LIKELY_BENIGN,
            Coding(
                code="LA26334-5",
                system="http://loinc.org",
                display="Likely benign",
            ),
        ),
        MappingRule(
            GenomicVariantClinicalRelevanceChoices.BENIGN,
            Coding(
                code="LA6675-8",
                system="http://loinc.org",
                display="Benign",
            ),
        ),
    ],
)

GenomicVariantProfile.register_mapping(
    "Confidence",
    [
        MappingRule(
            GenomicVariantConfidenceChoices.HIGH,
            Coding(
                code="high",
                display="High",
                system="http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/variant-confidence-status-cs",
            ),
        ),
        MappingRule(
            GenomicVariantConfidenceChoices.LOW,
            Coding(
                code="low",
                display="Low",
                system="http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/variant-confidence-status-cs",
            ),
        ),
        MappingRule(
            GenomicVariantConfidenceChoices.INDETERMINATE,
            Coding(
                code="intermediate",
                display="Intermediate",
                system="http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/variant-confidence-status-cs",
            ),
        ),
    ],
)

GenomicVariantProfile.register_mapping(
    "GenomicVariantAssessment",
    [
        MappingRule(
            GenomicVariantAssessmentChoices.PRESENT,
            Coding(code="LA9633-4", display="Present", system="http://loinc.org"),
        ),
        MappingRule(
            GenomicVariantAssessmentChoices.ABSENT,
            Coding(code="LA9634-2", display="Absent", system="http://loinc.org"),
        ),
        MappingRule(
            GenomicVariantAssessmentChoices.NOCALL,
            Coding(code="LA18198-4", display="No call", system="http://loinc.org"),
        ),
        MappingRule(
            GenomicVariantAssessmentChoices.INDETERMINATE,
            Coding(
                code="LA11884-6", display="Indeterminate", system="http://loinc.org"
            ),
        ),
    ],
)


GenomicVariantProfile.register_mapping(
    "Chromosomes",
    [
        MappingRule(
            "1",
            Coding(code="LA21254-0", system="http://loinc.org", display="Chromosome 1"),
        ),
        MappingRule(
            "2",
            Coding(code="LA21255-7", system="http://loinc.org", display="Chromosome 2"),
        ),
        MappingRule(
            "3",
            Coding(code="LA21256-5", system="http://loinc.org", display="Chromosome 3"),
        ),
        MappingRule(
            "4",
            Coding(code="LA21257-3", system="http://loinc.org", display="Chromosome 4"),
        ),
        MappingRule(
            "5",
            Coding(code="LA21258-1", system="http://loinc.org", display="Chromosome 5"),
        ),
        MappingRule(
            "6",
            Coding(code="LA21259-9", system="http://loinc.org", display="Chromosome 6"),
        ),
        MappingRule(
            "7",
            Coding(code="LA21260-7", system="http://loinc.org", display="Chromosome 7"),
        ),
        MappingRule(
            "8",
            Coding(code="LA21261-5", system="http://loinc.org", display="Chromosome 8"),
        ),
        MappingRule(
            "9",
            Coding(code="LA21262-3", system="http://loinc.org", display="Chromosome 9"),
        ),
        MappingRule(
            "10",
            Coding(
                code="LA21263-1", system="http://loinc.org", display="Chromosome 10"
            ),
        ),
        MappingRule(
            "11",
            Coding(
                code="LA21264-9", system="http://loinc.org", display="Chromosome 11"
            ),
        ),
        MappingRule(
            "12",
            Coding(
                code="LA21265-6", system="http://loinc.org", display="Chromosome 12"
            ),
        ),
        MappingRule(
            "13",
            Coding(
                code="LA21266-4", system="http://loinc.org", display="Chromosome 13"
            ),
        ),
        MappingRule(
            "14",
            Coding(
                code="LA21267-2", system="http://loinc.org", display="Chromosome 14"
            ),
        ),
        MappingRule(
            "15",
            Coding(
                code="LA21268-0", system="http://loinc.org", display="Chromosome 15"
            ),
        ),
        MappingRule(
            "16",
            Coding(
                code="LA21269-8", system="http://loinc.org", display="Chromosome 16"
            ),
        ),
        MappingRule(
            "17",
            Coding(
                code="LA21270-6", system="http://loinc.org", display="Chromosome 17"
            ),
        ),
        MappingRule(
            "18",
            Coding(
                code="LA21271-4", system="http://loinc.org", display="Chromosome 18"
            ),
        ),
        MappingRule(
            "19",
            Coding(
                code="LA21272-2", system="http://loinc.org", display="Chromosome 19"
            ),
        ),
        MappingRule(
            "20",
            Coding(
                code="LA21273-0", system="http://loinc.org", display="Chromosome 20"
            ),
        ),
        MappingRule(
            "21",
            Coding(
                code="LA21274-8", system="http://loinc.org", display="Chromosome 21"
            ),
        ),
        MappingRule(
            "22",
            Coding(
                code="LA21275-5", system="http://loinc.org", display="Chromosome 22"
            ),
        ),
        MappingRule(
            "X",
            Coding(code="LA21276-3", system="http://loinc.org", display="Chromosome X"),
        ),
        MappingRule(
            "Y",
            Coding(code="LA21277-1", system="http://loinc.org", display="Chromosome Y"),
        ),
    ],
)

GenomicVariantProfile.register_mapping(
    "CodingChangeType",
    [
        MappingRule(
            DNAChangeType.SUBSTITUTION,
            Coding(
                code="SO:1000002",
                system="http://www.sequenceontology.org",
                display="substitution",
            ),
        ),
        MappingRule(
            DNAChangeType.DELETION_INSERTION,
            Coding(
                code="SO:1000032",
                system="http://www.sequenceontology.org",
                display="delins",
            ),
        ),
        MappingRule(
            DNAChangeType.INSERTION,
            Coding(
                code="SO:0000667",
                system="http://www.sequenceontology.org",
                display="insertion",
            ),
        ),
        MappingRule(
            DNAChangeType.DELETION,
            Coding(
                code="SO:0000159",
                system="http://www.sequenceontology.org",
                display="deletion",
            ),
        ),
        MappingRule(
            DNAChangeType.DUPLICATION,
            Coding(
                code="SO:1000035",
                system="http://www.sequenceontology.org",
                display="duplication",
            ),
        ),
        MappingRule(
            DNAChangeType.INVERSION,
            Coding(
                code="SO:1000036",
                system="http://www.sequenceontology.org",
                display="inversion",
            ),
        ),
        MappingRule(
            DNAChangeType.UNCHANGED,
            Coding(
                code="SO:0002073",
                system="http://www.sequenceontology.org",
                display="no_sequence_alteration",
            ),
        ),
        MappingRule(
            DNAChangeType.REPETITION,
            Coding(
                code="SO:0002096",
                system="http://www.sequenceontology.org",
                display="short_tandem_repeat_variation",
            ),
        ),
        MappingRule(
            DNAChangeType.TRANSLOCATION,
            Coding(
                code="SO:0000199",
                system="http://www.sequenceontology.org",
                display="translocation",
            ),
        ),
        MappingRule(
            DNAChangeType.TRANSPOSITION,
            Coding(
                code="SO:0000453",
                system="http://www.sequenceontology.org",
                display="transposition",
            ),
        ),
        MappingRule(DNAChangeType.METHYLATION_GAIN, None),
        MappingRule(DNAChangeType.METHYLATION_LOSS, None),
        MappingRule(DNAChangeType.METHYLATION_UNCHANGED, None),
    ],
)

GenomicVariantProfile.register_mapping(
    "AminoAcidChangeType",
    [
        MappingRule(
            ProteinChangeType.MISSENSE,
            Coding(
                code="LA6698-0",
                system="http://loinc.org",
                display="Missense",
            ),
        ),
        MappingRule(
            ProteinChangeType.NONSENSE,
            Coding(
                code="LA6699-8",
                system="http://loinc.org",
                display="Nonsense",
            ),
        ),
        MappingRule(
            ProteinChangeType.DELETION_INSERTION,
            Coding(
                code="LA9659-9",
                system="http://loinc.org",
                display="Insertion and Deletion",
            ),
        ),
        MappingRule(
            ProteinChangeType.INSERTION,
            Coding(
                code="LA6687-3",
                system="http://loinc.org",
                display="Insertion",
            ),
        ),
        MappingRule(
            ProteinChangeType.DELETION,
            Coding(
                code="LA6692-3",
                system="http://loinc.org",
                display="Deletion",
            ),
        ),
        MappingRule(
            ProteinChangeType.DUPLICATION,
            Coding(
                code="LA6686-5",
                system="http://loinc.org",
                display="Duplication",
            ),
        ),
        MappingRule(
            ProteinChangeType.FRAMESHIFT,
            Coding(
                code="LA6694-9",
                system="http://loinc.org",
                display="Frameshift",
            ),
        ),
        MappingRule(
            ProteinChangeType.EXTENSION,
            Coding(
                code="LA6701-2",
                system="http://loinc.org",
                display="Stop Codon Mutation",
            ),
        ),
        MappingRule(
            ProteinChangeType.SILENT,
            Coding(
                code="LA6700-4",
                system="http://loinc.org",
                display="Silent",
            ),
        ),
        MappingRule(
            ProteinChangeType.NO_PROTEIN,
            Coding(
                code="SO:0002395",
                system="http://sequenceontology.org",
                display="lost_polypeptide",
            ),
        ),
        MappingRule(ProteinChangeType.UNKNOWN, None),
        MappingRule(
            ProteinChangeType.REPETITION,
            Coding(
                code="SO:0001068",
                system="http://sequenceontology.org",
                display="polypeptide_repeat",
            ),
        ),
    ],
)
