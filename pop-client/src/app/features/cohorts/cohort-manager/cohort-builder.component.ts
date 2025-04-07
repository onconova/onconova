import { CommonModule, Location } from '@angular/common';
import { NgModule, Component, Input, ViewEncapsulation, OnInit, inject, DestroyRef,ChangeDetectionStrategy } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, FormGroup, FormsModule, Validators } from '@angular/forms';

import { Panel } from 'primeng/panel';
import { Button } from 'primeng/button';
import { MessageService } from 'primeng/api';
import { InputText } from 'primeng/inputtext';
import { DataView } from 'primeng/dataview';
import { Chip } from 'primeng/chip';
import { TabsModule } from 'primeng/tabs';
import { Divider } from 'primeng/divider';

// Icons
import { Users, CalendarClock, ClipboardCheck, Activity, VenusAndMars } from 'lucide-angular';
import { LucideAngularModule } from 'lucide-angular';

import { CohortsService, Cohort, PatientCase, CohortCreate, ModifiedResource, CohortContribution, CohortTraitMedian, CohortTraitCounts } from 'src/app/shared/openapi';

import { CohortQueryBuilderComponent } from '../cohort-query-builder/cohort-query-builder.component';
import { catchError, first, map, Observable, of } from 'rxjs';

import { CaseBrowserCardComponent } from '../../cases/case-search/components/case-card/case-search-item.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { DatasetComposerComponent } from 'src/app/features/cohorts/cohort-manager/components/dataset-composer/dataset-composer.component';
import { CohortContributorsComponent } from './components/cohort-constributors/cohort-contributors.component';
import { CohortGraphsComponent } from './components/cohort-graphs/cohort-graphs.component';
import { Skeleton } from 'primeng/skeleton';
import { Message } from 'primeng/message';
import { CohortTraitPanel } from './components/cohort-trait-panel/cohort-trait-panel.component';


@Component({
    standalone: true,
    selector: 'pop-cohort-builder',
    templateUrl: './cohort-builder.component.html',
    styleUrl: './cohort-builder.component.css',
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush,
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
        CohortTraitPanel,
        Panel,
        Message,
        Skeleton,
        InputText,
        UserBadgeComponent,
        Divider,
        TabsModule,
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
    public cohortAgeStats$: Observable<CohortTraitMedian | null> = of(null)
    public cohortGenderStats$: Observable<CohortTraitCounts | null> = of(null)
    public cohortOverallSurvivalStats$: Observable<CohortTraitMedian | null> = of(null)
    public cohortDataCompletionStats$: Observable<CohortTraitMedian | null> = of(null)
    public currentOffset: number = 0
    public pageSize: number = 15

    public readonly populationIcon = Users;
    public readonly genderIcon = VenusAndMars;
    public readonly survivalIcon = Activity;
    public readonly ageIcon = CalendarClock;
    public readonly completionIcon = ClipboardCheck;


    ngAfterViewInit() {
        this.refreshCohortData()
        this.refreshCohortCases()
        this.refreshCohortStatistics()
    }    
    

    refreshCohortData() {
        this.cohortsService.getCohortById({cohortId: this.cohortId}).pipe(first()).subscribe({
            next: (cohort: Cohort) => {
                this.cohort = cohort;
                if (!this.cohortControl.value.includeCriteria && !this.cohortControl.value.includeCriteria) {
                    this.cohortControl.controls['name'].setValue(cohort.name) ;
                    this.cohortControl.controls['isPublic'].setValue(cohort.isPublic);
                    this.cohortControl.controls['includeCriteria'].setValue(this.convertFromAPI(cohort.includeCriteria));
                    this.cohortControl.controls['excludeCriteria'].setValue(this.convertFromAPI(cohort.excludeCriteria));    
                }
            },
            error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort information', detail: error.error.detail })
        })
    }

    refreshCohortStatistics() {
        const errorHandler = (error: any) => {
            if (error.status == 422) {
                return of(null)
            } else {
                this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort statistics', detail: error.error.detail })
                console.error(error)
                return of(null)
            }
        }
        this.cohortAgeStats$ = this.cohortsService.getCohortTraitMedian({cohortId: this.cohortId, trait: 'age'}).pipe(catchError(errorHandler))
        this.cohortGenderStats$ = this.cohortsService.getCohortTraitCounts({cohortId: this.cohortId, trait: 'gender.display'}).pipe(
            map(
            (response: CohortTraitCounts[]) => response.sort((a,b) => b.counts - a.counts)[0] 
            ),
            catchError(errorHandler),
        )
        this.cohortOverallSurvivalStats$ = this.cohortsService.getCohortTraitMedian({cohortId: this.cohortId, trait: 'overallSurvival'}).pipe(catchError(errorHandler))
        this.cohortDataCompletionStats$ = this.cohortsService.getCohortTraitMedian({cohortId: this.cohortId, trait: 'dataCompletionRate'}).pipe(catchError(errorHandler))
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
            error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort cases', detail: error.error.detail })
        })
    }

    submitCohort() {
        this.editCohortName = false;
        this.loading = true;
        const cohortData = this.cohortControl.value;
        const payload: CohortCreate = {
            name: cohortData.name,
            isPublic: cohortData.isPublic,
            includeCriteria: this.convertToAPI(cohortData.includeCriteria),
            excludeCriteria: this.convertToAPI(cohortData.excludeCriteria),
        };
        this.cohortsService.updateCohort({cohortId: this.cohortId, cohortCreate: payload}).pipe(first()).subscribe({
            next: (response: ModifiedResource) => {
                this.refreshCohortData()
                this.refreshCohortCases()
                this.refreshCohortStatistics()
                this.messageService.add({ severity: 'success', summary: 'Success', detail: `Updated "${response.description}"` });
            },
            error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error saving the cohort', detail: error.error.detail }),
            complete: () => this.loading = false
        });
    }

    setPaginationAndRefresh(event: any) {
        this.currentOffset = event.first;
        this.pageSize = event.rows;
        this.refreshCohortCases()
     }
     

    private convertFromAPI(ruleset_: any) {  
        if (!ruleset_) {
            return ruleset_
        }
        let ruleset = {...ruleset_};
        if (ruleset.rules && ruleset.rules.length > 0) {
            ruleset.rules = this.convertRule(ruleset.rules, true) 
        }
        return ruleset
    }  

    private convertToAPI(ruleset_: any) {  
        if (!ruleset_) {
            return ruleset_
        }
        let ruleset = {...ruleset_};
        if (ruleset.rules && ruleset.rules.length > 0) {
            ruleset.rules = this.convertRule(ruleset.rules, false) 
        }
        return ruleset
    }  

    private convertRule(rules: any, toInternal: boolean = true) {
        if (!rules || rules.length === 0) {
            return null
        }
        return rules.map((rule_: any) => {
            let rule = {...rule_};
            if (rule.filters && rule.filters.length > 0) {
                rule.filters = rule.filters.map((filter_: any) => {
                    let filter = {...filter_}
                    if (filter.field) {
                        if (toInternal) {
                            filter.field = `${rule.entity}.${filter.field}`
                        } else {
                            filter.field = filter.field.split('.').pop();
                        }
                    }
                    return filter
                })
            }
            // Recursively apply to nested rules
            if (rule.rules && rule.rules.length > 0) {
                rule.rules = this.convertRule(rule.rules, toInternal);
            }
            return rule
        });
      }


}
