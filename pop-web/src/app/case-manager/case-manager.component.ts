import { Component, OnInit, Input, ViewEncapsulation, inject  } from '@angular/core';
import { Observable, of } from 'rxjs'; 

import { MessageService } from 'primeng/api';

import { PatientCase, PatientCasesService } from '../core/modules/openapi';
import { NeoplasticEntitiesService, PaginatedNeoplasticEntity } from '../core/modules/openapi'

import { NeoplasticEntityFormComponent } from '../core/forms/neoplastic-entity-form/neoplastic-entity-form.component';



@Component({
    templateUrl: './case-manager.component.html',
    styleUrl: './case-manager.component.css',
    encapsulation: ViewEncapsulation.None
})
export class CaseManagerComponent implements OnInit {

    @Input() pseudoidentifier: string = '';
    public case!: PatientCase;

    public neoplasticEntities$!: Observable<PaginatedNeoplasticEntity> 

    public NeoplasticEntityFormComponent = NeoplasticEntityFormComponent

    private caseService = inject(PatientCasesService);
    private neoplasticEntitiesService = inject(NeoplasticEntitiesService)
    private messageService = inject(MessageService) 



    ngOnInit() {

        this.caseService.getPatientCaseByPseudoidentifier(this.pseudoidentifier).subscribe(
            (response) => {
                this.case = response;
                this.neoplasticEntities$ = this.neoplasticEntitiesService.getNeoplasticEntities(this.case.id)
            },
            (error) => {
                // Report any problems
                this.messageService.add({ severity: 'error', summary: 'Error loadin case', detail: error.message });
            }
        )
    }


}