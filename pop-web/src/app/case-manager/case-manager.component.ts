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

    // Dummy
    entries = [
        {
            date: new Date('2021/01/01'),
            description: 'Data entry 1',
        },
        {
            date: new Date('2021/02/02'),
            description: 'Data entry 2',
        },
        {
            date: new Date('2021/03/03'),
            description: 'Data entry 3',
        },
        {
            date: new Date('2021/04/04'),
            description: 'Data entry 4',
        }
    ]

    public NeoplasticEntityFormComponent = NeoplasticEntityFormComponent

    private caseService = inject(PatientCasesService);
    private neoplasticEntitiesService = inject(NeoplasticEntitiesService)
    private messageService = inject(MessageService) 



    ngOnInit() {
        this.neoplasticEntities$ = this.neoplasticEntitiesService.getNeoplasticEntities(this.case?.id)

        this.caseService.getPatientCaseByPseudoidentifier(this.pseudoidentifier).subscribe(
            (response) => {
                this.case = response;
            },
            (error) => {
                // Report any problems
                this.messageService.add({ severity: 'error', summary: 'Error loadin case', detail: error.message });
            }
        )
    }


}