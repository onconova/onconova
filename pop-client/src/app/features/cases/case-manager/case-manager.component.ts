import { Component, OnInit, Input, ViewEncapsulation, inject  } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Observable, delay } from 'rxjs'; 

import { AvatarModule } from 'primeng/avatar';
import { SkeletonModule } from 'primeng/skeleton';
import { Button } from 'primeng/button';
import { KnobModule } from 'primeng/knob';
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
    InteroperabilityService
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
import { ModalFormComponent } from "../../../shared/components/identicon/identicon.component";



@Component({
    standalone: true,
    templateUrl: './case-manager.component.html',
    styleUrl: './case-manager.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    CaseManagerPanelComponent,
    AvatarModule,
    Button,
    Fieldset,
    KnobModule,
    Divider,
    SkeletonModule,
    ModalFormComponent
],
})
export class CaseManagerComponent implements OnInit {

    // Injected dependencies
    public authService: AuthService = inject(AuthService);
    private interoperabilityService: InteroperabilityService = inject(InteroperabilityService);
    private caseService: PatientCasesService = inject(PatientCasesService);
    private neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    private stagingsService: StagingsService = inject(StagingsService);
    private tumorMarkersService: TumorMarkersService = inject(TumorMarkersService);
    private riskAssessmentsService: RiskAssessmentsService = inject(RiskAssessmentsService);
    private systemicTherapiesService: SystemicTherapiesService = inject(SystemicTherapiesService);
    private performanceStatiiService: PerformanceStatusService = inject(PerformanceStatusService);
    private surgeriesService: SurgeriesService = inject(SurgeriesService);
    private lifestylesService: LifestylesService = inject(LifestylesService);
    private comorbiditiesAssessmentsService: ComorbiditiesAssessmentsService = inject(ComorbiditiesAssessmentsService);
    private familyHistoriesService: FamilyHistoriesService = inject(FamilyHistoriesService);
    private radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService);
    private genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    private genomicSignaturesService: GenomicSignaturesService = inject(GenomicSignaturesService);
    private vitalsCoreService: VitalsService = inject(VitalsService);
    private adverseEventsService: AdverseEventsService = inject(AdverseEventsService);
    private tumorBoardsService: TumorBoardsService = inject(TumorBoardsService);
    private treatmentResponsesService: TreatmentResponsesService = inject(TreatmentResponsesService);
    private downloadService: DownloadService = inject(DownloadService);
    public location: Location = inject(Location);

    public exportLoading: boolean = false;

    // Case properties
    @Input() public pseudoidentifier: string = '';
    public case$!: Observable<PatientCase>;

    // Case-specific data observables
    public neoplasticEntityService: DataService = {
        get: (caseId) => this.neoplasticEntitiesService.getNeoplasticEntities({caseId: caseId}),
        delete: (id) => this.neoplasticEntitiesService.deleteNeoplasticEntityById({entityId: id}),
    };

    // Case-specific data observables
    public stagingService: DataService = {
        get: (caseId) => this.stagingsService.getStagings({caseId: caseId}),
        delete: (id) => this.stagingsService.deleteStagingById({stagingId: id}),
    };


    // Case-specific data observables
    public tumorMarkerService: DataService = {
        get: (caseId) => this.tumorMarkersService.getTumorMarkers({caseId: caseId}),
        delete: (id) => this.tumorMarkersService.deleteTumorMarkerById({tumorMarkerId: id}),
    };

    // Case-specific data observables
    public riskAssessmentService: DataService = {
        get: (caseId) => this.riskAssessmentsService.getRiskAssessments({caseId: caseId}),
        delete: (id) => this.riskAssessmentsService.deleteRiskAssessmentById({riskAssessmentId: id}),
    };

    // Case-specific data observables
    public systemicTherapyService: DataService = {
        get: (caseId) => this.systemicTherapiesService.getSystemicTherapies({caseId: caseId}),
        delete: (id) => this.systemicTherapiesService.deleteSystemicTherapyById({systemicTherapyId: id}),
    };

    // Case-specific data observables
    public performanceStatusService: DataService = {
        get: (caseId) => this.performanceStatiiService.getPerformanceStatus({caseId: caseId}),
        delete: (id) => this.performanceStatiiService.deletePerformanceStatus({performanceStatusId: id}),
    };

    // Case-specific data observables
    public surgeryService: DataService = {
        get: (caseId) => this.surgeriesService.getSurgeries({caseId: caseId}),
        delete: (id) => this.surgeriesService.deleteSurgeryById({surgeryId: id}),
    };
    // Case-specific data observables
    public radiotherapyService: DataService = {
        get: (caseId) => this.radiotherapiesService.getRadiotherapies({caseId: caseId}),
        delete: (id) => this.radiotherapiesService.deleteRadiotherapyById({radiotherapyId: id}),
    };
    // Case-specific data observables
    public lifestyleService: DataService = {
        get: (caseId) => this.lifestylesService.getLifestyles({caseId: caseId}),
        delete: (id) => this.lifestylesService.deleteLifestyleById({lifestyleId: id}),
    };
    // Case-specific data observables
    public familyHistoryService: DataService = {
        get: (caseId) => this.familyHistoriesService.getFamilyHistories({caseId: caseId}),
        delete: (id) => this.familyHistoriesService.deleteFamilyHistoryById({familyHistoryId: id}),
    };
    // Case-specific data observables
    public comorbiditiesAssessmentService: DataService = {
        get: (caseId) => this.comorbiditiesAssessmentsService.getComorbiditiesAssessments({caseId: caseId}),
        delete: (id) => this.comorbiditiesAssessmentsService.deleteComorbiditiesAssessment({comorbiditiesAssessmentId: id}),
    };
    // Case-specific data observables
    public genomicVariantService: DataService = {
        get: (caseId) => this.genomicVariantsService.getGenomicVariants({caseId: caseId}),
        delete: (id) => this.genomicVariantsService.deleteGenomicVariant({genomicVariantId: id}),
    };
    // Case-specific data observables
    public genomicSignatureService: DataService = {
        get: (caseId) => this.genomicSignaturesService.getGenomicSignatures({caseId: caseId}),
        delete: (id) => this.genomicSignaturesService.deleteGenomicSignatureById({genomicSignatureId: id}),
    };
    // Case-specific data observables
    public vitalsService: DataService = {
        get: (caseId) => this.vitalsCoreService.getVitals({caseId: caseId}),
        delete: (id) => this.vitalsCoreService.deleteVitalsById({vitalsId: id}),
    };
    // Case-specific data observables
    public adverseEventService: DataService = {
        get: (caseId) => this.adverseEventsService.getAdverseEvents({caseId: caseId}),
        delete: (id) => this.adverseEventsService.deleteAdverseEventById({adverseEventId: id}),
    };
    // Case-specific data observables
    public tumorBoardService: DataService = {
        get: (caseId) => this.tumorBoardsService.getTumorBoards({caseId: caseId}),
        delete: (id) => this.tumorBoardsService.deleteTumorBoardById({tumorBoardId: id}),
    };
    // Case-specific data observables
    public treatmentResponseService: DataService = {
        get: (caseId) => this.treatmentResponsesService.getTreatmentResponses({caseId: caseId}),
        delete: (id) => this.treatmentResponsesService.deleteTreatmentResponse({treatmentRresponseId: id}),
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

    ngOnInit() {
        this.case$ = this.caseService.getPatientCaseByPseudoidentifier({pseudoidentifier:this.pseudoidentifier});
    }

    downloadCaseBundle(caseId: string) {
        this.exportLoading = true;
        this.interoperabilityService.exportPatientCaseBundle({caseId:caseId}).subscribe({
            next: (response) => {
                this.downloadService.downloadAsJson(response, `case-bundle-${this.pseudoidentifier}.json`)
            },
            complete: () => {
                this.exportLoading = false;
            }
        })
    }

}