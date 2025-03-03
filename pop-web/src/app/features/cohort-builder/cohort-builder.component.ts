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

import { CohortsService, Cohort, PatientCase, CohortCreate, CohortStatisticsSchema, ModifiedResource, CohortContribution } from 'src/app/shared/openapi';

import { CohortQueryBuilderComponent } from '../cohort-query-builder/cohort-query-builder.component';
import { first, map } from 'rxjs';

import { CaseBrowserCardComponent } from '../case-search/components/case-card/case-search-item.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { DatasetComposerComponent } from 'src/app/features/dataset-composer/dataset-composer.component';
import { CohortContributorsComponent } from './components/cohort-constributors/cohort-contributors.components';
import { CohortGraphsComponent } from './components/cohort-graphs/cohort-graphs.component';
import { Skeleton } from 'primeng/skeleton';


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
        CohortGraphsComponent,
        CohortContributorsComponent,
        CohortQueryBuilderComponent,
        CaseBrowserCardComponent,
        DatasetComposerComponent,
        Panel,
        Card,
        Skeleton,
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


    public cohortControl: FormGroup = this.formBuilder.group({
        name: [null,Validators.required],
        isPublic: [null,Validators.required],
        includeCriteria: [null],
        excludeCriteria: [null],
    });  
    public cohortCases: PatientCase[] = [];
    public cohort!: Cohort; 
    public loading: boolean = false;
    public editCohortName: boolean = false;
    public cohortContributions!: CohortContribution[];
    public cohortStatistics!: CohortStatisticsSchema;
    public currentOffset: number = 0
    public pageSize: number = 15

    public readonly populationIcon = Users;
    public readonly ageIcon = CalendarClock;
    public readonly completionIcon = ClipboardCheck;


    ngAfterViewInit() {
        this.refreshCohortData()
        this.refreshCohortCases()
        this.refreshCohortStatistics()
        this.refreshCohortContributions()
    }    
    

    refreshCohortData() {
        this.cohortsService.getCohortById({cohortId: this.cohortId}).pipe(first()).subscribe({
            next: (cohort: Cohort) => {
                this.cohort = cohort;
                if (!this.cohortControl.value.includeCriteria && !this.cohortControl.value.includeCriteria) {
                    this.cohortControl.controls['name'].setValue(cohort.name) ;
                    this.cohortControl.controls['isPublic'].setValue(cohort.isPublic);
                    this.cohortControl.controls['includeCriteria'].setValue(cohort.includeCriteria);
                    this.cohortControl.controls['excludeCriteria'].setValue(cohort.excludeCriteria);    
                }
            },
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort information', detail: error.message })
        })
    }

    refreshCohortContributions() {
        this.cohortsService.getCohortContributors({cohortId: this.cohortId}).pipe(
            map((contributions: CohortContribution[])  => {
                    this.cohortContributions = contributions;
            }),
            first()
        ).subscribe({
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort contributors', detail: error.message })
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
                this.refreshCohortContributions()
                this.messageService.add({ severity: 'success', summary: 'Success', detail: `Updated "${response.description}"` });
            },
            error: (error: Error) => this.messageService.add({ severity: 'error', summary: 'Error saving the cohort', detail: error.message }),
            complete: () => this.loading = false
        });
    }

    setPaginationAndRefresh(event: any) {
        this.currentOffset = event.first;
        this.pageSize = event.rows;
        this.refreshCohortCases()
     }
     

}
