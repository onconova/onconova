import { Component, OnInit, Input, ViewEncapsulation, inject  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, Subscription } from 'rxjs'; 

import { MessageService } from 'primeng/api';
import { AvatarModule } from 'primeng/avatar';

import { NgxJdenticonModule } from "ngx-jdenticon";

import { 
    Ribbon, HeartPulse, Tags, TestTubeDiagonal, Dna, 
    Fingerprint, Tablets, Slice, Radiation, Cigarette, 
    DiamondPlus, Activity, Presentation, ShieldAlert, 
    Image, CircleGauge } from 'lucide-angular';

import { 
    PatientCase, 
    PatientCasesService,
    NeoplasticEntitiesService,
    StagingsService,
    TumorMarkersService,
    RiskAssessmentsService,
    SystemicTherapiesService,
    PerformanceStatusService,
    SurgeriesService,
    LifestylesService,
    RadiotherapiesService,
    GenomicVariantsService,
    GenomicSignaturesService
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
    RadiotherapyFormComponent,
    GenomicVariantFormComponent,
} from 'src/app/core/forms';

import { ModalFormComponent } from 'src/app/shared/components/modal-form/modal-form.component'
import { CaseManagerPanelComponent } from './components/case-manager-panel/case-manager-panel.component'


interface DataService {
    get: CallableFunction;
    create: CallableFunction;
    delete: CallableFunction;
    update: CallableFunction;
}


@Component({
    standalone: true,
    templateUrl: './case-manager.component.html',
    styleUrl: './case-manager.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule,
        CaseManagerPanelComponent,
        ModalFormComponent,
        NgxJdenticonModule,
        AvatarModule,
    ]
})
export class CaseManagerComponent implements OnInit {

    // Injected dependencies
    private caseService: PatientCasesService = inject(PatientCasesService);;
    private caseServiceSubscription!: Subscription;
    private neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    private stagingsService: StagingsService = inject(StagingsService);
    private tumorMarkersService: TumorMarkersService = inject(TumorMarkersService);
    private riskAssessmentsService: RiskAssessmentsService = inject(RiskAssessmentsService);
    private systemicTherapiesService: SystemicTherapiesService = inject(SystemicTherapiesService);
    private performanceStatiiService: PerformanceStatusService = inject(PerformanceStatusService);
    private surgeriesService: SurgeriesService = inject(SurgeriesService);
    private lifestylesService: LifestylesService = inject(LifestylesService);
    private radiotherapiesService: RadiotherapiesService = inject(RadiotherapiesService);
    private genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    private genomicSignaturesService: GenomicSignaturesService = inject(GenomicSignaturesService);
    private messageService: MessageService = inject(MessageService);

    // Case properties
    @Input() public pseudoidentifier: string = '';
    public case!: PatientCase;
    public caseId!: string;

    // Case-specific data observables
    public neoplasticEntityService: DataService = {
        get: this.neoplasticEntitiesService.getNeoplasticEntities.bind(this.neoplasticEntitiesService),
        create: this.neoplasticEntitiesService.createNeoplasticEntity.bind(this.neoplasticEntitiesService),
        delete: this.neoplasticEntitiesService.deleteNeoplasticEntityById.bind(this.neoplasticEntitiesService),
        update: this.neoplasticEntitiesService.updateNeoplasticEntityById.bind(this.neoplasticEntitiesService),
    };

    // Case-specific data observables
    public stagingService: DataService = {
        get: this.stagingsService.getStagings.bind(this.stagingsService),
        create: this.stagingsService.createStaging.bind(this.stagingsService),
        delete: this.stagingsService.deleteStagingById.bind(this.stagingsService),
        update: this.stagingsService.updateStagingById.bind(this.stagingsService),
    };


    // Case-specific data observables
    public tumorMarkerService: DataService = {
        get: this.tumorMarkersService.getTumorMarkers.bind(this.tumorMarkersService),
        create: this.tumorMarkersService.createTumorMarker.bind(this.tumorMarkersService),
        delete: this.tumorMarkersService.deleteTumorMarkerById.bind(this.tumorMarkersService),
        update: this.tumorMarkersService.updateTumorMarkerById.bind(this.tumorMarkersService),
    };

    // Case-specific data observables
    public riskAssessmentService: DataService = {
        get: this.riskAssessmentsService.getRiskAssessments.bind(this.riskAssessmentsService),
        create: this.riskAssessmentsService.createRiskAssessment.bind(this.riskAssessmentsService),
        delete: this.riskAssessmentsService.deleteRiskAssessmentById.bind(this.riskAssessmentsService),
        update: this.riskAssessmentsService.updateRiskAssessmentById.bind(this.riskAssessmentsService),
    };

    // Case-specific data observables
    public systemicTherapyService: DataService = {
        get: this.systemicTherapiesService.getSystemicTherapies.bind(this.systemicTherapiesService),
        create: this.systemicTherapiesService.createSystemicTherapy.bind(this.systemicTherapiesService),
        delete: this.systemicTherapiesService.deleteSystemicTherapyById.bind(this.systemicTherapiesService),
        update: this.systemicTherapiesService.updateSystemicTherapy.bind(this.systemicTherapiesService),
    };

    // Case-specific data observables
    public performanceStatusService: DataService = {
        get: this.performanceStatiiService.getPerformanceStatus.bind(this.performanceStatiiService),
        create: this.performanceStatiiService.createPerformanceStatus.bind(this.performanceStatiiService),
        delete: this.performanceStatiiService.deletePerformanceStatus.bind(this.performanceStatiiService),
        update: this.performanceStatiiService.updatePerformanceStatusById.bind(this.performanceStatiiService),
    };

    // Case-specific data observables
    public surgeryService: DataService = {
        get: this.surgeriesService.getSurgeries.bind(this.surgeriesService),
        create: this.surgeriesService.createSurgery.bind(this.surgeriesService),
        delete: this.surgeriesService.deleteSurgeryById.bind(this.surgeriesService),
        update: this.surgeriesService.updateSurgeryById.bind(this.surgeriesService),
    };
    // Case-specific data observables
    public radiotherapyService: DataService = {
        get: this.radiotherapiesService.getRadiotherapies.bind(this.radiotherapiesService),
        create: this.radiotherapiesService.createRadiotherapy.bind(this.radiotherapiesService),
        delete: this.radiotherapiesService.deleteRadiotherapyById.bind(this.radiotherapiesService),
        update: this.radiotherapiesService.updateRadiotherapy.bind(this.radiotherapiesService),
    };
    // Case-specific data observables
    public lifestyleService: DataService = {
        get: this.lifestylesService.getLifestyles.bind(this.lifestylesService),
        create: this.lifestylesService.createLifestyle.bind(this.lifestylesService),
        delete: this.lifestylesService.deleteLifestyleById.bind(this.lifestylesService),
        update: this.lifestylesService.updateLifestyleById.bind(this.lifestylesService),
    };
    // Case-specific data observables
    public genomicVariantService: DataService = {
        get: this.genomicVariantsService.getGenomicVariants.bind(this.genomicVariantsService),
        create: this.genomicVariantsService.createGenomicVariant.bind(this.genomicVariantsService),
        delete: this.genomicVariantsService.deleteGenomicVariant.bind(this.genomicVariantsService),
        update: this.genomicVariantsService.updateGenomicVariant.bind(this.genomicVariantsService),
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
    public RadiotherapyFormComponent = RadiotherapyFormComponent;
    public GenomicVariantFormComponent = GenomicVariantFormComponent;

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
        comorbidities: DiamondPlus,
        vitals: Activity,
        tumorBoards: Presentation,
        adverseEvents: ShieldAlert,
        treatmentResponses: Image, 
        performanceStatus: CircleGauge,
    }

    ngOnInit() {
        this.caseServiceSubscription = this.caseService.getPatientCaseByPseudoidentifier(this.pseudoidentifier).subscribe({
            next: (data) => {
                this.case = data;
                // Get internal case ID used for API requests
                this.caseId = this.case.id;
                // Get data observables for this specific case 
            },
            error: (error) => {
                // Report any problems
                this.messageService.add({ severity: 'error', summary: 'Error loading case', detail: error.message });
            }
        })
    }

    ngOnDestroy() {
        this.caseServiceSubscription.unsubscribe()
    }


}