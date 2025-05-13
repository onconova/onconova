import { Component, OnInit, Input, ViewEncapsulation, inject, input, computed, contentChild  } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Observable, catchError, delay, map, tap } from 'rxjs'; 

import { AvatarModule } from 'primeng/avatar';
import { SkeletonModule } from 'primeng/skeleton';
import { Button } from 'primeng/button';
import { Knob, KnobModule } from 'primeng/knob';
import { Divider } from 'primeng/divider';
import { Fieldset } from 'primeng/fieldset';

import { 
    Ribbon, HeartPulse, Tags, TestTubeDiagonal, Dna, 
    Fingerprint, Tablets, Slice, Radiation, Cigarette, 
    DiamondPlus, Activity, Presentation, ShieldAlert, 
    Image, CircleGauge, History } from 'lucide-angular';

import { 
    PatientCase, 
    PatientCasesService,
    PatientCaseDataCategories,
    NeoplasticEntitiesService,
    StagingsService,
    TumorMarkersService,
    RiskAssessmentsService,
    SystemicTherapiesService,
    PerformanceStatusService,
    SurgeriesService,
    LifestylesService,
    ComorbiditiesAssessmentsService,
    FamilyHistoriesService,
    VitalsService,
    RadiotherapiesService,
    GenomicVariantsService,
    GenomicSignaturesService,
    AdverseEventsService,
    TumorBoardsService,
    TreatmentResponsesService,
    InteroperabilityService,
    NeoplasticEntity,
    AnyStaging
} from 'src/app/shared/openapi'

import { 
    NeoplasticEntityFormComponent,
    StagingFormComponent,
    TumorMarkerFormComponent,
    RiskAssessmentFormComponent,
    SystemicTherapyFormComponent,
    PerformanceStatusFormComponent,
    SurgeryFormComponent,
    LifestyleFormComponent,
    FamilyHistoryFormComponent,
    VitalsFormComponent,
    ComorbiditiesAssessmentFormComponent,
    RadiotherapyFormComponent,
    GenomicVariantFormComponent,
    GenomicSignatureFormComponent,
    TumorBoardFormComponent,
    AdverseEventFormComponent,
    TreatmentResponseFormComponent,
} from 'src/app/features/forms';

import { CaseManagerPanelComponent,DataService } from './components/case-manager-panel/case-manager-panel.component'
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DownloadService } from 'src/app/shared/services/download.service';
import { IdenticonComponent } from "../../../shared/components/identicon/identicon.component";
import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { rxResource } from '@angular/core/rxjs-interop';



@Component({
    templateUrl: './case-manager.component.html',
    selector: 'pop-case-manager',
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        CaseManagerPanelComponent,
        AvatarModule,
        Button,
        Fieldset,
        UserBadgeComponent,
        CancerIconComponent,
        KnobModule,
        Divider,
        Knob,
        SkeletonModule,
        IdenticonComponent
    ]
})
export class CaseManagerComponent {

    public additionalCaseActionButtons = contentChild<TemplateRef<any> | null>('additionalCaseActionButtons', { descendants: false });
  
    // Injected dependencies
    public location: Location = inject(Location);
    readonly #authService: AuthService = inject(AuthService);
    readonly #downloadService: DownloadService = inject(DownloadService);

    // Domain-specific dependencies
    readonly #interoperabilityService = inject(InteroperabilityService);
    readonly #caseService = inject(PatientCasesService);
    readonly #neoplasticEntitiesService = inject(NeoplasticEntitiesService);
    readonly #stagingsService = inject(StagingsService);
    readonly #tumorMarkersService = inject(TumorMarkersService);
    readonly #riskAssessmentsService = inject(RiskAssessmentsService);
    readonly #systemicTherapiesService = inject(SystemicTherapiesService);
    readonly #performanceStatiiService = inject(PerformanceStatusService);
    readonly #surgeriesService = inject(SurgeriesService);
    readonly #lifestylesService = inject(LifestylesService);
    readonly #comorbiditiesAssessmentsService = inject(ComorbiditiesAssessmentsService);
    readonly #familyHistoriesService = inject(FamilyHistoriesService);
    readonly #radiotherapiesService = inject(RadiotherapiesService);
    readonly #genomicVariantsService = inject(GenomicVariantsService);
    readonly #genomicSignaturesService = inject(GenomicSignaturesService);
    readonly #vitalsCoreService = inject(VitalsService);
    readonly #adverseEventsService = inject(AdverseEventsService);
    readonly #tumorBoardsService = inject(TumorBoardsService);
    readonly #treatmentResponsesService = inject(TreatmentResponsesService);


    public neoplasticEntityService: DataService = {
        get: (caseId) => this.#neoplasticEntitiesService.getNeoplasticEntities({caseId: caseId}),
        delete: (id) => this.#neoplasticEntitiesService.deleteNeoplasticEntityById({entityId: id}),
        history: (id) => this.#neoplasticEntitiesService.getAllNeoplasticEntityHistoryEvents({entityId: id}),
    };
    public stagingService: DataService = {
        get: (caseId) => this.#stagingsService.getStagings({caseId: caseId}),
        delete: (id) => this.#stagingsService.deleteStagingById({stagingId: id}),
        history: (id) => this.#stagingsService.getAllStagingHistoryEvents({stagingId: id}),
    };
    public tumorMarkerService: DataService = {
        get: (caseId) => this.#tumorMarkersService.getTumorMarkers({caseId: caseId}),
        delete: (id) => this.#tumorMarkersService.deleteTumorMarkerById({tumorMarkerId: id}),
        history: (id) => this.#tumorMarkersService.getAllTumorMarkerHistoryEvents({tumorMarkerId: id}),
    };
    public riskAssessmentService: DataService = {
        get: (caseId) => this.#riskAssessmentsService.getRiskAssessments({caseId: caseId}),
        delete: (id) => this.#riskAssessmentsService.deleteRiskAssessmentById({riskAssessmentId: id}),
        history: (id) => this.#riskAssessmentsService.getAllRiskAssessmentHistoryEvents({riskAssessmentId: id}),
    };
    public systemicTherapyService: DataService = {
        get: (caseId) => this.#systemicTherapiesService.getSystemicTherapies({caseId: caseId}),
        delete: (id) => this.#systemicTherapiesService.deleteSystemicTherapyById({systemicTherapyId: id}),
        history: (id) => this.#systemicTherapiesService.getAllSystemicTherapyHistoryEvents({systemicTherapyId: id}),
    };
    public performanceStatusService: DataService = {
        get: (caseId) => this.#performanceStatiiService.getPerformanceStatus({caseId: caseId}),
        delete: (id) => this.#performanceStatiiService.deletePerformanceStatus({performanceStatusId: id}),
        history: (id) => this.#performanceStatiiService.getAllPerformanceStatusHistoryEvents({performanceStatusId: id}),
    };
    public surgeryService: DataService = {
        get: (caseId) => this.#surgeriesService.getSurgeries({caseId: caseId}),
        delete: (id) => this.#surgeriesService.deleteSurgeryById({surgeryId: id}),
        history: (id) => this.#surgeriesService.getAllSurgeryHistoryEvents({surgeryId: id}),
    };
    public radiotherapyService: DataService = {
        get: (caseId) => this.#radiotherapiesService.getRadiotherapies({caseId: caseId}),
        delete: (id) => this.#radiotherapiesService.deleteRadiotherapyById({radiotherapyId: id}),
        history: (id) => this.#radiotherapiesService.getAllRadiotherapyHistoryEvents({radiotherapyId: id}),
    };
    public lifestyleService: DataService = {
        get: (caseId) => this.#lifestylesService.getLifestyles({caseId: caseId}),
        delete: (id) => this.#lifestylesService.deleteLifestyleById({lifestyleId: id}),
        history: (id) => this.#lifestylesService.getAllLifestyleHistoryEvents({lifestyleId: id}),
    };
    public familyHistoryService: DataService = {
        get: (caseId) => this.#familyHistoriesService.getFamilyHistories({caseId: caseId}),
        delete: (id) => this.#familyHistoriesService.deleteFamilyHistoryById({familyHistoryId: id}),
        history: (id) => this.#familyHistoriesService.getAllFamilyHistoryHistoryEvents({familyHistoryId: id}),
    };
    public comorbiditiesAssessmentService: DataService = {
        get: (caseId) => this.#comorbiditiesAssessmentsService.getComorbiditiesAssessments({caseId: caseId}),
        delete: (id) => this.#comorbiditiesAssessmentsService.deleteComorbiditiesAssessment({comorbiditiesAssessmentId: id}),
        history: (id) => this.#comorbiditiesAssessmentsService.getAllComorbiditiesAssessmentHistoryEvents({comorbiditiesAssessmentId: id}),
    };
    public genomicVariantService: DataService = {
        get: (caseId) => this.#genomicVariantsService.getGenomicVariants({caseId: caseId}),
        delete: (id) => this.#genomicVariantsService.deleteGenomicVariant({genomicVariantId: id}),
        history: (id) => this.#genomicVariantsService.getAllGenomicVariantHistoryEvents({genomicVariantId: id}),
    };
    public genomicSignatureService: DataService = {
        get: (caseId) => this.#genomicSignaturesService.getGenomicSignatures({caseId: caseId}),
        delete: (id) => this.#genomicSignaturesService.deleteGenomicSignatureById({genomicSignatureId: id}),
        history: (id) => this.#genomicSignaturesService.getAllGenomicSignatureHistoryEvents({genomicSignatureId: id}),
    };
    public vitalsService: DataService = {
        get: (caseId) => this.#vitalsCoreService.getVitals({caseId: caseId}),
        delete: (id) => this.#vitalsCoreService.deleteVitalsById({vitalsId: id}),
        history: (id) => this.#vitalsCoreService.getAllVitalsHistoryEvents({vitalsId: id}),
    };
    public adverseEventService: DataService = {
        get: (caseId) => this.#adverseEventsService.getAdverseEvents({caseId: caseId}),
        delete: (id) => this.#adverseEventsService.deleteAdverseEventById({adverseEventId: id}),
        history: (id) => this.#adverseEventsService.getAllAdverseEventHistoryEvents({adverseEventId: id}),
    };
    public tumorBoardService: DataService = {
        get: (caseId) => this.#tumorBoardsService.getTumorBoards({caseId: caseId}),
        delete: (id) => this.#tumorBoardsService.deleteTumorBoardById({tumorBoardId: id}),
        history: (id) => this.#tumorBoardsService.getAllTumorBoardHistoryEvents({tumorBoardId: id}),
    };
    public treatmentResponseService: DataService = {
        get: (caseId) => this.#treatmentResponsesService.getTreatmentResponses({caseId: caseId}),
        delete: (id) => this.#treatmentResponsesService.deleteTreatmentResponse({treatmentRresponseId: id}),
        history: (id) => this.#treatmentResponsesService.getAllTreatmentResponseHistoryEvents({treatmentRresponseId: id}),
    };

    // Form components
    public NeoplasticEntityFormComponent = NeoplasticEntityFormComponent;
    public StagingFormComponent = StagingFormComponent;
    public TumorMarkerFormComponent = TumorMarkerFormComponent;
    public RiskAssessmentFormComponent = RiskAssessmentFormComponent;
    public SystemicTherapyFormComponent = SystemicTherapyFormComponent;
    public PerformanceStatusFormComponent =PerformanceStatusFormComponent;
    public SurgeryFormComponent = SurgeryFormComponent;
    public LifestyleFormComponent = LifestyleFormComponent;
    public FamilyHistoryFormComponent = FamilyHistoryFormComponent;
    public VitalsFormComponent = VitalsFormComponent;
    public ComorbiditiesAssessmentFormComponent = ComorbiditiesAssessmentFormComponent;
    public RadiotherapyFormComponent = RadiotherapyFormComponent;
    public GenomicVariantFormComponent = GenomicVariantFormComponent;
    public GenomicSignatureFormComponent = GenomicSignatureFormComponent;
    public TumorBoardFormComponent = TumorBoardFormComponent;
    public AdverseEventFormComponent = AdverseEventFormComponent;
    public TreatmentResponseFormComponent = TreatmentResponseFormComponent;

    public readonly PatientCaseDataCategories = PatientCaseDataCategories; 

    public icons = {
        neoplasticEntities: Ribbon,
        stagings: Tags,
        riskAssessments: HeartPulse,
        tumorMarkers: TestTubeDiagonal,
        genomicVariants: Dna,
        genomicSignatures: Fingerprint,
        systemicTherapies: Tablets,
        surgeries: Slice, 
        radiotherapies: Radiation,
        lifestyle: Cigarette,
        familyHistory: History,
        comorbidities: DiamondPlus,
        vitals: Activity,
        tumorBoards: Presentation,
        adverseEvents: ShieldAlert,
        treatmentResponses: Image, 
        performanceStatus: CircleGauge,
    }

    public exportLoading: boolean = false;
    public totalCompletion!: number; 
    readonly currentUser = computed(() => this.#authService.user());
    
    // Case properties
    public pseudoidentifier = input.required<string>();
    public case$ = rxResource({
        request: () => ({pseudoidentifier: this.pseudoidentifier()}),
        loader: ({request}) => this.#caseService.getPatientCaseByPseudoidentifier(request).pipe(
            tap(response => this.totalCompletion = response.dataCompletionRate)
        )
    })
    public primaryEntity$ = rxResource({
        request: () => ({caseId: this.case$.value()?.id, relationship: 'primary', limit: 1}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(
            map(data => data.items.length ? data.items[0] : null)
        )
    })
    public latestStaging$ = rxResource({
        request: () => ({caseId: this.case$.value()?.id, limit: 1}),
        loader: ({request}) => this.#stagingsService.getStagings(request).pipe(
            map(data => data.items.length ? data.items[0] : null)
        )
    })
    
    downloadCaseBundle(caseId: string) {
        this.exportLoading = true;
        this.#interoperabilityService.exportPatientCaseBundle({caseId:caseId}).subscribe({
            next: (response) => {
                this.#downloadService.downloadAsJson(response, `case-bundle-${this.pseudoidentifier}.json`)
            },
            complete: () => {
                this.exportLoading = false;
            }
        })
    }

    updateCompletion(completed: boolean) {
        this.totalCompletion = this.totalCompletion + Math.round(100*(completed ? 1 : -1)/Object.keys(this.icons).length);
    }

}