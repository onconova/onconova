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
import { Users, CalendarClock, ClipboardCheck, Activity, VenusAndMars, Locate } from 'lucide-angular';
import { LucideAngularModule } from 'lucide-angular';

import { CohortsService, Cohort, PatientCase, CohortCreate, ModifiedResource, CohortContribution, CohortTraitMedian, CohortTraitCounts, HistoryEvent } from 'src/app/shared/openapi';

import { CohortQueryBuilderComponent } from './components/cohort-query-builder/cohort-query-builder.component';
import { catchError, first, map, Observable, of, throwError } from 'rxjs';

import { CaseBrowserCardComponent } from '../../cases/case-search/components/case-search-item/case-search-item.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { DatasetComposerComponent } from 'src/app/features/cohorts/cohort-manager/components/dataset-composer/dataset-composer.component';
import { CohortContributorsComponent } from './components/cohort-contributors.component';
import { CohortGraphsComponent } from './components/cohort-graphs/cohort-graphs.component';
import { Skeleton } from 'primeng/skeleton';
import { Message } from 'primeng/message';
import { CohortTraitPanel } from './components/cohort-trait-panel.component';
import { Timeline, TimelineModule } from 'primeng/timeline';
import { Card } from 'primeng/card';
import { Fieldset } from 'primeng/fieldset';


@Component({
    selector: 'pop-cohort-manager',
    templateUrl: './cohort-manager.component.html',
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
        Fieldset,
        Message,
        Skeleton,
        InputText,
        UserBadgeComponent,
        TimelineModule,
        Divider,
        TabsModule,
        DataView,
        Button,
        Card,
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
    public cohort$!: Observable<Cohort>; 
    public loading: boolean = false;
    public userCanEdit: boolean = false;
    public editCohortName: boolean = false;
    public cohortHistory$!: Observable<HistoryEvent[]>
    public cohortAgeStats$: Observable<CohortTraitMedian | null> = of(null)
    public cohortTopographyStats$: Observable<CohortTraitCounts | null> = of(null)
    public cohortGenderStats$: Observable<CohortTraitCounts | null> = of(null)
    public cohortOverallSurvivalStats$: Observable<CohortTraitMedian | null> = of(null)
    public cohortDataCompletionStats$: Observable<CohortTraitMedian | null> = of(null)
    public currentOffset: number = 0
    public pageSize: number = 15
    
    public readonly populationIcon = Users;
    public readonly genderIcon = VenusAndMars;
    public readonly survivalIcon = Activity;
    public readonly ageIcon = CalendarClock;
    public readonly siteIcon = Locate;
    public readonly completionIcon = ClipboardCheck;
    
    
    
    ngAfterViewInit() {
        this.refreshCohortData()
        this.refreshCohortCases()
        this.refreshCohortStatistics()
    }    
    
    
    refreshCohortData() {
        this.cohort$ = this.cohortsService.getCohortById({cohortId: this.cohortId}).pipe(
            first(), 
            catchError(
                (error: any, caught: any) => {
                    this.messageService.add({ severity: 'error', summary: 'Error retrieving the cohort information', detail: error.error.detail})
                    return throwError(() => new Error(error));
                }
            ),
            map(
            (cohort: Cohort) => {
                this.userCanEdit = (cohort.isPublic || (!cohort.isPublic && cohort.createdBy == this.authService.user.username)) && this.authService.user.canManageCohorts 
                if (!this.cohortControl.value.includeCriteria && !this.cohortControl.value.includeCriteria) {
                    this.cohortControl.controls['name'].setValue(cohort.name) ;
                    this.cohortControl.controls['isPublic'].setValue(cohort.isPublic);
                    this.cohortControl.controls['includeCriteria'].setValue(cohort.includeCriteria);
                    this.cohortControl.controls['excludeCriteria'].setValue(cohort.excludeCriteria);    
                    this.cohortControl.updateValueAndValidity();
                }
                this.loading = false;
                return cohort
            })
        )
        this.cohortHistory$ = this.cohortsService.getAllCohortHistoryEvents({cohortId: this.cohortId}).pipe(map(response=>response.items))
    }
    
    revertCohortDefinition(old: Cohort, timestamp: string) {
        try {
            this.cohortControl.controls['name'].setValue(old.name);
            this.cohortControl.controls['isPublic'].setValue(old.isPublic);
            this.cohortControl.controls['includeCriteria'].setValue(old.includeCriteria);
            this.cohortControl.controls['excludeCriteria'].setValue(old.excludeCriteria);    
            this.messageService.add({ severity: 'success', summary: 'Changes applied', detail: 'Applied previous cohort defintion snapshot changes from ' + timestamp })
        } catch (error) {
            this.messageService.add({ severity: 'error', summary: 'Error reverting cohort definition', detail: 'Cohort definition might be invalid due to updates and/or recent changes.' })
        }
        this.cohortControl.updateValueAndValidity();
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
        this.cohortTopographyStats$ = this.cohortsService.getCohortTraitCounts({cohortId: this.cohortId, trait: 'neoplasticEntities.topographyGroup.display'}).pipe(
            map(
                (response: CohortTraitCounts[]) => response.sort((a,b) => b.counts - a.counts)[0] 
            ),
            catchError(errorHandler),
        )
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
            includeCriteria: cohortData.includeCriteria,
            excludeCriteria: cohortData.excludeCriteria,
        };
        this.cohortsService.updateCohort({cohortId: this.cohortId, cohortCreate: payload}).pipe(first()).subscribe({
            next: (response: ModifiedResource) => {
                this.refreshCohortData()
                this.refreshCohortCases()
                this.refreshCohortStatistics()
                this.messageService.add({ severity: 'success', summary: 'Success', detail: `Updated "${response.description}"` });
            },
            error: (error: any) => this.messageService.add({ severity: 'error', summary: 'Error saving the cohort', detail: error.error.detail }),
        });
    }
    
    setPaginationAndRefresh(event: any) {
        this.currentOffset = event.first;
        this.pageSize = event.rows;
        this.refreshCohortCases()
    }
    
    
    //  describeChanges(oldObj: any, newObj: any): string {
    //     const changes = this.getChanges(oldObj, newObj);
    //     const changeDescription = changes.map(change => {
    //       if (change.type === 'added') {
    //         return `Added property '${change.key}' with value ${this.formatValue(change.value)}`;
    //       } else if (change.type === 'removed') {
    //         return `Removed property ${change.key}=${this.formatValue(change.oldValue)}`;
    //       } else if (change.type === 'updated') {
    //         return `Updated property '${change.key}' from ${this.formatValue(change.oldValue)} to ${this.formatValue(change.value)}`;
    //       } return ''
    //     }).join('\n');
    //     return changeDescription;
    //   }
    
    public getAllChanges(differential: any): any[] {
        return Object.entries(differential).flatMap(([key, value]) => {
            const oldObj =  (value as any[])[0]
            const newObj =  (value as any[])[1]
            if (oldObj && newObj) {
                return this.getChanges(key,oldObj,newObj)                
            } else {
                return []
            }
        });
    }
    
    private formatValue(value: any): string {
        if (typeof value === 'object') {
            return JSON.stringify(value, null, 2);
        } else {
            return `'${value}'`;
        }
    }
    
    private getChanges(field: string, oldObj: any, newObj: any, path = ''): any[] {
        const changes: any[] = [];
        if (typeof newObj === 'object') {
            Object.keys(oldObj).forEach(key => {
                const newPath = path ? `${path}.${key}` : key;
                if (typeof oldObj[key] === 'object' && typeof newObj[key] === 'object') {
                    const nestedChanges = this.getChanges(
                        field, 
                        typeof oldObj[key] === 'object' ? oldObj[key] : oldObj, 
                        typeof newObj[key] === 'object' ? newObj[key] : oldObj, 
                        newPath
                    );
                    changes.push(...nestedChanges);
                } else if (!(key in newObj)) {
                    changes.push({ field: field, type: 'removed', key: newPath, oldValue: oldObj[key] });
                }  else if (oldObj[key] !== newObj[key]) {
                    changes.push({ field: field, type: 'updated', key: newPath, oldValue: oldObj[key], value: newObj[key] });
                }
                
            })
        } else if (oldObj !== newObj) {
            changes.push({ field: field, type: 'updated', key: '', oldValue: oldObj, value: newObj });
        };
        if (typeof oldObj === 'object') {
            Object.keys(newObj).forEach(key => {
                const newPath = path ? `${path}.${key}` : key;
                if (!(key in oldObj)) {
                    changes.push({ field: field, type: 'added', key: newPath, value: newObj[key] });
                }
            }
        )};
        return changes;
    }
    
    
}
