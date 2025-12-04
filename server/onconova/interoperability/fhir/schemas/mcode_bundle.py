from datetime import datetime
from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference, Coding
from fhircraft.fhir.resources.datatypes.R4.core import Bundle, BundleEntry
from onconova.interoperability.fhir import schemas as profiles
from onconova.interoperability.fhir.models import LymphomaStage as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept


class BundleProfile(Bundle):

    @classmethod
    def construct_bundle(cls, case: models.PatientCase) -> "BundleProfile":
        bundle = BundleProfile(
            type="collection",
            timestamp=datetime.now().isoformat(),
        )
        bundle.entry = [
            BundleEntry(resource=profiles.CancerPatientProfile.model_validate(case))
        ]
        for condition in case.neoplastic_entities.all():  # type: ignore
            if condition.relationship == "metastatic":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.SecondaryCancerConditionProfile.model_validate(
                            condition
                        )
                    )
                )
            else:
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.PrimaryCancerConditionProfile.model_validate(
                            condition
                        )
                    )
                )
        for staging in case.stagings.all():  # type: ignore
            if staging.staging_domain == "lympohoma":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.LymphomaStageProfile.model_validate(staging.lymphoma)  # type: ignore
                    )
                )
            elif staging.staging_domain == "tnm":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.TNMStageGroupProfile.model_validate(
                            staging.tnm
                        )
                    )
                )
            else:
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.CancerStageProfile.model_validate(getattr(staging, staging.staging_domain))  # type: ignore
                    )
                )
        for marker in case.tumor_markers.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(resource=profiles.TumorMarkerProfile.model_validate(marker))
            )
        for risk in case.risk_assessments.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.CancerRiskAssessmentProfile.model_validate(risk)
                )
            )
        for variant in case.genomic_variants.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.GenomicVariantProfile.model_validate(variant)
                )
            )
        for comorbidity in case.comorbidities.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.ComorbiditiesProfile.model_validate(comorbidity)
                )
            )
        for lifestyle in case.lifestyles.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.LifestyleProfile.model_validate(lifestyle)
                )
            )
        for score in case.performance_status.all():  # type: ignore
            if score.ecog_score is not None:
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.ECOGPerformanceStatusProfile.model_validate(
                            score
                        )
                    )
                )
            elif score.karnofsky_score is not None:
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.KarnofskyPerformanceStatusProfile.model_validate(
                            score
                        )
                    )
                )
        for response in case.treatment_responses.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.ImagingDiseaseStatusProfile.model_validate(
                        response
                    )
                )
            )
        for vitals in case.vitals.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(resource=profiles.VitalsPanelProfile.model_validate(vitals))
            )
        for signature in case.genomic_signatures.all():  # type: ignore
            if signature.genomic_signature_type == "tumor_mutational_burden":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.TumorMutationalBurdenProfile.model_validate(
                            signature.tumor_mutational_burden
                        )
                    )
                )
            elif signature.genomic_signature_type == "loss_of_heterozygosity":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.LossOfHeterozygosityProfile.model_validate(
                            signature.loss_of_heterozygosity
                        )
                    )
                )
            elif signature.genomic_signature_type == "microsatellite_instability":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.MicrosatelliteInstabilityProfile.model_validate(
                            signature.microsatellite_instability
                        )
                    )
                )
            elif (
                signature.genomic_signature_type
                == "homologous_recombination_deficiency"
            ):
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.HomologousRecombinationDeficiencyProfile.model_validate(
                            signature.homologous_recombination_deficiency
                        )
                    )
                )
            elif signature.genomic_signature_type == "tumor_neoantigen_burden":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.TumorNeoantigenBurdenProfile.model_validate(
                            signature.tumor_neoantigen_burden
                        )
                    )
                )
            elif signature.genomic_signature_type == "aneuploid_score":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.AneuploidScoreProfile.model_validate(
                            signature.aneuploid_score
                        )
                    )
                )
        for procedure in case.surgeries.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.SurgicalProcedureProfile.model_validate(procedure)
                )
            )
        for course in case.radiotherapies.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.RadiotherapyCourseSummaryProfile.model_validate(
                        course
                    )
                )
            )
        for board in case.tumor_boards.all():  # type: ignore
            if board.tumor_board_specialty == "molecular":
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.MolecularTumorBoardReviewProfile.model_validate(
                            board.molecular
                        )
                    )
                )
            else:
                bundle.entry.append(
                    BundleEntry(
                        resource=profiles.TumorBoardReviewProfile.model_validate(
                            board.unspecified
                        )
                    )
                )
        for therapy in case.systemic_therapies.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.MedicationAdministrationProfile.model_validate(
                        therapy
                    )
                )
            )
        for event in case.adverse_events.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(resource=profiles.AdverseEventProfile.model_validate(event))
            )
        for history in case.family_histories.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(
                    resource=profiles.CancerFamilyMemberHistoryProfile.model_validate(
                        history
                    )
                )
            )
        for line in case.therapy_lines.all():  # type: ignore
            bundle.entry.append(
                BundleEntry(resource=profiles.TherapyLineProfile.model_validate(line))
            )
        return bundle
