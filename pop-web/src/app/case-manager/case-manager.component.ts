import { Component, OnInit, Input, ViewEncapsulation, inject  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, Subscription } from 'rxjs'; 

import { MessageService } from 'primeng/api';
import { AvatarModule } from 'primeng/avatar';

import { NgxJdenticonModule, JDENTICON_CONFIG } from "ngx-jdenticon";

import { 
    PatientCase, 
    PatientCasesService,
    NeoplasticEntitiesService,
    StagingsService,
    TumorMarkersService,
} from '../core/modules/openapi'

import { 
    NeoplasticEntityFormComponent,
    StagingFormComponent,
    TumorMarkerFormComponent,
} from '../core/forms';

import { ModalFormComponent } from '../core/components/modal-form/modal-form.component'
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
    providers: [
        { 
            // Custom identicon style
            provide: JDENTICON_CONFIG,
            useValue: {
                hues: [220, 230],
            lightness: {
                color: [0.21, 0.9],
                grayscale: [0.23, 0.62],
            },
            saturation: {
                color: 0.80,
                grayscale: 0.50,
            },
            },
        }
    ],
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
    private messageService: MessageService = inject(MessageService) ;

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


    // Form components
    public NeoplasticEntityFormComponent = NeoplasticEntityFormComponent;
    public StagingFormComponent = StagingFormComponent;
    public TumorMarkerFormComponent = TumorMarkerFormComponent;


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