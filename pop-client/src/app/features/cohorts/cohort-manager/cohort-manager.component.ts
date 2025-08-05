import { CommonModule, Location } from '@angular/common';
import { Component, inject, computed, input, effect, signal, Signal } from '@angular/core';
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

import { CohortsService, Cohort, CohortCreate, ProjectsService, AccessRoles, CohortTraitCounts, PatientCaseConsentStatusChoices } from 'pop-api-client';

import { CohortQueryBuilderComponent } from './components/cohort-query-builder/cohort-query-builder.component';
import { catchError, map, of, throwError } from 'rxjs';

import { CaseSearchItemCardComponent } from '../../cases/case-search/components/case-search-item/case-search-item.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { DatasetComposerComponent } from 'src/app/features/cohorts/cohort-manager/components/dataset-composer/dataset-composer.component';
import { CohortContributorsComponent } from './components/cohort-contributors.component';
import { CohortGraphsComponent } from './components/cohort-graphs/cohort-graphs.component';
import { Skeleton } from 'primeng/skeleton';
import { Message } from 'primeng/message';
import { CohortTraitPanel } from './components/cohort-trait-panel.component';
import { TimelineModule } from 'primeng/timeline';
import { Card } from 'primeng/card';
import { Fieldset } from 'primeng/fieldset';
import { rxResource } from '@angular/core/rxjs-interop';
import { driver } from 'driver.js';
import TourDriverConfig from './cohort-manager.tour';
import { ToolbarModule } from 'primeng/toolbar';
import { Select, SelectModule } from 'primeng/select';
import { SelectButton } from 'primeng/selectbutton';
import { TableModule } from 'primeng/table';
import { Paginator } from 'primeng/paginator';


@Component({
    selector: 'pop-cohort-manager',
    templateUrl: './cohort-manager.component.html',
    imports: [
        CommonModule,
        FormsModule,
        Paginator,
        ReactiveFormsModule,
        LucideAngularModule,
        CohortGraphsComponent,
        CohortContributorsComponent,
        CohortQueryBuilderComponent,
        CaseSearchItemCardComponent,
        DatasetComposerComponent,
        CohortTraitPanel,
        Panel,
        Fieldset,
        Message,
        Skeleton,
        InputText,
        UserBadgeComponent,
        SelectModule,
        SelectButton,
        TableModule,
        TimelineModule,
        Divider,
        ToolbarModule,
        TabsModule,
        DataView,
        Button,
        Card,
        Chip,
    ]
})
export class CohortBuilderComponent {
    
    public cohortId = input.required<string>()   
    
    readonly #cohortsService = inject(CohortsService);
    readonly #projectsService = inject(ProjectsService);
    readonly #messageService = inject(MessageService);
    readonly #fb = inject(FormBuilder);
    readonly #location = inject(Location);
    readonly #authService = inject(AuthService)
    
    
    public cohortControl: FormGroup = this.#fb.group({
        name: this.#fb.nonNullable.control<string>('', Validators.required),
        project: this.#fb.control<string | null>(''),
        includeCriteria: this.#fb.control<object | null>(null),
        excludeCriteria: this.#fb.control<object | null>(null),
    });  

    public icons = {
        age: CalendarClock,
        gender: VenusAndMars,
        site: Locate,
        survival: Activity,
        population: Users,
        completion: ClipboardCheck
    };
    private readonly tour = TourDriverConfig
    private submittingCohort = signal(false)
    public loading = computed(() => this.cohort.isLoading() || this.submittingCohort())
    public editCohortName: boolean = false;
    public pagination = signal({limit: 15, offset: 0});
    public goBack = () => this.#location.back()
    public user = computed(() => this.#authService.user())

    public cohort = rxResource({
        request: () => ({cohortId: this.cohortId()}),
        loader: ({request}) => this.#cohortsService.getCohortById(request).pipe(
            catchError(
                (error: any, caught: any) => {
                    this.#messageService.add({ severity: 'error', summary: 'Error retrieving the cohort information', detail: error.error.detail})
                    return throwError(() => new Error(error));
                }
            ),
        )
    })

    public project = rxResource({
        request: () => ({projectId: this.cohort.value()?.projectId as string}),
        loader: ({request}) => request.projectId ? this.#projectsService.getProjectById(request) : of(null)
    })

    public cohortPopulation = computed<number | undefined>(()=> this.cohort.value()?.population)
    public cohortNonEmpty = computed<boolean>(()=> this.cohortPopulation() ? (this.cohortPopulation()! > 0) : false)
    public cohortHistoryPagination = {limit: signal(10), offset: signal(0)}
    public totalHistoryEntries = signal(0)
    public cohortHistory = rxResource({
        request: () => ({cohortId: this.currentCohortId(), limit: this.cohortHistoryPagination.limit(), offset: this.cohortHistoryPagination.offset(), ordering: '-pgh_created_at'}),
        loader: ({request}) => this.#cohortsService.getAllCohortHistoryEvents(request).pipe(map(response=>{
            this.totalHistoryEntries.set(response.count)
            return response.items
        }))
    })
    public cohortTitle = computed<string | undefined>(()=> this.cohort.value()?.name)
    public currentCohortId = computed<string>(() => this.cohort.hasValue() ? this.cohort.value()!.id : this.cohortId())


    public casesLayout: Signal<'grid' | 'list'> = signal('grid');
    protected casesOrderingFields = [
        {label: 'Creation date', value: 'createdAt'},
        {label: 'Last Updated', value: 'updatedAt'},
        {label: 'Title', value: 'name'},
        {label: 'Population', value: 'population'},
    ]
    protected casesOrderingDirections = [
        {label: 'Descending', value: '-'},
        {label: 'Ascending', value: ''},
    ]
    protected casesOrderingField = signal<string>(this.casesOrderingFields[0].value)
    protected casesOrderingDirection = signal<string>(this.casesOrderingDirections[0].value)
    protected casesOrdering = computed(() => this.casesOrderingDirection() + this.casesOrderingField()) 

    public cohortCases = rxResource({
        request: () => ({
            cohortId: this.currentCohortId(), 
            limit: this.pagination().limit, 
            offset: this.pagination().offset, 
            ordering: this.casesOrdering() || '-createdAt',
        }),
        loader: ({request}) => this.#cohortsService.getCohortCases(request).pipe(map(response=>response.items))
    })    

    public readonly currentUser = computed(() => this.#authService.user());
    public userCanEdit = computed(() => 
        this.project.value()?.status == 'ongoing' && (
            (this.project.value()?.leader == this.currentUser().username || this.project.value()?.members?.includes(this.currentUser().username)) 
        )|| [AccessRoles.PlatformManager, AccessRoles.SystemAdministrator].includes(this.currentUser().role)
    )

    #setCohortDataEffect = effect( () => {
        const cohort = this.cohort.value();
        if (cohort &&!this.cohortControl.value.includeCriteria && !this.cohortControl.value.includeCriteria) {
            this.cohortControl.setValue({
                name: cohort.name,
                project: cohort.projectId,
                includeCriteria: cohort.includeCriteria,
                excludeCriteria: cohort.excludeCriteria
            })
            this.cohortControl.updateValueAndValidity();
        }
    })

    public cohortTraits = rxResource({
        request: () => this.cohortNonEmpty() ? {cohortId: this.currentCohortId()} : undefined,
        loader: ({request}: any) =>  this.#cohortsService.getCohortTraitsStatistics(request)
    }) 
    protected totalInvalidCases = computed(() => {
        const consentStatusCounts = this.cohortTraits.value()?.consentStatus;
        if (consentStatusCounts) {
            return consentStatusCounts.filter(item => [
                PatientCaseConsentStatusChoices.Revoked as string,
                PatientCaseConsentStatusChoices.Unknown as string,
            ].includes(item.category)).reduce((total: number, item: CohortTraitCounts) => total + item.counts, 0)
        } else {
            return 0
        }
    })

    
    revertCohortDefinition(old: Cohort, timestamp: string) {
        try {
            this.cohortControl.setValue({
                name: this.cohortControl.value.name,
                includeCriteria: old?.includeCriteria || null,
                excludeCriteria: old?.excludeCriteria || null,
                project: this.cohortControl.value.project,
            })
            this.#messageService.add({ severity: 'success', summary: 'Changes applied', detail: 'Applied previous cohort defintion snapshot changes from ' + timestamp })
        } catch (error) {
            console.error(error)
            this.#messageService.add({ severity: 'error', summary: 'Error reverting cohort definition', detail: 'Cohort definition might be invalid due to updates and/or recent changes.' })
        }
        this.cohortControl.updateValueAndValidity();
    }    
    
    public submitCohort() {
        this.submittingCohort.set(true);
        this.editCohortName = false;
        const cohortData = this.cohortControl.value;
        const payload: CohortCreate = {
            name: cohortData.name,
            projectId: cohortData.project,
            includeCriteria: cohortData.includeCriteria,
            excludeCriteria: cohortData.excludeCriteria,
        };
        {
        this.#cohortsService.updateCohort({cohortId: this.cohortId(), cohortCreate: payload}).subscribe({
            next: (response) => {
                this.#messageService.add({ severity: 'success', summary: 'Success', detail: `Updated "${response.description}"` });
                this.submittingCohort.set(false);
                this.cohort.reload()
                this.cohortTraits.reload()                
            },
            complete: () => {
                this.submittingCohort.set(false);
            },
            error: (error) => {
                this.#messageService.add({ severity: 'error', summary: 'Error while updating', detail: error.error.detail });
                this.submittingCohort.set(false);
                return throwError(() => new Error(error));
                
            }                
        });
        } 
    }
    
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
    
    getPredominantCount(counts: CohortTraitCounts[]) {
        return counts.sort((a,b) => b.counts - a.counts)[0]
    }
    
    startTour() {
        driver(this.tour).drive()    
    }
    
}
