import { CommonModule, Location } from '@angular/common';
import { NgModule, Component, Input, ViewEncapsulation, OnInit, inject, DestroyRef,ChangeDetectionStrategy } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, FormGroup, FormsModule, Validators } from '@angular/forms';

import { Panel } from 'primeng/panel';
import { Button } from 'primeng/button';
import { Card } from 'primeng/card';
import { MessageService } from 'primeng/api';
import { InputText } from 'primeng/inputtext';
import { Avatar } from 'primeng/avatar';
import { DataView } from 'primeng/dataview';
import { Chip } from 'primeng/chip';
import { TabsModule } from 'primeng/tabs';
import { Divider } from 'primeng/divider';

// Icons
import { Users, CalendarClock, ClipboardCheck } from 'lucide-angular';
import { LucideAngularModule } from 'lucide-angular';

import { CohortsService, Cohort, PatientCase, CohortCreate, CohortStatisticsSchema, ModifiedResource } from 'src/app/shared/openapi';

import { CohortQueryBuilderComponent } from '../cohort-query-builder/cohort-query-builder.component';
import { first, map } from 'rxjs';

import { CaseBrowserCardComponent } from '../case-search/components/case-card/case-search-item.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { DatasetComposerComponent } from 'src/app/features/dataset-composer/dataset-composer.component';


@Component({
    standalone: true,
    selector: 'pop-cohort-builder',
    templateUrl: './cohort-builder.component.html',
    styleUrl: './cohort-builder.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        LucideAngularModule,
        CohortQueryBuilderComponent,
        CaseBrowserCardComponent,
        DatasetComposerComponent,
        Panel,
        Card,
        InputText,
        UserBadgeComponent,
        Divider,
        TabsModule,
        Avatar,
        DataView,
        Button,
        Chip,
    ]
})
export class CohortBuilderComponent {

    @Input() cohortId!: string;

    private readonly cohortsService = inject(CohortsService);
    private readonly messageService = inject(MessageService);
    public readonly formBuilder = inject(FormBuilder);
    public readonly location = inject(Location);
    public readonly authService = inject(AuthService)


    public cohortControl!: FormGroup;
    public cohortCases: PatientCase[] = [];
    public cohort!: Cohort; 
    public loading: boolean = false;
    public initloading: boolean = true;
    public editCohortName: boolean = false;
    public cohortStatistics!: CohortStatisticsSchema;
    public currentOffset: number = 0
    public pageSize: number = 15

    public readonly populationIcon = Users;
    public readonly ageIcon = CalendarClock;
    public readonly completionIcon = ClipboardCheck;


    ngOnInit() {
        this.refreshCohortData()
        this.refreshCohortCases()
        this.refreshCohortStatistics()
    }    
    

    refreshCohortData() {
        this.cohortsService.getCohortById({cohortId: this.cohortId}).pipe(first()).subscribe({
            next: (cohort: Cohort) => {
                this.cohort = cohort
                if (!this.cohortControl){
                    this.cohortControl = this.formBuilder.group({
                        name: [cohort.name,Validators.required],
                        isPublic: [cohort.isPublic,Validators.required],
                        includeCriteria: [cohort.includeCriteria],
                        excludeCriteria: [cohort.excludeCriteria],
                    });    
                    this.initloading = false    
                }
            },
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort information', detail: error.message })
        })
    }

    refreshCohortStatistics() {
        this.cohortsService.getCohortStatistics({cohortId: this.cohortId}).pipe(
            map((stats: CohortStatisticsSchema)  => {
                    this.cohortStatistics = stats;
            }),
            first()
        ).subscribe({
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort statistics', detail: error.message })
        })
    }

    refreshCohortCases() {
        this.cohortsService.getCohortCases({cohortId: this.cohortId, offset: this.currentOffset, limit: this.pageSize}).pipe(
            map(
                cases => {
                    this.cohortCases = cases.items;
                }
            ),
            first()
        ).subscribe({
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort cases', detail: error.message })
        })
    }

    submitCohort() {
        this.editCohortName = false;
        this.loading = true;
        const cohortData = this.cohortControl.value;
        const payload: CohortCreate = {
            name: cohortData.name,
            isPublic: cohortData.isPublic,
            includeCriteria: cohortData.includeCriteria,
            excludeCriteria: cohortData.excludeCriteria,
        };
        this.cohortsService.updateCohort({cohortId: this.cohortId, cohortCreate: payload}).pipe(first()).subscribe({
            next: (response: ModifiedResource) => {
                this.refreshCohortData()
                this.refreshCohortCases()
                this.refreshCohortStatistics()
                this.loading = false;
                this.messageService.add({ severity: 'success', summary: 'Success', detail: `Updated "${response.description}"` });
            },
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error saving the cohort', detail: error.message })
        });
    }

    setPaginationAndRefresh(event: any) {
        this.currentOffset = event.first;
        this.pageSize = event.rows;
        this.refreshCohortCases()
     }
     

}
