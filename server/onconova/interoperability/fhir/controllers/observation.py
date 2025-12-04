from ninja_extra import api_controller, route
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import (
    TumorMarkerProfile,
    CancerRiskAssessmentProfile,
    GenomicVariantProfile,
    TumorMutationalBurdenProfile,
    MicrosatelliteInstabilityProfile,
    LossOfHeterozygosityProfile,
    HomologousRecombinationDeficiencyProfile,
    TumorNeoantigenBurdenProfile,
    AneuploidScoreProfile,
    ComorbiditiesProfile,
    LifestyleProfile,
    ECOGPerformanceStatusProfile,
    KarnofskyPerformanceStatusProfile,
    ImagingDiseaseStatusProfile,
    CancerStageProfile,
    TNMStageGroupProfile,
    LymphomaStageProfile,
    VitalsPanelProfile,
)
from onconova.oncology.models import (
    TumorMarker,
    RiskAssessment,
    GenomicVariant,
    TumorMutationalBurden,
    MicrosatelliteInstability,
    LossOfHeterozygosity,
    HomologousRecombinationDeficiency,
    TumorNeoantigenBurden,
    AneuploidScore,
    ComorbiditiesAssessment,
    Lifestyle,
    PerformanceStatus,
    TreatmentResponse,
    FIGOStaging,
    BreslowDepth,
    RaiStaging,
    BinetStaging,
    ClarkStaging,
    ISSStaging,
    RISSStaging,
    INSSStage,
    INRGSSStage,
    GleasonGrade,
    RhabdomyosarcomaClinicalGroup,
    WilmsStage,
    TNMStaging,
    LymphomaStaging,
    Vitals,
)
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "Observation",
    auth=[XSessionTokenAuth()],
    tags=["Observations"],
)
class ObservationController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={
            200: GenomicVariantProfile
            | TumorMarkerProfile
            | TumorMutationalBurdenProfile
            | MicrosatelliteInstabilityProfile
            | LossOfHeterozygosityProfile
            | HomologousRecombinationDeficiencyProfile
            | TumorNeoantigenBurdenProfile
            | AneuploidScoreProfile
            | ComorbiditiesProfile
            | LifestyleProfile
            | VitalsPanelProfile
            | ECOGPerformanceStatusProfile
            | KarnofskyPerformanceStatusProfile
            | ImagingDiseaseStatusProfile
            | LymphomaStageProfile
            | TNMStageGroupProfile
            | CancerStageProfile
            | CancerRiskAssessmentProfile,
            **COMMON_READ_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="readObservation",
        exclude_none=True,
        summary="Read the current state of the resource",
    )
    def read_observation(self, rid: str):
        return self.read_fhir_resource(
            rid,
            [
                TumorMarker,
                RiskAssessment,
                GenomicVariant,
                TumorMutationalBurden,
                MicrosatelliteInstability,
                LossOfHeterozygosity,
                HomologousRecombinationDeficiency,
                TumorNeoantigenBurden,
                AneuploidScore,
                ComorbiditiesAssessment,
                Lifestyle,
                PerformanceStatus,
                TreatmentResponse,
                FIGOStaging,
                BreslowDepth,
                RaiStaging,
                BinetStaging,
                ClarkStaging,
                ISSStaging,
                RISSStaging,
                INSSStage,
                INRGSSStage,
                GleasonGrade,
                RhabdomyosarcomaClinicalGroup,
                WilmsStage,
                TNMStaging,
                LymphomaStaging,
                Vitals,
            ],
        )

    @route.put(
        path="{rid}",
        response={
            200: GenomicVariantProfile
            | TumorMarkerProfile
            | TumorMutationalBurdenProfile
            | MicrosatelliteInstabilityProfile
            | LossOfHeterozygosityProfile
            | HomologousRecombinationDeficiencyProfile
            | TumorNeoantigenBurdenProfile
            | AneuploidScoreProfile
            | ComorbiditiesProfile
            | LifestyleProfile
            | VitalsPanelProfile
            | ECOGPerformanceStatusProfile
            | KarnofskyPerformanceStatusProfile
            | ImagingDiseaseStatusProfile
            | LymphomaStageProfile
            | TNMStageGroupProfile
            | CancerStageProfile
            | CancerRiskAssessmentProfile
            | OperationOutcome
            | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateObservation",
        exclude_none=True,
        summary="Update the current state of the resource",
    )
    def update_observation(
        self,
        rid: str,
        payload: (
            GenomicVariantProfile
            | TumorMarkerProfile
            | TumorMutationalBurdenProfile
            | MicrosatelliteInstabilityProfile
            | LossOfHeterozygosityProfile
            | HomologousRecombinationDeficiencyProfile
            | TumorNeoantigenBurdenProfile
            | AneuploidScoreProfile
            | ComorbiditiesProfile
            | LifestyleProfile
            | VitalsPanelProfile
            | ECOGPerformanceStatusProfile
            | KarnofskyPerformanceStatusProfile
            | ImagingDiseaseStatusProfile
            | LymphomaStageProfile
            | TNMStageGroupProfile
            | CancerStageProfile
            | CancerRiskAssessmentProfile
        ),
    ):
        return self.update_fhir_resource(rid, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteObservation",
        exclude_none=True,
        summary="Delete the resource so that it no exists (no read, search etc)",
    )
    def delete_observation(self, rid: str):
        return self.delete_fhir_resource(
            rid,
            [
                TumorMarker,
                RiskAssessment,
                GenomicVariant,
                TumorMutationalBurden,
                MicrosatelliteInstability,
                LossOfHeterozygosity,
                HomologousRecombinationDeficiency,
                TumorNeoantigenBurden,
                AneuploidScore,
                ComorbiditiesAssessment,
                Lifestyle,
                PerformanceStatus,
                TreatmentResponse,
                FIGOStaging,
                BreslowDepth,
                RaiStaging,
                BinetStaging,
                ClarkStaging,
                ISSStaging,
                RISSStaging,
                INSSStage,
                INRGSSStage,
                GleasonGrade,
                RhabdomyosarcomaClinicalGroup,
                WilmsStage,
                TNMStaging,
                LymphomaStaging,
                Vitals,
            ],
        )

    @route.post(
        path="",
        response={
            200: GenomicVariantProfile
            | TumorMarkerProfile
            | TumorMutationalBurdenProfile
            | MicrosatelliteInstabilityProfile
            | LossOfHeterozygosityProfile
            | HomologousRecombinationDeficiencyProfile
            | TumorNeoantigenBurdenProfile
            | AneuploidScoreProfile
            | ComorbiditiesProfile
            | LifestyleProfile
            | VitalsPanelProfile
            | ECOGPerformanceStatusProfile
            | KarnofskyPerformanceStatusProfile
            | ImagingDiseaseStatusProfile
            | LymphomaStageProfile
            | TNMStageGroupProfile
            | CancerStageProfile
            | CancerRiskAssessmentProfile
            | OperationOutcome
            | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createObservation",
        exclude_none=True,
        summary="Create a new resource",
    )
    def create_observation(
        self,
        payload: (
            GenomicVariantProfile
            | TumorMarkerProfile
            | TumorMutationalBurdenProfile
            | MicrosatelliteInstabilityProfile
            | LossOfHeterozygosityProfile
            | HomologousRecombinationDeficiencyProfile
            | TumorNeoantigenBurdenProfile
            | AneuploidScoreProfile
            | ComorbiditiesProfile
            | LifestyleProfile
            | VitalsPanelProfile
            | ECOGPerformanceStatusProfile
            | KarnofskyPerformanceStatusProfile
            | ImagingDiseaseStatusProfile
            | LymphomaStageProfile
            | TNMStageGroupProfile
            | CancerStageProfile
            | CancerRiskAssessmentProfile
        ),
    ):
        return self.create_fhir_resource(payload)
