import { Component, inject, input, computed, contentChild, TemplateRef, signal  } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { map, tap } from 'rxjs'; 

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
    PatientCaseIdentifier,
} from 'pop-api-client'

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
import { AvatarGroup } from 'primeng/avatargroup';
import Scan from 'src/assets/images/icons/scan';
import Tumor from 'src/assets/images/icons/tumor';
import Risk from 'src/assets/images/icons/risk';
import Comorbidities from 'src/assets/images/icons/comorbidities';
import GenomicSignature from 'src/assets/images/icons/genomic_signature';
import AdverseEvent from 'src/assets/images/icons/adverse_event';
import Board from 'src/assets/images/icons/board';
import TourDriverConfig from './case-manager.tour';
import { driver } from 'driver.js';
import { ExportConfirmDialogComponent } from "../../../shared/components/export-confirm-dialog/export-confirm-dialog.component";
import { ConfirmDialog } from 'primeng/confirmdialog';
import { ConfirmationService, MessageService } from 'primeng/api';


@Component({
    templateUrl: './case-manager.component.html',
    selector: 'pop-case-manager',
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        CaseManagerPanelComponent,
        AvatarModule,
        AvatarGroup,
        Button,
        Fieldset,
        UserBadgeComponent,
        CancerIconComponent,
        ConfirmDialog,
        KnobModule,
        Divider,
        Knob,
        SkeletonModule,
        IdenticonComponent,
        ExportConfirmDialogComponent
    ],
    providers: [
        ConfirmationService,
    ]
})
export class CaseManagerComponent {

    public additionalCaseActionButtons = contentChild<TemplateRef<any> >('additionalCaseActionButtons', { descendants: false });
    
    readonly #route = inject(ActivatedRoute);
    protected readonly caseId = this.#route.snapshot.data['caseId'];

    // Injected dependencies
    public location = inject(Location);
    readonly #authService = inject(AuthService);
    readonly #downloadService = inject(DownloadService);
    readonly #messageService = inject(MessageService);
    readonly #confirmationService = inject(ConfirmationService);

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
        get: (request) => this.#neoplasticEntitiesService.getNeoplasticEntities(request),
        delete: (id) => this.#neoplasticEntitiesService.deleteNeoplasticEntityById({entityId: id}),
        history: (id) => this.#neoplasticEntitiesService.getAllNeoplasticEntityHistoryEvents({entityId: id}),
    };
    public stagingService: DataService = {
        get: (request) => this.#stagingsService.getStagings(request),
        delete: (id) => this.#stagingsService.deleteStagingById({stagingId: id}),
        history: (id) => this.#stagingsService.getAllStagingHistoryEvents({stagingId: id}),
    };
    public tumorMarkerService: DataService = {
        get: (request) => this.#tumorMarkersService.getTumorMarkers(request),
        delete: (id) => this.#tumorMarkersService.deleteTumorMarkerById({tumorMarkerId: id}),
        history: (id) => this.#tumorMarkersService.getAllTumorMarkerHistoryEvents({tumorMarkerId: id}),
    };
    public riskAssessmentService: DataService = {
        get: (request) => this.#riskAssessmentsService.getRiskAssessments(request),
        delete: (id) => this.#riskAssessmentsService.deleteRiskAssessmentById({riskAssessmentId: id}),
        history: (id) => this.#riskAssessmentsService.getAllRiskAssessmentHistoryEvents({riskAssessmentId: id}),
    };
    public systemicTherapyService: DataService = {
        get: (request) => this.#systemicTherapiesService.getSystemicTherapies(request),
        delete: (id) => this.#systemicTherapiesService.deleteSystemicTherapyById({systemicTherapyId: id}),
        history: (id) => this.#systemicTherapiesService.getAllSystemicTherapyHistoryEvents({systemicTherapyId: id}),
    };
    public performanceStatusService: DataService = {
        get: (request) => this.#performanceStatiiService.getPerformanceStatus(request),
        delete: (id) => this.#performanceStatiiService.deletePerformanceStatus({performanceStatusId: id}),
        history: (id) => this.#performanceStatiiService.getAllPerformanceStatusHistoryEvents({performanceStatusId: id}),
    };
    public surgeryService: DataService = {
        get: (request) => this.#surgeriesService.getSurgeries(request),
        delete: (id) => this.#surgeriesService.deleteSurgeryById({surgeryId: id}),
        history: (id) => this.#surgeriesService.getAllSurgeryHistoryEvents({surgeryId: id}),
    };
    public radiotherapyService: DataService = {
        get: (request) => this.#radiotherapiesService.getRadiotherapies(request),
        delete: (id) => this.#radiotherapiesService.deleteRadiotherapyById({radiotherapyId: id}),
        history: (id) => this.#radiotherapiesService.getAllRadiotherapyHistoryEvents({radiotherapyId: id}),
    };
    public lifestyleService: DataService = {
        get: (request) => this.#lifestylesService.getLifestyles(request),
        delete: (id) => this.#lifestylesService.deleteLifestyleById({lifestyleId: id}),
        history: (id) => this.#lifestylesService.getAllLifestyleHistoryEvents({lifestyleId: id}),
    };
    public familyHistoryService: DataService = {
        get: (request) => this.#familyHistoriesService.getFamilyHistories(request),
        delete: (id) => this.#familyHistoriesService.deleteFamilyHistoryById({familyHistoryId: id}),
        history: (id) => this.#familyHistoriesService.getAllFamilyHistoryHistoryEvents({familyHistoryId: id}),
    };
    public comorbiditiesAssessmentService: DataService = {
        get: (request) => this.#comorbiditiesAssessmentsService.getComorbiditiesAssessments(request),
        delete: (id) => this.#comorbiditiesAssessmentsService.deleteComorbiditiesAssessment({comorbiditiesAssessmentId: id}),
        history: (id) => this.#comorbiditiesAssessmentsService.getAllComorbiditiesAssessmentHistoryEvents({comorbiditiesAssessmentId: id}),
    };
    public genomicVariantService: DataService = {
        get: (request) => this.#genomicVariantsService.getGenomicVariants(request),
        delete: (id) => this.#genomicVariantsService.deleteGenomicVariant({genomicVariantId: id}),
        history: (id) => this.#genomicVariantsService.getAllGenomicVariantHistoryEvents({genomicVariantId: id}),
    };
    public genomicSignatureService: DataService = {
        get: (request) => this.#genomicSignaturesService.getGenomicSignatures(request),
        delete: (id) => this.#genomicSignaturesService.deleteGenomicSignatureById({genomicSignatureId: id}),
        history: (id) => this.#genomicSignaturesService.getAllGenomicSignatureHistoryEvents({genomicSignatureId: id}),
    };
    public vitalsService: DataService = {
        get: (request) => this.#vitalsCoreService.getVitals(request),
        delete: (id) => this.#vitalsCoreService.deleteVitalsById({vitalsId: id}),
        history: (id) => this.#vitalsCoreService.getAllVitalsHistoryEvents({vitalsId: id}),
    };
    public adverseEventService: DataService = {
        get: (request) => this.#adverseEventsService.getAdverseEvents(request),
        delete: (id) => this.#adverseEventsService.deleteAdverseEventById({adverseEventId: id}),
        history: (id) => this.#adverseEventsService.getAllAdverseEventHistoryEvents({adverseEventId: id}),
    };
    public tumorBoardService: DataService = {
        get: (request) => this.#tumorBoardsService.getTumorBoards(request),
        delete: (id) => this.#tumorBoardsService.deleteTumorBoardById({tumorBoardId: id}),
        history: (id) => this.#tumorBoardsService.getAllTumorBoardHistoryEvents({tumorBoardId: id}),
    };
    public treatmentResponseService: DataService = {
        get: (request) => this.#treatmentResponsesService.getTreatmentResponses(request),
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
        neoplasticEntities: Tumor,
        stagings: Tags,
        riskAssessments: Risk,
        tumorMarkers: TestTubeDiagonal,
        genomicVariants: Dna,
        genomicSignatures: GenomicSignature,
        systemicTherapies: Tablets,
        surgeries: Slice, 
        radiotherapies: Radiation,
        lifestyle: Cigarette,
        familyHistory: History,
        comorbidities: Comorbidities,
        vitals: Activity,
        tumorBoards: Board,
        adverseEvents: AdverseEvent,
        treatmentResponses: Scan, 
        performanceStatus: CircleGauge,
    }

    protected readonly tour = TourDriverConfig;
    public exportLoading: boolean = false;
    public totalCompletion!: number; 
    readonly currentUser = computed(() => this.#authService.user());
    protected anonymized = signal<boolean>(true); 
    
    // Case properties
    public pseudoidentifier = input.required<string>();
    public case$ = rxResource({
        request: () => ({caseId: this.caseId, anonymized: this.anonymized()}),
        loader: ({request}) => this.#caseService.getPatientCaseById(request).pipe(
            tap(response => this.totalCompletion = response.dataCompletionRate)
        )
    })
    public primaryEntity = rxResource({
        request: () => ({caseId: this.caseId, relationship: 'primary', limit: 1}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(
            map(data => data.items.length ? data.items[0] : null)
        )
    })
    public latestStaging = rxResource({
        request: () => ({caseId: this.caseId, limit: 1}),
        loader: ({request}) => this.#stagingsService.getStagings(request).pipe(
            map(data => data.items.length ? data.items[0] : null)
        )
    })
    
    downloadCaseBundle(caseId: string) {
        this.#confirmationService.confirm({
            accept: () => {
                this.exportLoading = true;
                this.#messageService.add({severity: 'info', summary: 'Export in progress', detail:'Preparing data for download. Please wait.'})
                this.#interoperabilityService.exportPatientCaseBundle({caseId:caseId}).subscribe({
                    next: (response) => {
                        this.#downloadService.downloadAsJson(response, `case-bundle-${this.pseudoidentifier()}.json`)
                    },
                    complete: () => {
                        this.#messageService.add({ severity: 'success', summary: 'Successfully exported'})
                        this.exportLoading = false;
                    },
                    error: (error: any) => {
                        this.#messageService.add({ severity: 'error', summary: 'Error exporting case', detail: error?.error?.detail })
                        this.exportLoading = false;
                    },
                })
            }
        })

    }

    updateCompletion(completed: boolean) {
        this.totalCompletion = this.totalCompletion + Math.round(100*(completed ? 1 : -1)/Object.keys(this.icons).length);
    }

    startTour() {
        driver(this.tour).drive()    
    }

}