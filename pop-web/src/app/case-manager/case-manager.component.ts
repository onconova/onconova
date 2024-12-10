import { Component, OnInit, Input, ViewEncapsulation, inject  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, Subscription } from 'rxjs'; 

import { MessageService } from 'primeng/api';
import { AvatarModule } from 'primeng/avatar';

import { NgxJdenticonModule, JDENTICON_CONFIG } from "ngx-jdenticon";

import { 
    PatientCase, PatientCasesService,
    NeoplasticEntitiesService, PaginatedNeoplasticEntity,
} from '../core/modules/openapi'

import { 
    NeoplasticEntityFormComponent 
} from '../core/forms';

import { ModalFormComponent } from '../core/components/modal-form/modal-form.component'
import { CaseManagerPanelComponent } from './components/case-manager-panel/case-manager-panel.component'


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
    private caseService: PatientCasesService = inject(PatientCasesService);
    private caseServiceSubscription!: Subscription
    private neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
    private messageService: MessageService = inject(MessageService) 

    // Case properties
    @Input() public pseudoidentifier: string = '';
    public case!: PatientCase;
    public caseId!: string;

    // Case-specific data observables
    public neoplasticEntities$!: Observable<PaginatedNeoplasticEntity> 

    // Form components
    public NeoplasticEntityFormComponent = NeoplasticEntityFormComponent


    ngOnInit() {
        this.caseServiceSubscription = this.caseService.getPatientCaseByPseudoidentifier(this.pseudoidentifier).subscribe({
            next: (data) => {
                this.case = data;
                // Get internal case ID used for API requests
                this.caseId = this.case.id;
                // Get data observables for this specific case 
                this.neoplasticEntities$ = this.neoplasticEntitiesService.getNeoplasticEntities(this.case.id)
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